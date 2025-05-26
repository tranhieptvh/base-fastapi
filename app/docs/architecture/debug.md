# Debugging Guide for FastAPI Project

## Debug Configuration

The project is configured to support debugging in a Docker environment with the following tools:

- **debugpy**: Python debugging library
- **VS Code**: Pre-configured IDE for debugging
- **Docker**: Application runtime environment with Poetry pre-installed

## Setup

1. **Start Docker container**:
```bash
docker-compose down
docker-compose up --build
```

Note: Poetry is pre-installed in the Docker container, you don't need to install Poetry locally.

## Using the Debugger

### 1. VS Code Configuration

The `.vscode/launch.json` file is pre-configured with two debug modes:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "main:app",
                "--reload",
                "--port",
                "8000"
            ],
            "jinja": true,
            "justMyCode": true,
            "console": "integratedTerminal"
        },
        {
            "name": "Python: Docker Attach",
            "type": "python",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 5678
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}",
                    "remoteRoot": "/app"
                }
            ],
            "justMyCode": true,
            "redirectOutput": true,
            "logToFile": true,
            "showReturnValue": true,
            "console": "integratedTerminal"
        }
    ]
}
```

### 2. Debug Modes

1. **Python: FastAPI** (Local Debug Mode):
   - Runs FastAPI application directly using uvicorn
   - Uses port 8000
   - Includes hot reload functionality
   - Suitable for debugging without Docker

2. **Python: Docker Attach** (Docker Debug Mode):
   - Connects to the running Docker container
   - Uses port 5678 for debugging
   - Maps local code to container code
   - Suitable for debugging in a Docker environment
   - Recommended for this project as it matches the production environment

### 3. Debug Steps

1. **Set breakpoints**:
   - Click to the left of line numbers in VS Code
   - Breakpoints can be set in any Python file in the project

2. **Start debugging**:
   - Open Debug tab in VS Code (Ctrl+Shift+D)
   - Select "Python: Docker Attach" from the dropdown menu
   - Press F5 or click the play button to start debugging

3. **Debug shortcuts**:
   - F5: Continue execution
   - F10: Step Over (execute current line)
   - F11: Step Into (enter function)
   - Shift+F11: Step Out (exit function)
   - Shift+F5: Stop debugging

### 4. Debug Features

- **Variable inspection**: 
  - Open Debug sidebar to view variable values
  - Hover over variables to see their values
  - Use Debug Console to evaluate expressions

- **Hot Reload**:
  - Application supports hot reload
  - Code changes are automatically updated
  - Breakpoints remain active after reload

## Important Notes

1. **Debug Ports**:
   - Port 5678: Used for debugger connection
   - Port 8000: Used for the application

2. **Docker Container**:
   - Container waits for debugger connection
   - May take a few seconds to connect debugger

3. **Performance**:
   - Debug mode may slow down the application
   - Use debug mode only when necessary

## Troubleshooting

1. **Debugger connection issues**:
   - Check if port 5678 is open
   - Ensure Docker container is running
   - Try restarting VS Code

2. **Breakpoint not working**:
   - Check file mapping in launch.json
   - Ensure container code matches local code
   - Try setting breakpoint at a different location

3. **Container startup issues**:
   - Check logs: `docker-compose logs app`
   - Ensure all dependencies are installed
   - Try rebuilding container: `docker-compose up --build` 