import boto3
import os
import datetime
from datetime import date
from datetime import timedelta

session = boto3.Session(profile_name='default')

# Connect to EC2 in Source region
source_client = session.client('ec2', region_name='us-east-1')

yesterday = (datetime.datetime.now() - timedelta(days=1)).date()
#today = (datetime.datetime.now() - timedelta(days=0)).date()

response = source_client.describe_snapshots(
  Filters=[
    {
      'Name': 'tag-key',
      'Values': [ 'Group' ]
    },
    {
      'Name': 'tag-value',
      'Values': [ 'elasticsearch' ]
    },
  ]
  )

# Connect to EC2 in Destination region
destination_client = session.client('ec2', region_name='us-west-1')

snapshots = response['Snapshots']
for snapshot in snapshots:
  snapdate = snapshot['StartTime'].date()
  volSize = snapshot['VolumeSize']
#  if snapdate >= yesterday and volSize > 500 and volSize < 1000: # to add additional conditions
  if snapdate >= yesterday:    
    mytags = snapshot['Tags'];
    print(mytags)
    print(volSize)
    print(snapshot['SnapshotId'], snapdate)

    # remove aws:* tags because they are used internally from a list.
    mytags.remove({u'Value': 'Default Schedule', u'Key': 'aws:dlm:lifecycle-schedule-name'})
    mytags.remove({u'Value': 'policy-06467effff93a871e', u'Key': 'aws:dlm:lifecycle-policy-id'})
    # print(snapshot['SnapshotId'], snapdate)

    # copy snapshot and pass retrieve tags
    copy_response = destination_client.copy_snapshot(
        Description='Snapshot copied from' + snapshot['SnapshotId'],
        DestinationRegion='us-west-1',
        SourceRegion='us-east-1',
        SourceSnapshotId=snapshot['SnapshotId'],
        TagSpecifications=[
            {
            'ResourceType': 'snapshot',
            'Tags' : mytags
            }
        ]#,
        #DryRun=True
    )
    print(copy_response)
