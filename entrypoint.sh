
#!/bin/bash
# scripts/entrypoint.sh

# Setup GCP connections
python /opt/airflow/scripts/gcp_connections.py

# Execute the original entrypoint with the provided command
exec /entrypoint "$@"