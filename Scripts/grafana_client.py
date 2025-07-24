import os
import requests
import base64
import time
from urllib.parse import urlencode
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Search Parameters
correlation_id = ""  # <-- SET THIS VALUE
deployment_environment = "test"  # <-- SET THIS VALUE (e.g., "test", "production", or "" to search all)

# Grafana Loki Connection Details
grafana_url = os.getenv('GRAFANA_URL', 'https://logs-prod-008.grafana.net')
username = os.getenv('GRAFANA_USERNAME', '444103')
password = os.getenv('GRAFANA_PASSWORD')

# Create header for Basic Authentication
auth_string = f"{username}:{password}"
base64_auth_string = base64.b64encode(auth_string.encode("ascii")).decode("ascii")
headers = {
    "Authorization": f"Basic {base64_auth_string}"
}

def test_connection():
    """
    Tests the connection to Grafana Loki and prints the status.
    """
    endpoint = "/loki/api/v1/labels"
    request_url = f"{grafana_url}{endpoint}"
    try:
        response = requests.get(request_url, headers=headers)
        response.raise_for_status()
        response_json = response.json()
        if response_json.get("status") == "success":
            print("Successfully connected to Grafana Loki.")
            return True
        else:
            print(f"Connection attempt returned a non-success status: {response_json.get('status')}")
            return False
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred during connection test: {http_err}")
        print(f"Response body: {response.text}")
        return False
    except Exception as err:
        print(f"An error occurred during connection test: {err}")
        return False

def search_by_correlation_id(correlation_id_to_search, environment):
    """
    Searches for logs containing the given correlation ID within the last hour,
    optionally filtering by a deployment environment.
    """
    print(f"\nSearching for Correlation ID: {correlation_id_to_search}...")
    if environment:
        print(f"Filtering by environment: {environment}")

    # Build the LogQL query dynamically
    if environment:
        # Filter by environment label, then search for the correlation ID in the line
        logql_query = f'{{deployment_environment="{environment}"}} |= "{correlation_id_to_search}"'
    else:
        # Fallback to a broad search if no environment is specified
        logql_query = f'{{job=~".+"}} |= "{correlation_id_to_search}"'

    print(f"Using LogQL query: {logql_query}")

    # Time range: last 7 days
    end_time = int(time.time() * 1_000_000_000)  # nanoseconds
    start_time = end_time - (7 * 24 * 60 * 60 * 1_000_000_000)  # 7 days ago

    # Construct the query URL
    query_endpoint = "/loki/api/v1/query_range"
    params = {
        "query": logql_query,
        "start": str(start_time),
        "end": str(end_time),
        "limit": 100, # Max number of lines to return
    }
    request_url = f"{grafana_url}{query_endpoint}?{urlencode(params)}"

    try:
        response = requests.get(request_url, headers=headers)
        response.raise_for_status()

        response_json = response.json()
        if response_json.get("status") == "success":
            result_data = response_json.get("data", {}).get("result", [])
            if not result_data:
                print("No logs found for this Correlation ID in the last hour.")
                return

            print(f"Found {len(result_data)} log stream(s).")
            for stream in result_data:
                print(f"\n--- Log Stream: {stream.get('stream')} ---")
                for value_pair in stream.get("values", []):
                    timestamp_ns, log_line = value_pair
                    # Convert nanosecond timestamp to a readable format
                    timestamp_s = int(timestamp_ns) / 1_000_000_000
                    readable_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp_s))
                    print(f"[{readable_time}] {log_line}")
        else:
            print(f"Log query failed with status: {response_json.get('status')}")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred during log search: {http_err}")
        print(f"Response body: {response.text}")
    except Exception as err:
        print(f"An error occurred during log search: {err}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Search Grafana Loki logs for a given Correlation ID. "
                    "Prioritizes command-line argument over the in-script variable."
    )
    parser.add_argument(
        "correlation_id_arg",
        nargs="?",  # Make the argument optional
        default=None,
        help="The Correlation ID to search for (optional). If not provided, the script uses the 'correlation_id' variable."
    )
    args = parser.parse_args()

    # Determine which correlation ID to use
    id_to_search = args.correlation_id_arg if args.correlation_id_arg is not None else correlation_id

    if test_connection():
        if id_to_search:
            search_by_correlation_id(id_to_search, deployment_environment)
        else:
            print("\nNo Correlation ID provided.")
            print("To search, please provide a Correlation ID as a command-line argument or set the 'correlation_id' variable in the script.")
    else:
        print("\nConnection to Grafana Loki failed. Skipping search.")
        print("To search, please check your connection and try again.") 