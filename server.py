"""
Main MCP server for Aura services.
"""

import asyncio
import json
import os
from typing import Any, Sequence

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource, 
    Tool, 
    TextContent, 
    ImageContent, 
    EmbeddedResource
)
import mcp.types as types

from grafana_service import GrafanaService


class AuraMCPServer:
    """Main MCP server for Aura company services."""
    
    def __init__(self):
        """Initialize the Aura MCP server."""
        self.server = Server("aura-mcp-server")
        self.grafana_service = None
        self._setup_handlers()
        self._load_config()
    
    def _load_config(self):
        """Load configuration from environment variables."""
        # Grafana configuration
        grafana_url = os.getenv("GRAFANA_URL", "https://logs-prod-008.grafana.net")
        grafana_username = os.getenv("GRAFANA_USERNAME", "444103")
        grafana_password = os.getenv("GRAFANA_PASSWORD")
        
        # Initialize Grafana service
        self.grafana_service = GrafanaService(
            grafana_url=grafana_url,
            username=grafana_username,
            password=grafana_password
        )
    
    def _setup_handlers(self):
        """Setup MCP protocol handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="test_grafana_connection",
                    description="Test the connection to Grafana Loki API",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="search_grafana_logs",
                    description="Search Grafana logs for a specific correlation ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "correlation_id": {
                                "type": "string",
                                "description": "The correlation ID to search for in the logs"
                            },
                            "deployment_environment": {
                                "type": "string",
                                "description": "Optional deployment environment filter (e.g., 'test', 'production')",
                                "enum": ["test", "production"]
                            },
                            "days_back": {
                                "type": "integer",
                                "description": "Number of days to search back (default: 7)",
                                "minimum": 1,
                                "maximum": 30,
                                "default": 7
                            }
                        },
                        "required": ["correlation_id"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """Handle tool calls."""
            
            if name == "test_grafana_connection":
                return await self._handle_test_connection()
            
            elif name == "search_grafana_logs":
                correlation_id = arguments.get("correlation_id")
                if not correlation_id:
                    return [TextContent(
                        type="text",
                        text="Error: correlation_id is required"
                    )]
                
                deployment_environment = arguments.get("deployment_environment")
                days_back = arguments.get("days_back", 7)
                
                return await self._handle_search_logs(
                    correlation_id=correlation_id,
                    deployment_environment=deployment_environment,
                    days_back=days_back
                )
            
            else:
                return [TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )]
    
    async def _handle_test_connection(self) -> list[TextContent]:
        """Handle Grafana connection test."""
        try:
            is_connected = self.grafana_service.test_connection()
            
            if is_connected:
                message = "✅ Successfully connected to Grafana Loki API"
            else:
                message = "❌ Failed to connect to Grafana Loki API"
            
            return [TextContent(
                type="text",
                text=message
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Error testing connection: {str(e)}"
            )]
    
    async def _handle_search_logs(
        self, 
        correlation_id: str, 
        deployment_environment: str = None,
        days_back: int = 7
    ) -> list[TextContent]:
        """Handle Grafana log search."""
        try:
            # Perform the search
            result = self.grafana_service.search_by_correlation_id(
                correlation_id=correlation_id,
                deployment_environment=deployment_environment,
                days_back=days_back
            )
            
            if result["success"]:
                # Format the results
                total_entries = result["total_entries"]
                entries = result["entries"]
                
                if total_entries == 0:
                    message = f"🔍 No log entries found for correlation ID: {correlation_id}"
                    if deployment_environment:
                        message += f" in environment: {deployment_environment}"
                    message += f" (searched last {days_back} days)"
                else:
                    message = f"🔍 Found {total_entries} log entries for correlation ID: {correlation_id}\n"
                    if deployment_environment:
                        message += f"Environment: {deployment_environment}\n"
                    message += f"Search period: Last {days_back} days\n"
                    message += f"Query used: {result['query']}\n\n"
                    
                    # Add log entries (limit to first 10 for readability)
                    display_entries = entries[:10]
                    for i, entry in enumerate(display_entries, 1):
                        message += f"--- Entry {i} ---\n"
                        message += f"Time: {entry['timestamp_readable']}\n"
                        message += f"Message: {entry['message']}\n\n"
                    
                    if total_entries > 10:
                        message += f"... and {total_entries - 10} more entries\n"
                
                return [TextContent(
                    type="text",
                    text=message
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ Search failed: {result['error']}"
                )]
                
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Error searching logs: {str(e)}"
            )]
    
    async def run(self):
        """Run the MCP server."""
        # Import here to avoid issues with event loop
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="aura-mcp-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )


async def main():
    """Main entry point."""
    server = AuraMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main()) 