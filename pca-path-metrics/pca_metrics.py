#!/usr/bin/env python3
import configparser
import logging
import json
import requests
import sys
import ast

# ─── Load configuration from config.ini ───────────────────────────────────────
cfg = configparser.ConfigParser()
cfg.read('config.ini')

# PCA endpoint & credentials
PCA_BASE_URL   = cfg['auth']['PCA_BASE_URL']
USERNAME       = cfg['auth']['USERNAME']
PASSWORD       = cfg['auth']['PASSWORD']
LOGIN_ENDPOINT = "/api/v1/auth/login"
AGGREGATE_EP   = "/api/v3/metrics/aggregate"

# Time window settings
GRANULARITY = cfg['metrics']['granularity']  # e.g. "PT5M"
INTERVAL    = cfg['metrics']['interval']     # e.g. "2025-07-21T.../2025-07-21T..."

# ─── Parse monitored_objects list (one‑liner) ────────────────────────────────
raw = cfg['metrics'].get('monitored_objects', '').strip()
if not raw:
    print("ERROR: `monitored_objects` not defined in config.ini", file=sys.stderr)
    sys.exit(1)

try:
    monitored_list = ast.literal_eval(raw)
    if not isinstance(monitored_list, list):
        raise ValueError("Expected a list of [id, objectType] pairs")
except Exception as e:
    print(f"ERROR parsing `monitored_objects`: {e}", file=sys.stderr)
    sys.exit(1)

# ─── Configure logging (INFO + ERROR only) ────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger("PCAAuth")

# ─── Metric definitions per objectType ────────────────────────────────────────
SESSION_METRICS = [
    {"metric": "delayVarAvg", "direction": ["2"], "objectType": ["twamp-sf"]},
    {"metric": "jitterAvg",   "direction": ["2"], "objectType": ["twamp-sf"]},
]
INTERFACE_METRICS = [
    {"metric": "inputDataRate",  "direction": ["0"], "objectType": ["cisco-telemetry-xe-interface"]},
    {"metric": "outputDataRate", "direction": ["0"], "objectType": ["cisco-telemetry-xe-interface"]},
    {"metric": "txBps", "direction": ["0"], "objectType": ["cisco-telemetry-xe-interface"]},
    {"metric": "rxBps", "direction": ["0"], "objectType": ["cisco-telemetry-xe-interface"]},        
]

# ─── Combine into a config map for easy lookup ────────────────────────────────
METRIC_CONFIG = {
    "twamp-sf": {
        "metrics": SESSION_METRICS,
        "aggregation": "avg",
        "granularity": GRANULARITY,
        "queryContext": {
            "ignoreCleaning": True,
            "focusBusyHour": False,
            "ignoreMaintenance": False
        }
    },
    "cisco-telemetry-xe-interface": {
        "metrics": INTERFACE_METRICS,
        "aggregation": "avg",
        "granularity": GRANULARITY,
        "queryContext": {
            "ignoreCleaning": True,
            "focusBusyHour": False,
            "ignoreMaintenance": False
        }
    }
}

# ─── Authenticate and fetch a Bearer token ───────────────────────────────────
def get_bearer_token():
    """Logs in to PCA and returns the Bearer token."""
    url     = f"{PCA_BASE_URL}{LOGIN_ENDPOINT}"
    headers = {"Cache-Control": "no-cache", "Content-Type": "application/x-www-form-urlencoded"}
    data    = {"username": USERNAME, "password": PASSWORD}

    logger.info("Authenticating to PCA...")
    resp = requests.post(url, headers=headers, data=data, verify=False)
    resp.raise_for_status()

    auth = resp.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        logger.error("No Bearer token found in response")
        return None

    return auth.split("Bearer ")[1]

# ─── Core fetch function ─────────────────────────────────────────────────────
def fetch(token, oid, cfg):
    """
    Fetch metrics for a single monitoredObjectId.
    cfg on entry provides:
      - metrics: list of metric definitions
      - aggregation:  "avg"
      - granularity: ISO duration string
      - queryContext: dict for API queryContext
    Returns: (results_list, {metric_name: series_list})
    """
    url     = f"{PCA_BASE_URL}{AGGREGATE_EP}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/vnd.api+json"
    }

    payload = {
        "data": {
            "type": "aggregates",
            "attributes": {
                "aggregation": cfg["aggregation"],
                "granularity": cfg["granularity"],
                "interval": INTERVAL,
                "metrics": cfg["metrics"],
                "queryContext": cfg["queryContext"]
            }
        }
    }

    # Perform the API call
    resp = requests.post(url, headers=headers, json=payload, verify=False)
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        logger.error("Error fetching %s for ID %s: %s", cfg["aggregation"], oid, e)
        logger.error("Response body:\n%s", resp.text)
        return None, None

    # Parse out the 'result' array and build a metric→series map
    attrs   = resp.json().get("data", {}).get("attributes", {})
    results = attrs.get("result", [])
    series  = { item["metric"]: item.get("series", []) for item in results }
    return results, series

# ─── Script entrypoint ───────────────────────────────────────────────────────
if __name__ == "__main__":
    # Echo configuration
    print("INTERVAL =", INTERVAL)
    print("Monitored objects:", monitored_list)

    # Authenticate once
    token = get_bearer_token()
    if not token:
        sys.exit(1)
    print("Bearer token acquired.\n")

    # Loop and fetch each object
    for oid, otype in monitored_list:
        print(f"--- Processing ID={oid} as type='{otype}' ---")
        cfg_t = METRIC_CONFIG.get(otype)
        if not cfg_t:
            print(f"⚠️  Unknown objectType '{otype}', skipping")
            continue

        results, series = fetch(token, oid, cfg_t)
        if results is None:
            # Already logged the error
            continue

        if results:
            print(f"\nResults for {otype} [{oid}]:")
            print(json.dumps(results, indent=2))
        else:
            print(f"No data returned for {otype} ID {oid}\n")
