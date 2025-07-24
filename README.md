# Aura MCP Server

A Model Context Protocol (MCP) server for Aura company services, providing AI assistants with access to Grafana logs and other company tools.

## Features

- **Grafana Log Search**: Search Grafana Loki logs by correlation ID
- **Environment Filtering**: Filter logs by deployment environment (test/production)
- **Connection Testing**: Verify Grafana API connectivity
- **Flexible Time Ranges**: Search logs from 1-30 days back

## Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The server uses environment variables for configuration:

```bash
# Grafana Configuration
GRAFANA_URL=https://logs-prod-008.grafana.net
GRAFANA_USERNAME=444103
GRAFANA_PASSWORD=your_grafana_api_token_here
```

## Usage

### Running the Server

```bash
python server.py
```

### Testing with MCP Inspector

```bash
npx @modelcontextprotocol/inspector python server.py
```

### Integration with Cursor

Add this configuration to your Cursor MCP settings (`.vscode/mcp.json`):

```json
{
  "inputs": [],
  "servers": {
    "aura-mcp-server": {
      "type": "stdio",
      "command": "python",
      "args": ["C:\\Source\\aura-mcp-server\\server.py"],
      "env": {
        "GRAFANA_URL": "https://logs-prod-008.grafana.net",
        "GRAFANA_USERNAME": "444103",
        "GRAFANA_PASSWORD": "your_grafana_api_token_here"
      }
    }
  }
}
```

## Available Tools

### `test_grafana_connection`