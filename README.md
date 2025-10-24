# Nova Act Docker Runner

A dockerized environment for running AWS Nova Act scripts with Playwright, providing both REST API and CLI interfaces for script execution in isolated environments.

## Features

- **Docker-based**: Runs in Python 3.12 container with all dependencies
- **Dual Interface**: Both REST API and CLI access
- **Script Isolation**: Each script runs in a fresh environment
- **Hot Reload**: Scripts directory mounted for external development
- **Browser Security**: Chromium runs inside container, avoiding host security issues
- **Environment Variables**: Secure API key management

## Quick Start

1. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your Nova Act API key
   ```

2. **Build and start the container:**
   ```bash
   docker-compose up --build
   ```

3. **Test the REST API:**
   ```bash
   # List available scripts
   curl http://localhost:8000/scripts

   # Execute a script
   curl -X POST http://localhost:8000/execute/example_script \
     -H "Content-Type: application/json" \
     -d '{}'
   ```

4. **Use the CLI interface:**
   ```bash
   # List scripts
   docker-compose run --rm nova-act-cli python src/cli.py list

   # Execute a script
   docker-compose run --rm nova-act-cli python src/cli.py execute example_script
   
   # Get JSON output
   docker-compose run --rm nova-act-cli python src/cli.py execute example_script --json
   ```

   **Note**: The CLI and REST API are independent - you don't need the server running to use CLI commands.

## API Endpoints

### REST API

- `GET /health` - Health check
- `GET /scripts` - List available scripts
- `POST /execute/{script_name}` - Execute a script
- `GET /validate/{script_name}` - Validate script syntax

**Response Format**: The `POST /execute/{script_name}` endpoint returns:
```json
{
  "success": true,
  "output": "Script output here...",
  "error": "Nova Act logs (not actual errors, just diagnostic info)",
  "exit_code": 0,
  "script_name": "example_script"
}
```

**Note**: The `error` field contains Nova Act's verbose logging output (stderr), not actual errors. It includes the AI's thinking process and session details for debugging. Check `success` and `exit_code` for actual error status.

### CLI Usage

When running inside the container, use these commands:

```bash
# List all available scripts
docker-compose run --rm nova-act-cli python src/cli.py list

# Execute a script
docker-compose run --rm nova-act-cli python src/cli.py execute <script_name>

# Execute with environment variables
docker-compose run --rm nova-act-cli python src/cli.py execute <script_name> --env "DEBUG=true,TIMEOUT=300"

# Execute with script arguments
docker-compose run --rm nova-act-cli python src/cli.py execute <script_name> --args "--verbose --output /tmp/result"

# Get JSON output
docker-compose run --rm nova-act-cli python src/cli.py execute <script_name> --json

# Validate script syntax
docker-compose run --rm nova-act-cli python src/cli.py validate <script_name>
```

**Note**: These commands work independently of the REST API server.

## Script Development

1. **Add scripts to the `scripts/` directory**
2. **Scripts must be Python files with `.py` extension**
3. **Scripts should handle the Nova Act API key from environment variables**
4. **Example script structure:**

```python
import os
from nova_act import NovaAct
from dotenv import load_dotenv

load_dotenv()

# Nova Act will automatically use NOVA_ACT_API_KEY from environment
nova = NovaAct(
    starting_page="https://example.com",
    headless=True
)

nova.start()
# Your Nova Act commands here
nova.stop()
```

## Environment Variables

Required:
- `NOVA_ACT_API_KEY` - Your Nova Act API key from https://nova.amazon.com/act

Optional:
- `NOVA_ACT_BROWSER_ARGS` - Additional browser arguments
- `HOST` - Server host (default: 0.0.0.0)  
- `PORT` - Server port (default: 8000)

## Docker Commands

```bash
# Build the container
docker-compose build

# Start the REST API server
docker-compose up

# Run a one-off CLI command
docker-compose run --rm nova-act-cli python src/cli.py list

# Execute a script via CLI
docker-compose run --rm nova-act-cli python src/cli.py execute example_script

# Stop all services
docker-compose down
```

## Integration Examples

### Python Integration

```python
import requests

# Execute a script via REST API
response = requests.post(
    "http://localhost:8000/execute/example_script",
    json={
        "env_vars": {"DEBUG": "true"},
        "args": ["--verbose"]
    }
)

result = response.json()
print(f"Success: {result['success']}")
print(f"Output: {result['output']}")
```

### Shell Integration

```bash
#!/bin/bash
# Execute script and capture result
result=$(docker-compose run --rm nova-act-cli python src/cli.py execute example_script --json)
success=$(echo "$result" | jq -r '.success')

if [ "$success" = "true" ]; then
    echo "Script executed successfully"
else
    echo "Script failed"
    echo "$result" | jq -r '.error'
fi
```

## Troubleshooting

### Common Issues

1. **API Key Missing**: Ensure `NOVA_ACT_API_KEY` is set in your `.env` file
2. **Port Already in Use**: Change the port mapping in `docker-compose.yml`
3. **Browser Issues**: The container uses `--no-sandbox` for Chrome compatibility
4. **Script Not Found**: Ensure your script is in the `scripts/` directory with `.py` extension

### Debugging

1. **Check container logs:**
   ```bash
   docker-compose logs nova-act-runner
   ```

2. **Access container shell:**
   ```bash
   docker-compose run --rm nova-act-runner bash
   ```

3. **Test script validation:**
   ```bash
   docker-compose run --rm nova-act-cli python src/cli.py validate <script_name>
   ```

## Security Considerations

- Nova Act API keys are passed via environment variables
- Container runs with restricted permissions
- Browser runs in sandboxed mode
- Scripts execute in isolated subprocess environments
