## choose the base image and the python version
FROM apache/airflow:latest

# Install additional dependencies
USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    install pyspark \
    && rm -rf /var/lib/apt/lists/*

# for regular apache-ariflow installation.
USER airflow

# Install Google Cloud SDK
RUN curl -sSL https://sdk.cloud.google.com | bash
ENV PATH $PATH:/home/airflow/google-cloud-sdk/bin

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Setup GCP authentication
ENV GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/credentials/<insert_sample_gcp_credentials_path>

# Create script to setup GCP connections
RUN mkdir -p /opt/airflow/scripts
COPY scripts/gcp_connections.py /opt/airflow/scripts/

# Add GCP credentials
RUN mkdir -p /opt/airflow/credentials/
COPY credentials/<insert_sample_gcp_credentials_path> /opt/airflow/credentials/
COPY credentials/<insert_sample_credentials_key_base64_path> /opt/airflow/credentials/

# Create directory for GCS connector
RUN mkdir -p /opt/airflow/config

# Download GCS connector
RUN curl -o /opt/airflow/config/gcs-connector-hadoop3-latest.jar \
    https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-hadoop3-latest.jar