variable "credentials" {
  description = "My Credentials"
  default     = "<insert_gcp_credentials_file_path>"
}


variable "project" {
  description = "Project"
  default     = "<insert_gcp_project_id>"
}

variable "region" {
  description = "Region"
  default     = "<insert_gcp_region>"
}

variable "location" {
  description = "Project Location"
  default     = "<insert_gcp_location>"
}

variable "zone" {
  description = "Zone"
  default     = "<insert_gcp_zone>"
}

variable "bg_dataset_name" {
  description = "My Biquery Dataset Name"
  default     = "<insert_bigquery_dataset_name>"
}

variable "gcs_bucket_name" {
  description = "My Storage Bucket Name"
  default     = "<insert_gcs_bucket_name>"
}

variable "gcs_bucket_class" {
  description = "Bucket Storage Class"
  default     = "STANDARD"
}

variable "machine_type" {
  description = "specified image id for instance"
  default = "e2-standard-2"
}

variable "image" {
  description = "Machine Image"
  default     = "ubuntu-2004-focal-v20240307b"
}

variable "image_family" {
  description = "Machine image family for given instance"
  default = "ubuntu-os-cloud"
}

variable "network" {
  description = "network for given instance"
  default = "default"
}

variable "user" {
  description = "User for maching"
  default     = "<insert_username>"
}

variable "service_account" {
  default = "sample.account@gmail.com"
}

variable "ssh_key_file" {
  description = "Path to the SSH public key file"
  default     = "<insert_ssh_key_file_path>"

}