terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.51.0"
    }
  }
}


provider "google" {
  credentials = file(var.credentials)
  project     = var.project
  region      = var.region
}

locals {
  script_content          = file("../Install_docker.sh")
  gsc_service_acct        = file("<insert_gcp_credentials_file_path>")
  gsc_service_acct_base64 = base64encode(file("<insert_gcp_credentials_infile_path>"))
}

resource "google_storage_bucket" "demo-bucket" {
  name          = var.gcs_bucket_name
  location      = var.location
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}

resource "google_bigquery_dataset" "demo_dataset" {
  dataset_id = var.bg_dataset_name
  location   = var.location
}

data "google_compute_image" "image" {
  name    = var.image
  project = var.image_family
}

resource "google_compute_instance" "vm_instance" {
  name         = "dezoomcamp-vm"
  machine_type = var.machine_type
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = data.google_compute_image.image.self_link
    }
  }

  network_interface {
    network = var.network
    access_config {

    }
  }

  service_account {
    email = "${var.service_account}"
    scopes = ["cloud-platform"]
  }

  metadata = {
    ssh-keys  = "${var.user}:${file(var.ssh_key_file)}"
    user-data = <<-EOF
    #!/bin/bash
    
    sudo apt-get update
    echo '${local.script_content}' > /tmp/install_docker.sh
    chmod +x /tmp/install_docker.sh
    bash /tmp/install_docker.sh

    sudo mkdir -p /home/${var.user}/credentials
    chmod -R 755 /home/${var.user}/credentials

    cd /home/${var.user}

  EOF
  }
}

output "public_ip" {
  value = google_compute_instance.vm_instance.network_interface[0].access_config[0].nat_ip
}