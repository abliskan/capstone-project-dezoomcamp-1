## Setup Terraform for Automate GCP Services

1. Install terraform on local machine
2. Check the Terraform version:
```
terraform -v
```
3. Go to project directory
```
cd ..\capstone-project-dezoomcamp-1\terraform
```
4. Initialize Terraform
```
terraform init
```
5. Checks configuration changes against remote state and cloud resources
```
terraform plan
```
6. Validate to catch syntax errors, misconfigurations, or unsupported arguments
```
terraform validate
```
7. apply
```
terraform apply
```
8. <Optional> Use this if you want to deleting infrastructure resources present in the state file
```
terraform destroy
```
<br>
![alt text](https://github.com/abliskan/capstone-project-dezoomcamp-1/blob/main/assets/GCP%20VM.png)
