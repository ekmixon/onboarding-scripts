#!/usr/bin/env python

import json
import os
import sys
from time import sleep
import argparse
import configparser
import requests
import random, string
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from datetime import datetime
from datetime import timedelta 

d9id = ''
d9secret = ''
cloudid = ''
mode = ''
print('\n:: Dome9 Snapshot Assessment :: \nExecution time: ' + str(datetime.now()) + '\n')

def add_aws_account(name, arn, extid):

    url = "https://api.dome9.com/v2/CloudAccounts"
    urldata = {"name": name, "credentials": {"arn": arn, "secret": extid, "type": "RoleBased", "isReadOnly": "true"}, "fullProtection": "false"}
    headers = {'content-type': 'application/json'}

    print('\nAdding target AWS account to Dome9...')

    try:
        resp = requests.post(url, auth=HTTPBasicAuth(d9id, d9secret), json=urldata, headers=headers)
        
        # If the response was successful, no Exception will be raised
        resp.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}') 
    except Exception as err:
        print(f'Other error occurred: {err}') 
    else:
        print('Success!')
    
    if resp.status_code == 201:
        resp = json.loads(resp.content)
        print('AWS account added successfully, id: ' + resp['id'])
        return resp['id']
    
    elif resp.status_code == 400:
        print('AWS Cloud Account already added or bad request. Please remove the account from Dome9 before using this script.')

    else:
        print('Error when attempting to add AWS account.')
        print(resp)
        return False

def add_azure_account(name, subscriptionid, tenantid, appid, appkey):

    url = "https://api.dome9.com/v2/AzureCloudAccount"
    urldata = {"name":name,"subscriptionId":subscriptionid,"tenantId":tenantid,"credentials":{"clientId":appid,"clientPassword":appkey},"operationMode":"Read"}
    headers = {'content-type': 'application/json'}

    print('\nAdding target Azure subscription to Dome9...')

    try:
        resp = requests.post(url, auth=HTTPBasicAuth(d9id, d9secret), json=urldata, headers=headers)
        
        # If the response was successful, no Exception will be raised
        resp.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}') 
    except Exception as err:
        print(f'Other error occurred: {err}') 
    else:
        print('Success!')
    
    if resp.status_code == 201:
        resp = json.loads(resp.content)
        print('Azure Subscription added successfully, id: ' + resp['id'])
        return resp['id']
    
    elif resp.status_code == 400:
        print('Azure Subscription already added or bad request. Please remove the subscription from Dome9 before using this script.')

    else:
        print('Error when attempting to add Azure subscription.')
        print(resp)
        return False

def add_gcp_account(name, key):
    
    url = "https://api.dome9.com/v2/GoogleCloudAccount"
    urldata = {"name":name,"serviceAccountCredentials":key}
    headers = {'content-type': 'application/json'}

    print('\nAdding target GCP project to Dome9...')

    try:
        resp = requests.post(url, auth=HTTPBasicAuth(d9id, d9secret), json=urldata, headers=headers)
        
        # If the response was successful, no Exception will be raised
        resp.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}') 
    except Exception as err:
        print(f'Other error occurred: {err}') 
    else:
        print('Success!')
    
    if resp.status_code == 201:
        resp = json.loads(resp.content)
        print('GCP Project added successfully, id: ' + resp['id'])
        return resp['id']
    
    elif resp.status_code == 400:
        print('GCP Project already added or bad request. Please remove the project from Dome9 before using this script.')

    else:
        print('Error when attempting to add GCP Project.')
        print(resp)
        return False
        
def add_notification_policy(name, email, cronexpression):

    url = "https://api.dome9.com/v2/Compliance/ContinuousComplianceNotification"
    urldata = {"name":name,"description":"","alertsConsole":False,"scheduledReport":{"emailSendingState":"Enabled","scheduleData":{"cronExpression":cronexpression,"type":"Detailed","recipients":[email]}},"changeDetection":{"emailSendingState":"Disabled","emailPerFindingSendingState":"Disabled","snsSendingState":"Disabled","externalTicketCreatingState":"Disabled","awsSecurityHubIntegrationState":"Disabled"},"gcpSecurityCommandCenterIntegration":{"state":"Disabled"}}
    headers = {'content-type': 'application/json'}

    print('\nCreating Notification Policy...')
    
    try:
        resp = requests.post(url, auth=HTTPBasicAuth(d9id, d9secret), json=urldata, headers=headers)
        
        # If the response was successful, no Exception will be raised
        resp.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}') 
    except Exception as err:
        print(f'Other error occurred: {err}') 
    else:
        print('Success!')

    if resp.status_code == 201:
        resp = json.loads(resp.content)
        print('Dome9 Notification policy added successfully. name: ' + name + ', id: ' + resp['id'])
        return resp['id']
    
    elif resp.status_code == 400:
        print('Dome9 Notification policy bad request.')
        print('resp')

    else:
        print('Error when attempting to add Notification policy.')
        print(resp)
        return False
        
def add_cc_policy(d9cloudaccountid, extaccountid, notificationid, rulesetid):

    url = "https://api.dome9.com/v2/Compliance/ContinuousCompliancePolicy/ContinuousCompliancePolicies"
    urldata = [{"cloudAccountId":d9cloudaccountid,"bundleId":rulesetid,"externalAccountId":extaccountid,"cloudAccountType":cloudid,"notificationIds":[notificationid],"product":"compliance"}]
    headers = {'content-type': 'application/json'}
    print('\nCreating Continuous Compliance Policy...')

    try:
        resp = requests.post(url, auth=HTTPBasicAuth(d9id, d9secret), json=urldata, headers=headers)
        
        # If the response was successful, no Exception will be raised
        resp.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}') 
    except Exception as err:
        print(f'Other error occurred: {err}') 
    else:
        print('Success!')

    if resp.status_code == 201:
        resp = json.loads(resp.content)
        print('Dome9 Continuous Compliance policy added successfully. id: ' + resp[0]['id'])
        return resp[0]['id']
    
    elif resp.status_code == 400:
        print('Dome9 Continuous Compliance policy bad request.')
        print(resp)

    else:
        print('Error when attempting to add Continuous Compliance policy.')
        print(resp)
        return False

def run_assessment(d9cloudaccountid, rulesetid):
    url = "https://api.dome9.com/v2/assessment/bundleV2"
    urldata = {"Id": rulesetid, "CloudAccountId": d9cloudaccountid, "CloudAccountType": cloudid, "Region":""}
    headers = {'content-type': 'application/json'}
    print('\nRunning Compliance Assessment using ruleset id: ' + str(rulesetid))

    try:
        resp = requests.post(url, auth=HTTPBasicAuth(d9id, d9secret), json=urldata, headers=headers)
        
        # If the response was successful, no Exception will be raised
        resp.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}') 
    except Exception as err:
        print(f'Other error occurred: {err}') 
    else:
        print('Success!')

    if resp.status_code == 200:
        resp = json.loads(resp.content)
        print('Compliance Assessment completed successfully. \nView ephemeral report at: https://secure.dome9.com/v2/compliance-engine/result/' + str(resp['id']))
        return True
    
    else:
        print('Error when attempting to run assessment.')
        print(resp.content)
        return False
    
def remove_cloud_account(id):

    print('\nRemoving Cloud Account...')
    
    if mode == 'aws':
        url = "https://api.dome9.com/v2/cloudaccounts/" + id
    elif mode == 'azure':
        url = "https://api.dome9.com/v2/AzureCloudAccount/" + id
    elif mode == 'gcp':
        url = "https://api.dome9.com/v2/GoogleCloudAccount/" + id
    else:
        print('Invalid cloud provider mode: ' + mode)
        return False

    urldata = {}
    headers = {'content-type': 'application/json'}

    try:
        resp = requests.delete(url, auth=HTTPBasicAuth(d9id, d9secret), json=urldata, headers=headers)
        
        # If the response was successful, no Exception will be raised
        resp.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}') 
    except Exception as err:
        print(f'Other error occurred: {err}') 
    else:
        print('Success!')
    
def unassociate_cc_policy(id):

    url = "https://api.dome9.com/v2/Compliance/ContinuousCompliancePolicy/" + id
    urldata = {}
    headers = {'content-type': 'application/json'}
    print('\nUnassociating Compliance Policy...')

    try:
        resp = requests.delete(url, auth=HTTPBasicAuth(d9id, d9secret), json=urldata, headers=headers)
        
        # If the response was successful, no Exception will be raised
        resp.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}') 
    except Exception as err:
        print(f'Other error occurred: {err}') 
    else:
        print('Success!')
    
def delete_notification_policy(id):

    url = "https://api.dome9.com/v2/Compliance/ContinuousComplianceNotification/" + id
    urldata = {}
    headers = {'content-type': 'application/json'}
    print('\nDeleting Notification Policy...')

    try:
        resp = requests.delete(url, auth=HTTPBasicAuth(d9id, d9secret), json=urldata, headers=headers)
        
        # If the response was successful, no Exception will be raised
        resp.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}') 
    except Exception as err:
        print(f'Other error occurred: {err}') 
    else:
        print('Success!')    
        
def get_scheduled_report_status(targetstring, email):
    startdatetime = datetime.utcnow() + timedelta(hours=-2)
    enddatetime = datetime.utcnow() + timedelta(hours=2)

    url = 'https://api.dome9.com/v2/Audit?&eventType=AssessmentScheduledReportSentEvent&eventsPerPage=100&fim=false&pageNum=1&startTimestamp=' + str(startdatetime.date()) + 'T' + str(startdatetime.time()) + 'Z&endTimestamp=' + str(enddatetime.date()) + 'T' + str(enddatetime.time()) + 'Z'
    urldata = {}
    headers = {'content-type': 'application/json'}
    #print('Querying Audit Trail...')

    try:
        resp = requests.get(url, auth=HTTPBasicAuth(d9id, d9secret), json=urldata, headers=headers)
        
        # If the response was successful, no Exception will be raised
        resp.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}') 
    except Exception as err:
        print(f'Other error occurred: {err}') 
    #else:
        #print('Success!')
        
    if resp.status_code == 200:
        resp = json.loads(resp.content)
        for item in resp['rows']:
            if item['cell'][4].find(targetstring) > -1 and item['cell'][4].find(email) > -1: 
                return True
    
    else:
        return False

def process_account(account_added, extaccountid):

    print('\nWaiting ' + OPTIONS.delay + ' minutes for cloud sync to complete...')
    syncwait = int(OPTIONS.delay) * 60
    sleep(syncwait)
    print('Showtime!')

    notification_name = OPTIONS.accountname + '_snapshot_' + ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(5))
    utc_datetime = (datetime.utcnow() + timedelta(minutes=4))
    cronexpression = '0 ' + str(utc_datetime.minute) + ' ' + str(utc_datetime.hour) + ' 1/1 * ? *'
    notification_policy_added = add_notification_policy(notification_name, OPTIONS.email, cronexpression)

    cc_policy_added = add_cc_policy(account_added, extaccountid, notification_policy_added, OPTIONS.rulesetid)
    run_assessment(account_added, OPTIONS.rulesetid)

    print('\nAssessment email report is scheduled. Waiting for confirmation...')
    t = 0
    while t < 30:
        t += 1
        sleep(60)
        print('... Try ' + str(t) + '/30')
        notification_found = get_scheduled_report_status(notification_name, OPTIONS.email)
        if notification_found:
            print("\nSuccess! Scheduled report sent to " + OPTIONS.email)
            break

    if not notification_found:
        print("Failed to validate report was sent.")
    
    unassociate_cc_policy(cc_policy_added)
    delete_notification_policy(notification_policy_added)
    remove_cloud_account(account_added) 

# Main
def main(argv=None):

    global OPTIONS, d9id, d9secret, mode, cloudid
    account_added = ''
    notification_added = ''

    config = configparser.ConfigParser()
    config.read("./d9_account.conf")

    # set up our Dome9 API endpoint(s) and other Dome9 dependencies
    global d9id, d9secret
    d9id = config.get('dome9', 'd9id')
    d9secret = config.get('dome9','d9secret')

# handle arguments
    if argv is None:
        argv = sys.argv[2:]

    mode = sys.argv[1].lower()
    print("Mode: " + mode)

    parser = argparse.ArgumentParser("%prog <aws|azure|gcp> [options] ")
    parser.add_argument("--name", dest="accountname", help="Cloud account friendly name")
    if mode == 'aws':
        parser.add_argument("--arn", dest="arn", help="AWS Role ARN for Dome9 *")
        parser.add_argument("--externalid", dest="externalid", help="AWS external ID used for Dome9 Role *")
        parser.add_argument("--rulesetid", dest="rulesetid", default=-16, help="AWS-specific Dome9 Compliance Ruleset ID. Default: -16 (NIST 800-53)")

    elif mode == 'azure':
        parser.add_argument("--subscriptionid", dest="subscriptionid", help="Azure Subscription ID *")
        parser.add_argument("--tenantid", dest="tenantid", help="Azure AD/Tenant ID *")
        parser.add_argument("--appid", dest="appid", help="Azure App (Client) ID for App Registration *")
        parser.add_argument("--key", dest="key", help="Azure App (Client) Secret Key for Azure App Registration *")
        parser.add_argument("--rulesetid", dest="rulesetid", default=-23, help="Azure-specific Dome9 Compliance Ruleset ID. Default: -23 (NIST 800-53)")

    elif mode == 'gcp':
        parser.add_argument("--keyfile", dest="keyfile", help="Path to GCP key file in JSON format of the Dome9 service account")
        parser.add_argument("--rulesetid", dest="rulesetid", default=-25, help="GCP-specific Dome9 Compliance Ruleset ID. Default: -25 (NIST 800-53)")
    
    parser.add_argument("--email", dest="email", help="E-mail Address *")
    parser.add_argument("--delay", dest="delay", default="10", help="Time to wait after account onboarded (in minutes). Default: 10")

    OPTIONS = parser.parse_args(argv)

    if len(sys.argv) == 1:
        parser.print_help()
        os._exit(1)

    if mode == '-h' or mode == '--help':
        parser.print_help()
        os._exit(1)

    if not OPTIONS.email or not OPTIONS.accountname or not OPTIONS.rulesetid:
        print("ERROR: Missing required arguments \n")        
        parser.print_help()
        os._exit(1)

    if mode == 'aws':
        if not OPTIONS.arn or not OPTIONS.externalid:
            print("ERROR: Missing required arguments for mode 'aws'\n")        
            parser.print_help()
            os._exit(1)

        cloudid = 1
        arnparse = OPTIONS.arn.split(':')
        extaccountid = arnparse[4]

        print('Cloud Account \n-ID: ' + extaccountid + '\n-Name: ' + OPTIONS.accountname)
        account_added = add_aws_account(OPTIONS.accountname, OPTIONS.arn, OPTIONS.externalid)

        if account_added:
            process_account(account_added, extaccountid)

    elif mode == 'azure':
        if not OPTIONS.subscriptionid or not OPTIONS.tenantid or not OPTIONS.appid or not OPTIONS.key:
            print("ERROR: Missing required arguments for mode 'azure'\n")        
            parser.print_help()
            os._exit(1)

        cloudid = 7

        print('Cloud Account \n-ID: ' + OPTIONS.subscriptionid + '\n-Name: ' + OPTIONS.accountname)
        account_added = add_azure_account(OPTIONS.accountname, OPTIONS.subscriptionid, OPTIONS.tenantid, OPTIONS.appid, OPTIONS.key)

        if account_added:
            process_account(account_added, OPTIONS.subscriptionid)

    elif mode == 'gcp':
        if not OPTIONS.keyfile:
            print("ERROR: Missing required arguments for mode 'gcp'\n")        
            parser.print_help()
            os._exit(1)

        keyfileexists = os.path.isfile(OPTIONS.keyfile)
        if not keyfileexists:
            print("GCP key file not found on disk: " + OPTIONS.keyfile)
            os._exit(1)

        cloudid = 10
        with open(OPTIONS.keyfile) as json_file:
            key = json.load(json_file)

        print('Cloud Account \n-ID: ' + key['project_id'] + '\n-Name: ' + OPTIONS.accountname)
        account_added = add_gcp_account(OPTIONS.accountname, key)

        if account_added:
            process_account(account_added, key['project_id'])

    return 0

if __name__ == "__main__":
    sys.exit(main())