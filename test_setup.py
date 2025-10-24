#!/usr/bin/env python3
"""Test script to validate the Nova Act Docker setup."""
import subprocess
import sys
import time
import requests
import json


def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n🔄 {description}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout:
                print(f"Output: {result.stdout[:500]}...")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {description} - EXCEPTION: {e}")
        return False


def test_docker_build():
    """Test Docker build process."""
    print("\n🔄 Building Docker containers")
    print("Command: docker-compose build --no-cache")
    print("⏳ This may take 5-10 minutes...")
    
    try:
        result = subprocess.run(
            ["docker-compose", "build", "--no-cache"],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout for build
        )
        
        if result.returncode == 0:
            print("✅ Building Docker containers - SUCCESS")
            return True
        else:
            print("❌ Building Docker containers - FAILED")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Building Docker containers - TIMEOUT (exceeded 10 minutes)")
        return False
    except Exception as e:
        print(f"💥 Building Docker containers - EXCEPTION: {e}")
        return False


def test_api_startup():
    """Test API server startup."""
    print("\n🔄 Starting API server...")
    
    # Start the server in background
    process = subprocess.Popen(
        ["docker-compose", "up", "-d"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for startup
    time.sleep(10)
    
    # Check if container is running
    result = subprocess.run(
        ["docker-compose", "ps"],
        capture_output=True,
        text=True
    )
    
    if "nova-act-runner" in result.stdout and "Up" in result.stdout:
        print("✅ API server started successfully")
        return True
    else:
        print("❌ API server failed to start")
        print(result.stdout)
        return False


def test_health_endpoint():
    """Test health endpoint."""
    print("\n🔄 Testing health endpoint...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check exception: {e}")
        return False


def test_scripts_endpoint():
    """Test scripts listing endpoint."""
    print("\n🔄 Testing scripts endpoint...")
    
    try:
        response = requests.get("http://localhost:8000/scripts", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Scripts endpoint passed: {data}")
            return True
        else:
            print(f"❌ Scripts endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Scripts endpoint exception: {e}")
        return False


def test_cli_list():
    """Test CLI list command."""
    return run_command(
        ["docker-compose", "run", "--rm", "nova-act-cli", "python", "src/cli.py", "list"],
        "Testing CLI list command"
    )


def test_script_validation():
    """Test script validation."""
    return run_command(
        ["docker-compose", "run", "--rm", "nova-act-cli", "python", "src/cli.py", "validate", "example_script"],
        "Testing script validation"
    )


def cleanup():
    """Clean up test environment."""
    print("\n🧹 Cleaning up...")
    subprocess.run(["docker-compose", "down"], capture_output=True)
    print("✅ Cleanup completed")


def main():
    """Run all tests."""
    print("🚀 Starting Nova Act Docker Environment Tests")
    print("=" * 50)
    
    tests = [
        ("Docker Build", test_docker_build),
        ("API Startup", test_api_startup),
        ("Health Endpoint", test_health_endpoint),
        ("Scripts Endpoint", test_scripts_endpoint),
        ("CLI List", test_cli_list),
        ("Script Validation", test_script_validation),
    ]
    
    results = {}
    
    try:
        for test_name, test_func in tests:
            results[test_name] = test_func()
            
            # Small delay between tests
            time.sleep(2)
    
    finally:
        cleanup()
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Nova Act Docker environment is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
