# VMware vCloud Director vAPPs Deployment Performance Check

## Overview

This script is designed to check performance of vApp deployments on VMware vCloud Director. It automates the deployment of a vApp from a specified template either on the default vDC configured on the tenant at the time of execution or a randomly selected vDC if no default vDC was found. If the deployment exceeds the desired deployment time threshold, the script sends a high-urgent notification to a predefined email address.

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
INFO: 19/10/2023 15:59:32: Logging in cloud=cloud.example.com, org=sysadmins, user=svc-user
INFO: 19/10/2023 15:59:35: Fetching organization sysadmins...
WARNING: 19/10/2023 15:59:45: vAPP Test_Performance_vAPP already exists on vDC Provider09, checking if it has active tasks...
INFO: 19/10/2023 15:59:48: vAPP Test_Performance_vAPP has no active tasks, deleting it....
INFO: 19/10/2023 15:59:50: Start deleting vApp Test_Performance_vAPP...
INFO: 19/10/2023 16:00:02: vApp Test_Performance_vAPP has been deleted.
INFO: 19/10/2023 16:00:02: Default vDC is _DEFAULT_Provider03
INFO: 19/10/2023 16:00:07: Deploying vApp Test_Performance_vAPP on tenant sysadmins....
INFO: 19/10/2023 16:00:07: vAPP Test_Performance_vAPP creation task status is queued....
INFO: 19/10/2023 16:00:37: vAPP Test_Performance_vAPP creation task status is running....
INFO: 19/10/2023 16:01:07: vAPP Test_Performance_vAPP creation task status is running....
INFO: 19/10/2023 16:01:37: vAPP Test_Performance_vAPP creation task status is running....
INFO: 19/10/2023 16:02:08: vAPP Test_Performance_vAPP creation task status is success....
INFO: 19/10/2023 16:02:38: vApp Test_Performance_vAPP created in 151.18470907211304 seconds.
INFO: 19/10/2023 16:03:40: Start deleting vApp Test_Performance_vAPP...
INFO: 19/10/2023 16:03:56: vApp Test_Performance_vAPP has been deleted.
INFO: 19/10/2023 16:03:56: Logging out from cloud.example.com tenant sysadmins
```
