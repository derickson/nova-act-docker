"""Core script runner for executing Nova Act scripts in isolation."""
import os
import sys
import subprocess
import json
import tempfile
import importlib.util
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class ScriptResult:
    """Result of script execution."""
    success: bool
    output: str
    error: Optional[str] = None
    exit_code: int = 0


class NovaActScriptRunner:
    """Executes Nova Act scripts in isolated environments."""
    
    def __init__(self, scripts_dir: str = "/app/scripts"):
        self.scripts_dir = Path(scripts_dir)
        
    def list_scripts(self) -> List[str]:
        """List all available Python scripts in the scripts directory."""
        if not self.scripts_dir.exists():
            return []
        
        return [
            f.stem for f in self.scripts_dir.glob("*.py")
            if f.is_file() and not f.name.startswith("__")
        ]
    
    def script_exists(self, script_name: str) -> bool:
        """Check if a script exists."""
        script_path = self.scripts_dir / f"{script_name}.py"
        return script_path.exists() and script_path.is_file()
    
    def get_script_path(self, script_name: str) -> Path:
        """Get the full path to a script."""
        return self.scripts_dir / f"{script_name}.py"
    
    def execute_script(
        self, 
        script_name: str, 
        env_vars: Optional[Dict[str, str]] = None,
        args: Optional[List[str]] = None
    ) -> ScriptResult:
        """
        Execute a Nova Act script in an isolated Python subprocess.
        
        Args:
            script_name: Name of the script (without .py extension)
            env_vars: Additional environment variables to pass
            args: Command line arguments to pass to the script
            
        Returns:
            ScriptResult with execution details
        """
        if not self.script_exists(script_name):
            return ScriptResult(
                success=False,
                output="",
                error=f"Script '{script_name}' not found",
                exit_code=1
            )
        
        script_path = self.get_script_path(script_name)
        
        # Prepare environment
        exec_env = os.environ.copy()
        if env_vars:
            exec_env.update(env_vars)
        
        # Ensure Nova Act API key is present
        if "NOVA_ACT_API_KEY" not in exec_env:
            return ScriptResult(
                success=False,
                output="",
                error="NOVA_ACT_API_KEY environment variable is required",
                exit_code=1
            )
        
        # Prepare command
        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)
        
        try:
            # Execute script in subprocess for isolation
            result = subprocess.run(
                cmd,
                cwd=str(self.scripts_dir),
                env=exec_env,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return ScriptResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr if result.stderr else None,
                exit_code=result.returncode
            )
            
        except subprocess.TimeoutExpired:
            return ScriptResult(
                success=False,
                output="",
                error="Script execution timed out after 5 minutes",
                exit_code=124
            )
        except Exception as e:
            return ScriptResult(
                success=False,
                output="",
                error=f"Failed to execute script: {str(e)}",
                exit_code=1
            )
    
    def validate_script(self, script_name: str) -> ScriptResult:
        """
        Validate a script by checking its syntax without executing it.
        
        Args:
            script_name: Name of the script to validate
            
        Returns:
            ScriptResult indicating if the script is valid
        """
        if not self.script_exists(script_name):
            return ScriptResult(
                success=False,
                output="",
                error=f"Script '{script_name}' not found",
                exit_code=1
            )
        
        script_path = self.get_script_path(script_name)
        
        try:
            # Try to compile the script
            with open(script_path, 'r') as f:
                source = f.read()
            
            compile(source, str(script_path), 'exec')
            
            return ScriptResult(
                success=True,
                output=f"Script '{script_name}' syntax is valid",
                error=None,
                exit_code=0
            )
            
        except SyntaxError as e:
            return ScriptResult(
                success=False,
                output="",
                error=f"Syntax error in script: {e}",
                exit_code=1
            )
        except Exception as e:
            return ScriptResult(
                success=False,
                output="",
                error=f"Failed to validate script: {str(e)}",
                exit_code=1
            )


# Global runner instance
runner = NovaActScriptRunner()

