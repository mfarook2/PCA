# PCA Path Metrics

A simple Python script to authenticate with Cisco’s Provider Connectivity Assurance (PCA) API and fetch aggregated TWAMP metrics.

## Repo Layout

```
pca-path-metrics/
├── .gitignore
├── README.md
├── requirements.txt
└── main.py
```

## Prerequisites

- Python 3.7+
- `pip install -r requirements.txt`

## Configuration

Edit `main.py` and update the following variables at the top of the file:

```python
PCA_BASE_URL       = "https://your-pca-tenant.analytics.accedian.io"
LOGIN_ENDPOINT     = "/api/v1/auth/login"
AGGREGATE_ENDPOINT = "/api/v3/metrics/aggregate"
USERNAME           = "your.username@example.com"
PASSWORD           = "YourPassword!"
```

- **PCA_BASE_URL**: The base URL for your PCA tenant (e.g. `https://playground.dhus-labs.analytics.accedian.io`).
- **LOGIN_ENDPOINT**: Typically `/api/v1/auth/login`
- **AGGREGATE_ENDPOINT**: Typically `/api/v3/metrics/aggregate`
- **USERNAME** / **PASSWORD**: Your PCA credentials.

## Usage

```bash
python main.py
```

This will:
1. Log in and retrieve a Bearer token.
2. Call the aggregate‐metrics API with a sample payload.
3. Print the JSON response to stdout.

## Customizing the Payload

Inside `fetch_aggregated_metrics`, adjust:

- `interval` (ISO-8601 range to query)
- `aggregation` (`min`/`max`/`avg`/`sum`/`count`)
- `granularity` (e.g. `PT1M`, `PT1H`)
- `globalMetricFilterContext` (monitored object IDs, directions, objectTypes)
- `metrics` (list of metric specs, e.g. `delayVarAvg`, `jitterAvg`, etc.)

Refer to the API docs for full field definitions.
The metrics retrieval API is https://api.accedian.io/session.html#tag/MetricsServiceV3/operation/GetDerivedMetricsGroupByV3

## License

MIT © Your Name
