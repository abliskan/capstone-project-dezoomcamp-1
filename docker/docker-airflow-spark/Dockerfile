## choose the base image and the python version
FROM apache/airflow:latest

## set the user as root, helps with the installation permissions :)
USER root

## set environment varibale to avoid ui pop-ups during installations.
ENV DEBIAN_FRONTEND=noninteractive

## install JDK necessary packages in the image,
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    apt-transport-https \
    build-essential \
    gcc \
    gnupg2 \
    libssl-dev \
    libffi-dev \
    libpq-dev \
    libmariadb-dev-compat \
    libmariadb-dev \
    lsb-release \
    openjdk-17-jdk \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*


## set up java home. Debian 12 bookworm comes with jdk-17 as default.
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"
RUN export JAVA_HOME

## for regular apache-ariflow installation.
USER airflow
COPY requirements.txt /
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}"  \
apache-airflow-providers-apache-spark \
-r /requirements.txt 

# Install Google Cloud SDK
RUN curl -sSL https://sdk.cloud.google.com | bash
ENV PATH $PATH:/home/airflow/google-cloud-sdk/bin

# Create script to setup GCP connections
RUN mkdir -p /opt/airflow/scripts
COPY scripts/gcp_connections.py /opt/airflow/scripts/

# Add GCP credentials
RUN mkdir -p /opt/airflow/credentials/
COPY credentials/<insert_sample_gcp_credentials_path> /opt/airflow/credentials/
COPY credentials/<insert_sample_credentials_key_base64_path> /opt/airflow/credentials/

# Setup GCP authentication
ENV GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/<insert_sample_gcp_credentials>

# Create directory for GCS connector
RUN mkdir -p /opt/airflow/config

# Download GCS connector
RUN curl -o /opt/airflow/config/gcs-connector-hadoop3-latest.jar \
    https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-hadoop3-latest.jar