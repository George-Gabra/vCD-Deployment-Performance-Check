import sys
import logging
import traceback
import urllib3
import requests
import time
import random
from datetime import datetime
from pyvcloud.vcd.client import BasicLoginCredentials
from pyvcloud.vcd.client import Client
from pyvcloud.vcd.client import EntityType
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.vapp import VApp
from pyvcloud.vcd.exceptions import EntityNotFoundException
from pyvcloud.vcd.task import Task
from pyvcloud.vcd.client import TaskStatus
from pyvcloud.vcd.client import EntityType
from pyvcloud.vcd.client import RelationType
from pyvcloud.vcd.utils import task_to_dict
from pyvcloud.vcd.utils import to_dict

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Create Logger
logger = logging.getLogger('script_logger')
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s: %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)

# Start: Collect arguments
def parse_arguments(arg):
    parts = arg.split('=')
    if len(parts) != 2:
        print("Invalid argument format: {0}".format(arg))
        sys.exit(1)
    return parts[0], parts[1]

if len(sys.argv) != 9:
    print("Usage: python3 {0} CloudURI=cloud.example.com Tenant=sysadmins Username=svc-user Password=PASSWORD vAPP_Name=Test_Performance_vAPP Template_Name=ubuntu-latest Catalog_Name=vCloud-Demos Timeout=7200\nNote: Timeout value should be passed in seconds".format(sys.argv[0]))
    sys.exit(1)

arguments = {}
for i in range(1, len(sys.argv)):
    key, value = parse_arguments(sys.argv[i])
    arguments[key] = value

cloud = arguments.get('CloudURI', None)
org = arguments.get('Tenant', None)
user = arguments.get('Username', None)
password = arguments.get('Password', None)
vappname = arguments.get('vAPP_Name', None)
templatename = arguments.get('Template_Name', None)
catalogname = arguments.get('Catalog_Name', None)
timeout = arguments.get('Timeout', None)
# End: parse_arguments function

# Default vDC prefix
vdc_name_prefix = '_DEFAULT_'

# Disable warnings from self-signed certificates.
requests.packages.urllib3.disable_warnings()

# Login. SSL certificate verification is turned off to allow self-signed
# certificates.  You should only do this in trusted environments.
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
logger.info(dt_string + ": Logging in cloud={0}, org={1}, user={2}".format(cloud, org, user))
client = Client(cloud, verify_ssl_certs=False, log_file='pyvcloud.log', log_requests=True, log_headers=True, log_bodies=True)
client.set_highest_supported_version()
client.set_credentials(BasicLoginCredentials(user, org, password))
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
logger.info(dt_string + ": Fetching organization "+ org +"...")
org_resource = client.get_org()
org_instance = Org(client, resource=org_resource)


# Start: Check vAPP already exists
def check_vapp_exists(vappname):
 try:
    vapp_exists = False
    active_tasks = False
    vdc_name = None
    task_id = None

    vdclist = org_instance.list_vdcs()
    for vdcs in vdclist:
        vdcname = vdcs['name']
        vdc_resource = org_instance.get_vdc(vdcname)
        vdc = VDC(client, resource=vdc_resource)
        vapps = vdc.list_resources(EntityType.VAPP)
        for vapp in vapps:
            if vapp.get('name') == vappname:
                vapp_exists = True
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                logger.warning (dt_string + ": vAPP " + vappname + " already exists on vDC "+ vdcname + ", checking if it has active tasks...")

# If the vAPP exsists, store its current vDC name
                vdc_name = vdcname

# Reterieve list of queued or running tasks on the organization
                task = Task(client)
                taskslist = task.list_tasks(filter_status_list=['queued', 'preRunning', 'running'],newer_first=True)

# Check the object of each task to find out if the vAPP has any active tasks 
                for task in taskslist:
                    if task.get('objectName') == vappname:
                        active_tasks = True
                        task_urn = task.get('id')
                        split_parts = task_urn.split(':')
                        task_id = split_parts[-1]
                        break


 except Exception as e:
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    logger.error (str(e))
 
 finally:
  pass

 return vapp_exists, active_tasks, vdc_name, task_id
# End: check_vapp_exists function


# Start: Get current default vDC from the cloud tenant
def get_default_vdc():
 try:
    vdcname = None
    vdclist = org_instance.list_vdcs()
    available_vdcs = []

# Build list of available vDCs' names by excluding any vDC start with "DONT_USE" prefix or disabled vDCs
    for i in range(0, len(vdclist)):
        vdc = vdclist[i] 
        vdc_resource = org_instance.get_vdc(vdc['name'])
        if not vdc['name'].startswith("DONT_USE") and vdc_resource.IsEnabled:
            available_vdcs.append(vdc['name'])

# Exit the script if there are no available vDCs
    if not available_vdcs:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        logger.critical (dt_string + ": No available vDCs on tenant " + org)
        sys.exit(1)

# Get the vDC which starts with vDC prefix
    for vdc in available_vdcs:
        if vdc.startswith(vdc_name_prefix):
            vdcname = vdc
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            logger.info (dt_string + ": Default vDC is " + vdcname)
            break

# If there is no default vDC, select a random one
    if available_vdcs and not vdcname:
        vdcname = random.choice(available_vdcs)
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        logger.info (dt_string + ": No default vDC available on tenant " + org + ", randomly selected vDC " + vdcname)
        

 except Exception as e:
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    logger.error (str(e))

 finally:
    pass

 return vdcname
# End: get_default_vdc function

# Start: Deploy the vAPP. Default vDC is passed along with vAPP name, Template name, Catalog and desired creation timeout in seconds
def create_vApp(vdcname, vapp_name, template_name, catalog_name, timeout):
 try:
  vdc_resource = org_instance.get_vdc(vdcname)
  vdc = VDC(client, resource=vdc_resource)
  vapp = vdc.instantiate_vapp(vapp_name, catalog=catalog_name, template=template_name, description="vAPP created to test deployment performance", deploy=False, power_on=False)
  now = datetime.now()
  dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
  logger.info(dt_string + ": Deploying vApp " + vapp_name + " on tenant " + org +"....")
  task = vapp.Tasks.Task[0]
  task_urn = task.get('id')
  split_parts = task_urn.split(':')
  task_id = split_parts[-1]

# Start time counter for the vAPP deployment task
  start_time = time.time()
  target_duration = int(timeout)
  while time.time() - start_time < target_duration:
   now = datetime.now()
   taskstatus = client.get_task_monitor().get_status(task)
   dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
   logger.info (dt_string + ": vAPP " + vapp_name + " creation task status is " + taskstatus + "....")
   time.sleep(30)
   elapsed_time = time.time() - start_time

# Send notification if elapsed time exceeded timeout and the deployment task is still running
   if time.time() - start_time >= target_duration and (taskstatus == 'queued' or taskstatus == 'running'):
    try:
     now = datetime.now()
     dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
     logger.warning (dt_string + ": vAPP creation on " + cloud + " tenant " + org + " vDC " + vdcname + " timeout exeeded")

     send_email(vapp_name, cloud, org, vdcname, task_id, target_duration, 1)
     #cancel_task(client, vdcname, task, task_id)
     #delete_vapp(client, vapp_name, vdcname)
     break

    except Exception as e:
     now = datetime.now()
     dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
     logger.error (str(e))

# If vAPP deployment task completed within timeout value, wait for 60 seconds then delete it
   elif taskstatus == 'success':
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    logger.info (dt_string + ": vApp " + vapp_name + " created in " + str(elapsed_time) + " seconds.")
    time.sleep(60)
    delete_vapp(client, vapp_name, vdcname)
    break

# If vAPP deployment task reported error, delete the vAPP and exit the script
   elif taskstatus == 'error':
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    logger.error (dt_string + ": vApp " + vapp_name + " creation failed check task ID " + task_id + " for details.")
    time.sleep(60)
    delete_vapp(client, vapp_name, vdcname)
    cloud_logout()
    sys.exit(0)
    break

   else:
    pass

 finally:
  pass
# End: create_vApp function

# Start: Function to send email notification
def send_email(vapp_name, cloud_name, org_name, vdc_name, task_id, timeout, message_id):

 smtp_server = 'smtp.example.com'
 smtp_port = 25

 sender_email = 'sender@example.com'
 receiver_email = 'receiver@example.com'

 if message_id == 1:
  subject = f'Critical: vAPP deployment performance check failed on {cloud_name} tenant {org_name}'
  message = f'vAPP deployment performance did not meet performance threshold.\n\n vAPP Name: {vapp_name}\n Cloud Location: {cloud_name}\n Tenant Name: {org_name}\n Current Default vDC: {vdc_name}\n Task ID: {task_id}\n Timeout Value: {timeout} seconds.'
   
 elif message_id == 2:
  subject = f'Warning: vAPP deployment performance check on {cloud_name} tenant {org_name} detected running task'
  message = f'vDC deployment performance check job detected previous deployment task still running.\n\n vAPP Name: {vapp_name}\n Cloud Location: {cloud_name}\n Tenant Name: {org_name}\n Task running on vDC: {vdc_name}\n Task ID: {task_id}.\n\n Check previous script alerts reported for that tenant.'

 else: 
  now = datetime.now()
  dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
  logger.error ("Failed to send email. No proper message ID passed")


 msg = MIMEMultipart()
 msg['From'] = sender_email
 msg['To'] = receiver_email
 msg['Subject'] = subject
 msg['X-Priority'] = '2'

 msg.attach(MIMEText(message, 'plain'))

 try:
    server = smtplib.SMTP(smtp_server, smtp_port)

    server.sendmail(sender_email, receiver_email, msg.as_string())

 except Exception as e:
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    logger.error ("Failed to send email." + str(e))

 finally:
    server.quit()
# End: send_email function

# Start: Delete vAPP 
def delete_vapp(client, vapp_name, vdcname):
 try:
  vdc_resource = org_instance.get_vdc(vdcname)
  vdc = VDC(client, resource=vdc_resource)
  vappdelete = vdc.delete_vapp(vapp_name, force=True)

  now = datetime.now()
  dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
  logger.info (dt_string + ": Start deleting vApp " + vapp_name + "...")

  client.get_task_monitor().wait_for_success(vappdelete)

  now = datetime.now()
  dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
  logger.info (dt_string + ": vApp " + vapp_name + " has been deleted.")

 except Exception as e:
  now = datetime.now()
  dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
  logger.error ("Failed to delete vAPP " + vapp_name + " " + str(e))
# End: delete_vapp function


# Start: Function to cancel the deployment task 
def cancel_task(client, vdcname, task, task_id):
 vdc_resource = org_instance.get_vdc(vdcname)
 vdc = VDC(client, resource=vdc_resource)
 now = datetime.now()
 dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
 logger.info (dt_string + ": Cancelling vAPP creation task " + task_id)
 userdetails = org_instance.get_user(user)
 task_updater = Task(client)
 result = client.get_resource(f"{client.get_api_uri()}/task/{task_id}")

 task_href = task.get('href')
 task_namespace = task.get('serviceNamespace')
 task_operation = task.get('operation')
 task_operation_name = task.get('operationName')
 task_details = task.Details.text
 task_owner_href = task.Owner.get('href')
 task_owner_name = task.Owner.get('name')
 task_owner_type = task.Owner.get('type')
 task_organization = task.Organization.get('name')
 task_user = task.User.get('name')
 task_user_href = userdetails.get('href')
 
 try:
  updated_task = task_updater.update(
                    task_href=task_href,
                    status='aborted',
                    progress='100',
                    namespace=task_namespace,
                    operation=task_operation,
                    operation_name=task_operation_name,
                    details="Aborted creation task of vAPP",
                    owner_href=task_owner_href,
                    owner_name=task_owner_name,
                    owner_type=task_owner_type,
                    user_href=task_user_href,
                    user_name=task_user)
  print (updated_task)

 except Exception as e:
  now = datetime.now()
  dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
  logger.error ("Failed to cancel vAPP creation task" + task_id + " " + str(e))
# End: cancel_task function

# Start: Logout from cloud 
def cloud_logout():
 now = datetime.now()
 dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
 logger.info (dt_string + ": Logging out from " + cloud + " tenant " + org)
 client.logout()
# End: cloud_logout function


def main():
    vapp_exists = False
    active_tasks = False
    vdc_name = None
    task_id = None

    vapp_exists, active_tasks, vdc_name, task_id = check_vapp_exists(vappname)

# If vAPP exists and has active tasks, send email notification and logout
    if vapp_exists and active_tasks:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        logger.warning (dt_string + ": vAPP " + vappname + " has active task " + task_id)
        send_email(vappname, cloud, org, vdc_name, task_id, 0, 2)
        cloud_logout()
        sys.exit(0)

# If vAPP exists and has no active tasks, delete it and redeploy new one on the current default vDC 
    elif vapp_exists and not active_tasks:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        logger.info (dt_string + ": vAPP " + vappname + " has no active tasks, deleting it....")
        delete_vapp(client, vappname, vdc_name)
        defaultvdc = get_default_vdc()
        create_vApp(defaultvdc, vappname, templatename, catalogname, timeout)
        cloud_logout()

# If vAPP doesn't exists, get the current default vDC and deploy it 
    else:
        defaultvdc = get_default_vdc()
        create_vApp(defaultvdc, vappname, templatename, catalogname, timeout)
        cloud_logout()


if __name__ == "__main__":
    main()
