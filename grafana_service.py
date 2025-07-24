"""
Grafana service for searching logs via Loki API.
"""

import requests
import base64
import time
from urllib.parse import urlencode
from typing import Optional, Dict, Any, List
import json


class GrafanaService:
    """Service for interacting with Grafana Loki API."""
    
    def __init__(self, grafana_url: str, username: str, password: str):
        """
        Initialize the Grafana service.
        
        Args:
            grafana_url: The base URL for the Grafana instance
            username: Username for authentication
            password: Password/token for authentication
        """
        self.grafana_url = grafana_url
        self.username = username
        self.password = password
        
        # Create authentication header
        auth_string = f"{username}:{password}"
        base64_auth_string = base64.b64encode(auth_string.encode("ascii")).decode("ascii")
        self.headers = {
            "Authorization": f"Basic {base64_auth_string}"
        }
    
    def test_connection(self) -> bool:
        """
        Test the connection to Grafana Loki.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            endpoint = "/loki/api/v1/labels"
            request_url = f"{self.grafana_url}{endpoint}"
            
            response = requests.get(request_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("status") == "success"
            else:
                return False
                
        except Exception:
            return False
    
    def search_by_correlation_id(
        self, 
        correlation_id: str, 
        deployment_environment: Optional[str] = None,
        days_back: int = 7
    ) -> Dict[str, Any]:
        """
        Search for logs containing the given correlation ID.
        
        Args:
            correlation_id: The correlation ID to search for
            deployment_environment: Optional environment filter (e.g., "test", "production")
            days_back: Number of days to search back (default: 7)
            
        Returns:
            Dictionary containing search results and metadata
        """
        try:
            # Build the LogQL query
            if deployment_environment:
                logql_query = f'{{deployment_environment="{deployment_environment}"}} |= "{correlation_id}"'
            else:
                logql_query = f'{{job=~".+"}} |= "{correlation_id}"'
            
            # Time range: last N days
            end_time = int(time.time() * 1_000_000_000)  # nanoseconds
            start_time = end_time - (days_back * 24 * 60 * 60 * 1_000_000_000)
            
            # Construct the query URL
            query_endpoint = "/loki/api/v1/query_range"
            query_url = f"{self.grafana_url}{query_endpoint}"
            
            params = {
                "query": logql_query,
                "start": start_time,
                "end": end_time,
                "limit": 1000,
                "direction": "backward"
            }
            
            response = requests.get(query_url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "success":
                    # Process the results
                    result_data = data.get("data", {})
                    result_type = result_data.get("resultType", "")
                    results = result_data.get("result", [])
                    
                    # Extract log entries
                    log_entries = []
                    total_entries = 0
                    
                    for result in results:
                        values = result.get("values", [])
                        total_entries += len(values)
                        
                        for value in values:
                            if len(value) >= 2:
                                timestamp_ns = int(value[0])
                                log_line = value[1]
                                
                                log_entries.append({
                                    "timestamp": timestamp_ns,
                                    "timestamp_readable": time.strftime(
                                        "%Y-%m-%d %H:%M:%S UTC", 
                                        time.gmtime(timestamp_ns / 1_000_000_000)
                                    ),
                                    "message": log_line
                                })
                    
                    return {
                        "success": True,
                        "correlation_id": correlation_id,
                        "environment": deployment_environment,
                        "query": logql_query,
                        "total_entries": total_entries,
                        "entries": log_entries,
                        "search_period_days": days_back
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Grafana API returned status: {data.get('status')}",
                        "correlation_id": correlation_id
                    }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "correlation_id": correlation_id
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Exception occurred: {str(e)}",
                "correlation_id": correlation_id
            } 