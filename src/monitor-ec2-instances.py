import os
import json
import boto3
import requests

def send_slack_message(slack_webhook_url, slack_message):
  print('>send_slack_message:slack_message:'+slack_message)

  slack_payload = {
      'text': slack_message
  }

  print('>send_slack_message:posting message to slack channel')
  response = requests.post(slack_webhook_url, json.dumps(slack_payload))
  response_json = response.text
  print('>send_slack_message:response after posting to slack:'+str(response_json))

def _get_regions():
    client = boto3.client("ec2")
    get_regions = client.describe_regions()
    regions = [region['RegionName'] for region in get_regions['Regions']]

    return regions

def find_running_ec2instances():
  regions = _get_regions()

  notification_message = 'The following EC2 instance(s) are currently running and are costing you money. Turn them off if you have finished using them: \n'
  slack_webhook_url = os.environ['SLACK_WEBHOOK_URL']

  # find running instances in each of the regions
  total_running_ec2_instances = 0

  for region in regions:
    client = boto3.client("ec2", region_name=region)
    running_ec2_instances = client.describe_instances(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values': [
                    'running'
                ]
            }

        ],
        MaxResults=1000,
    )
    num_running_ec2_instances = len(running_ec2_instances['Reservations'])

    if num_running_ec2_instances > 0:
        # there is at least one running instance in this region
        total_running_ec2_instances += num_running_ec2_instances

        for instance in running_ec2_instances['Reservations']:
            ec2_info = 'InstanceType:' + instance['Instances'][0]['InstanceType'] + ' LaunchTime(UTC):' + str(instance['Instances'][0]['LaunchTime'])
            ec2_info += ' PrivateIpAddress:' + instance['Instances'][0]['PrivateIpAddress']

            try:
                ec2_info += ' PublicIpAddress:' + instance['Instances'][0]['PublicIpAddress']
            except:
                print('>find_running_ec2instances:this is a private instance - no public ip address found')

            # find the name of this instance, if it exists
            ec2_instance_name = ''
            try:
                tags = instance['Instances'][0]['Tags']

                # find a tag with Key == Name. This will contain the instance name. If no such tag exists then the name for this instance will be reported as blank
                for tag in tags:
                    if tag['Key'] == 'Name':
                        ec2_instance_name = tag['Value']
            except:
                ec2_instance_name = ''  # if no tags were found, leave ec2 instance name as blank

            ec2_info = 'Region:' + region + ' Name:' + ec2_instance_name + ' ' + ec2_info

            print('>find_running_ec2instances:running ec2 instance found:' + str(ec2_info))
            notification_message += ec2_info + '\n'

    print('>find_running_ec2instances:Number of running ec2-instances[' + region + ']:'+str(num_running_ec2_instances))

  print('>find_running_ec2instances:Total number of running ec2_instances[all regions]:'+str(total_running_ec2_instances))
  
  if total_running_ec2_instances > 0:
      print('>find_running_ec2instances:Slack notification message:' + notification_message)
      send_slack_message(slack_webhook_url, notification_message)
      
  return total_running_ec2_instances


def lambda_handler(event, context):
  num_running_instances = find_running_ec2instances()
  return {
      'statusCode': 200,
      'body': json.dumps('Number of EC2 instances currently running [all regions]:' + str(num_running_instances))
  }
