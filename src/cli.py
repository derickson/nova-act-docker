#!/usr/bin/env python3
"""Command-line interface for Nova Act script execution."""
import os
import sys
import json
import argparse
from typing import Dict, List, Optional

from runner import runner


def parse_env_vars(env_string: str) -> Dict[str, str]:
    """Parse environment variables from key=value,key2=value2 format."""
    if not env_string:
        return {}
    
    env_vars = {}
    pairs = env_string.split(',')
    
    for pair in pairs:
        if '=' not in pair:
            print(f"Warning: Invalid environment variable format: {pair}")
            continue
        
        key, value = pair.split('=', 1)
        env_vars[key.strip()] = value.strip()
    
    return env_vars


def list_scripts_command():
    """List all available scripts."""
    try:
        scripts = runner.list_scripts()
        if not scripts:
            print("No scripts found in the scripts directory.")
            return 0
        
        print("Available scripts:")
        for script in sorted(scripts):
            print(f"  - {script}")
        return 0
        
    except Exception as e:
        print(f"Error listing scripts: {e}", file=sys.stderr)
        return 1


def validate_script_command(script_name: str):
    """Validate a script's syntax."""
    try:
        result = runner.validate_script(script_name)
        
        if result.success:
            print(f"✓ Script '{script_name}' is valid")
            return 0
        else:
            print(f"✗ Script '{script_name}' has errors:")
            print(result.error, file=sys.stderr)
            return 1
            
    except Exception as e:
        print(f"Error validating script: {e}", file=sys.stderr)
        return 1


def execute_script_command(
    script_name: str,
    env_vars: Optional[Dict[str, str]] = None,
    args: Optional[List[str]] = None,
    json_output: bool = False
):
    """Execute a Nova Act script."""
    try:
        # Check for Nova Act API key
        all_env_vars = os.environ.copy()
        if env_vars:
            all_env_vars.update(env_vars)
        
        if "NOVA_ACT_API_KEY" not in all_env_vars:
            print("Error: NOVA_ACT_API_KEY environment variable is required", file=sys.stderr)
            return 1
        
        # Execute the script
        result = runner.execute_script(
            script_name=script_name,
            env_vars=env_vars,
            args=args
        )
        
        if json_output:
            # Output results as JSON
            output_data = {
                "success": result.success,
                "output": result.output,
                "error": result.error,
                "exit_code": result.exit_code,
                "script_name": script_name
            }
            print(json.dumps(output_data, indent=2))
        else:
            # Human-readable output
            if result.success:
                print(f"✓ Script '{script_name}' executed successfully")
                if result.output:
                    print("\n--- Script Output ---")
                    print(result.output)
            else:
                print(f"✗ Script '{script_name}' failed (exit code: {result.exit_code})")
                if result.error:
                    print("\n--- Error Output ---")
                    print(result.error, file=sys.stderr)
                if result.output:
                    print("\n--- Standard Output ---")
                    print(result.output)
        
        return result.exit_code
        
    except Exception as e:
        if json_output:
            error_data = {
                "success": False,
                "output": "",
                "error": str(e),
                "exit_code": 1,
                "script_name": script_name
            }
            print(json.dumps(error_data, indent=2))
        else:
            print(f"Error executing script: {e}", file=sys.stderr)
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Nova Act Script Runner CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all scripts
  %(prog)s list

  # Execute a script
  %(prog)s execute my_script

  # Execute with environment variables
  %(prog)s execute my_script --env "API_KEY=xyz,DEBUG=true"

  # Execute with script arguments
  %(prog)s execute my_script --args "--verbose --output /tmp/result"

  # Get JSON output
  %(prog)s execute my_script --json

  # Validate script syntax
  %(prog)s validate my_script
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available scripts')
    
    # Execute command
    execute_parser = subparsers.add_parser('execute', help='Execute a script')
    execute_parser.add_argument('script_name', help='Name of the script to execute')
    execute_parser.add_argument(
        '--env', 
        help='Environment variables in key=value,key2=value2 format'
    )
    execute_parser.add_argument(
        '--args',
        help='Arguments to pass to the script (space-separated)'
    )
    execute_parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate script syntax')
    validate_parser.add_argument('script_name', help='Name of the script to validate')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute commands
    if args.command == 'list':
        return list_scripts_command()
    
    elif args.command == 'validate':
        return validate_script_command(args.script_name)
    
    elif args.command == 'execute':
        env_vars = parse_env_vars(args.env) if args.env else None
        script_args = args.args.split() if args.args else None
        
        return execute_script_command(
            script_name=args.script_name,
            env_vars=env_vars,
            args=script_args,
            json_output=args.json
        )
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
