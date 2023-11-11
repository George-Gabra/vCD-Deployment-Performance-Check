# VMware vCloud Director vAPPs Deployment Performance Check

## Table of Contents

- [Overview](#overview)
- [Usage](#usage)
- [Examples](#examples)
- [Ansible Playbook Description](#ansible-playbook-description)

## Overview

This script is designed to check performance of vApp deployments on VMware vCloud Director. It automates the deployment of a vApp from a specified template either on the default vDC configured on the tenant at the time of execution or a randomly selected vDC if no default vDC was found. If the deployment exceeds the desired deployment time threshold, the script sends a high-urgent notification to a predefined email address. The script streams logs to VMware Aria Operations for Logs.

## Usage

### Parameters

The script takes the following parameters:

- **CloudURI**: The URI of the vCD .
- **Tenant**: The name of the organization or tenant.
- **Username**: The username for logging into the organization/tenant.
- **Password**: The password associated with the provided username.
- **vAPP_Name**: The desired name for the vApp to be deployed.
- **Template_Name**: The name of the template to be used for the vApp deployment.
- **Catalog_Name**: The name of the catalog where the template is stored.
- **Timeout**: The desired deployment timeout threshold in seconds.

### Examples

The example demonstrates how to run the script with the required parameters.

```bash
python3 vdc_deployment_performance_check.py CloudURI=cloud.example.com Tenant=sysadmins Username=svc-user Password=PASSWORD vAPP_Name=Test_Performance_vAPP Template_Name=ubuntu-latest Catalog_Name=vCloud-Demos Timeout=7200
vCD_PerfChecker: INFO: 09/11/2023 10:46:39: Logging in cloud=cloud.example.com, org=sysadmins, user=svc-user
vCD_PerfChecker: INFO: 09/11/2023 10:46:41: Fetching organization sysadmins...
vCD_PerfChecker: WARNING: 09/11/2023 10:46:43: vAPP Test_Performance_vAPP already exists on vDC Provider09, checking if it has active tasks...
vCD_PerfChecker: INFO: 09/11/2023 10:46:44: vAPP Test_Performance_vAPP has no active tasks, deleting it....
vCD_PerfChecker: INFO: 09/11/2023 10:46:46: Start deleting vApp Test_Performance_vAPP...
vCD_PerfChecker: INFO: 09/11/2023 10:47:01: vApp Test_Performance_vAPP has been deleted.
vCD_PerfChecker: INFO: 09/11/2023 10:47:05: Default vDC is _DEFAULT_Provider03
vCD_PerfChecker: INFO: 09/11/2023 10:47:08: Deploying vApp Test_Performance_vAPP on tenant sysadmins....
vCD_PerfChecker: INFO: 09/11/2023 10:47:08: vAPP Test_Performance_vAPP creation task status is queued....
vCD_PerfChecker: INFO: 09/11/2023 10:47:38: vAPP Test_Performance_vAPP creation task status is running....
vCD_PerfChecker: INFO: 09/11/2023 10:48:08: vAPP Test_Performance_vAPP creation task status is running....
vCD_PerfChecker: INFO: 09/11/2023 10:48:38: vAPP Test_Performance_vAPP creation task status is running....
vCD_PerfChecker: INFO: 09/11/2023 10:49:08: vAPP Test_Performance_vAPP creation task status is success....
vCD_PerfChecker: INFO: 09/11/2023 10:49:39: vApp Test_Performance_vAPP created on cloud.example.com tenant sysadmins vDC _DEFAULT_Provider03 in 150.94408702850342 seconds.
vCD_PerfChecker: INFO: 09/11/2023 10:50:40: Start deleting vApp Test_Performance_vAPP...
vCD_PerfChecker: INFO: 09/11/2023 10:50:56: vApp Test_Performance_vAPP has been deleted.
vCD_PerfChecker: INFO: 09/11/2023 10:50:56: Logging out from cloud.example.com tenant sysadmins
```

## Ansible Playbook Description
Ansible playbook vcd_deployment_performance_check_playbook.yml can be used to run vcd_deployment_performance_check.py script on multiple cloud locations. This Ansible playbook runs the performance check script with the corresponding parameters on each cloud location specified in the CloudLocations group from ansible_hosts inventory file. The playbook will use the variables defined in vars.yml to customize the execution for each cloud location.

```bash
ansible-playbook vcd_deployment_performance_check_playbook.yml -i ansible_hosts
```
