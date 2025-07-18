import requests
import logging
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PCAAuth")

# PCA Auth Configuration
# ────────────────────────────────────────────────────────────────────────────────
# Replace the placeholders below with your actual PCA tenant details & credentials:
PCA_BASE_URL      = "https://your-pca-tenant.analytics.accedian.io"
LOGIN_ENDPOINT    = "/api/v1/auth/login"
AGGREGATE_ENDPOINT= "/api/v3/metrics/aggregate"
USERNAME          = "your.username@example.com"  # ← Replace with your PCA username
PASSWORD          = "YourPassword!"              # ← Replace with your PCA password
# ────────────────────────────────────────────────────────────────────────────────

def get_bearer_token():
    """
    Authenticate to PCA and return the Bearer token.
    """
    login_url = f"{PCA_BASE_URL}{LOGIN_ENDPOINT}"
    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "username": USERNAME,
        "password": PASSWORD
    }

    try:
        logger.info("Attempting login to PCA API...")
        response = requests.post(login_url, headers=headers, data=payload)
        if response.status_code == 200:
            bearer = response.headers.get("authorization", "")
            if bearer.startswith("Bearer "):
                logger.info("Bearer token successfully retrieved.")
                return bearer.split("Bearer ")[1]
            else:
                logger.error("Authorization header not found in response.")
        else:
            logger.error(f"Login failed: {response.status_code} – {response.text}")
    except Exception:
        logger.exception("Exception occurred during PCA authentication.")
    return None

def fetch_aggregated_metrics(token):
    """
    Fetch aggregated metrics like latency, jitter, and loss using PCA aggregate API.
    """
    url = f"{PCA_BASE_URL}{AGGREGATE_ENDPOINT}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/vnd.api+json"
    }
    payload = {
        "data": {
            "type": "aggregates",
            "attributes": {
                "aggregation": "max",
                "granularity": "PT1H",
                "interval": "2025-07-18T09:54:51.483Z/2025-07-18T14:54:51.483Z",
                "globalMetricFilterContext": {
                    "monitoredObjectId": [
                        "27-F6694D56-D2D4-17E7-EC3C-5E50BA16E908"
                    ]
                },
                "metrics": [
                    {
                        "metric": "delayVarAvg",
                        "direction": ["0"],
                        "objectType": ["twamp-sf"]
                    },
                    {
                        "metric": "jitterAvg",
                        "direction": ["0"],
                        "objectType": ["twamp-sf"]
                    },
                    {
                        "metric": "delayVarP95",
                        "direction": ["2"],
                        "objectType": ["twamp-sf"]
                    }
                ],
                "queryContext": {
                    "ignoreCleaning": True,
                    "focusBusyHour": False,
                    "ignoreMaintenance": False
                }
            }
        }
    }

    try:
        logger.info("Fetching aggregated metrics from PCA API...")
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            logger.info("Metrics successfully retrieved.")
            print(json.dumps(response.json(), indent=2))
        else:
            logger.error(f"Failed to fetch metrics: {response.status_code} – {response.text}")
    except Exception:
        logger.exception("Exception occurred while fetching aggregated metrics.")

if __name__ == "__main__":
    token = get_bearer_token()
    if token:
        fetch_aggregated_metrics(token)
    else:
        logger.error("Exiting due to token retrieval failure.")
