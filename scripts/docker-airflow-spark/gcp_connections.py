from airflow import settings
from airflow.models import Connection
import os

def create_connections():
    conn = Connection(
        conn_id='google_cloud_default',
        conn_type='google_cloud_platform',
        extra={
            'project': os.environ.get('GCP_PROJECT_ID'),
            'key_path': '/opt/airflow/credentials/kestra-demo-batch-pipeline-credentials.json'
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