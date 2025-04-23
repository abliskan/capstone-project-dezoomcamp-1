#!/bin/bash

# Create necessary directories
mkdir -p dags logs plugins credentials scripts

# Decode the GCP credentials from .env
source .env
echo $GCP_SERVICE_ACCOUNT_KEY_BASE64 | base64 -d > credentials/<insert_sample_gcp_credentials_path>

# Create the scripts directory and add the GCP connections script
cat > scripts/gcp_connections.py << EOL
from airflow import settings
from airflow.models import Connection
import os

def create_connections():
    conn = Connection(
        conn_id='google_cloud_default',
        conn_type='google_cloud_platform',
        extra={
            'project': os.environ.get('GCP_PROJECT_ID'),
            'key_path': '/opt/airflow/credentials/<insert_sample_gcp_credentials_path>'
        }
    )
    
    session = settings.Session()
    
    # Check if connection already exists
    existing_conn = session.query(Connection).filter(Connection.conn_id == conn.conn_id).first()
    if existing_conn:
        session.delete(existing_conn)
        session.commit()
    
    session.add(conn)
    session.commit()
    session.close()
    
    print(f"Google Cloud connection '{conn.conn_id}' created successfully.")

if __name__ == '__main__':
    create_connections()
EOL

# Create entrypoint script
cat > entrypoint.sh << EOL
#!/bin/bash
# Setup GCP connections
python /opt/airflow/scripts/gcp_connections.py

# Execute the original entrypoint with the provided command
exec /entrypoint "\$@"
EOL
chmod +x entrypoint.sh

# Start the containers
docker-compose up -d