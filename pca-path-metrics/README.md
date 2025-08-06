**PCA Metrics Collector**

This script fetches TWAMP session and interface metrics from the Cisco Provider Connectivity Assurance (PCA) API.
---

## Prerequisites

- Python 3.8 or newer
- Internet access to Accedian tenant

## Installation

1. Clone or download this repository.
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## `config.ini` Setup

Create a file named `config.ini` alongside `pca_metrics.py` with the following structure:

```ini
[auth]
PCA_BASE_URL = https://tenant.analytics.accedian.io
USERNAME     = your_username@company.com
PASSWORD     = your_password

[metrics]
# Granularity for both session and interface metrics (ISO 8601 duration)
granularity       = PT5M
# Time window in ISO8601 form: start/end
timeinterval       = 2025-07-21T20:48:33.657Z/2025-07-21T21:48:33.657Z
# List of ["objectId","objectType"] pairs; supported types:
#   - twamp-sf
#   - cisco-telemetry-xe-interface
monitored_objects = [["<TWAMP_SESSION_ID>","twamp-sf"],["<INTERFACE_ID>","cisco-telemetry-xe-interface"]]
```

Replace placeholders with your actual credentials, timestamps, and object IDs.

## Usage

Run the script:

```bash
python3 pca_metrics.py
```

It will output metrics for each monitored object. If you want informational logs only, the script defaults to INFO level.

## Requirements File (`requirements.txt`)

Create a file named `requirements.txt` in the same directory with the following contents:

```
requests
```

Install with:

```bash
pip install -r requirements.txt
```

---

**Tip:** To save output to a file:

```bash
python3 pca_metrics.py > metrics_output.json
```

Refer to the API docs for full field definitions.
The metrics retrieval API is https://api.accedian.io/session.html#tag/MetricsServiceV3/operation/GetDerivedMetricsGroupByV3

