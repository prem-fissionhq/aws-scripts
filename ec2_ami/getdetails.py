# Script to take the AMI of ec2 instances based on tags. This script will find all the instances with tag 
# <tagName> = <TagValue> and will take the AMI of that. It will also put deleteOn date on AMI based on user defined 
# retention days, the same will be removed by CleanUp lambda function.

import boto3
import collections
import datetime
import os
import time
import logging

profile="684878003660_SkyHiveGlobalAdmins"
ec = boto3.client('ec2', region_name='ca-central-1')
print(ec)

#def lambda_handler(event, context):
def lambda_handler():
    accountNumber = "684878003660"
    retentionDays = 3

    #accountNumber = os.environ['AWS_ACCOUNT_NUMBER']
    #retentionDays = int(os.environ['RETENTION_DAYS'])
    reservations = ec.describe_instances(
        Filters=[
            {'Name': 'tag:Backup', 'Values': ['true']}
        ]
    ).get('Reservations', [])

    #number of instances that are tagged with ami_creation tag
    instances = sum([
            [i for i in r['Instances']]
            for r in reservations
        ], [])

    print("Found %d instances that need backing up" % len(instances))

    to_tag = collections.defaultdict(list)
    amiList = []
    for instance in instances:
        print(instance)
        try:
            retention_days = [int(t.get('Value')) for t in instance['Tags']
                if t['Key'] == 'Retention'][0]
            print("-----------------------",retention_days)
        except IndexError:
            retention_days = retentionDays

            create_time = datetime.datetime.now()
            create_fmt = create_time.strftime('%Y-%m-%d-%H-%M-%S')

            for tag in instance['Tags']:
                if tag['Key'] == 'Name':
                    amiName = tag['Value']
                    print("******* ",amiName)
                    break

            AMIid = ec.create_image(InstanceId=instance['InstanceId'], Name= amiName + " " + instance['InstanceId'] + " " + create_fmt, Description="Lambda created AMI of instance " + instance['InstanceId'] + " on " + create_fmt, NoReboot=True, DryRun=True)

            to_tag[retention_days].append(AMIid['ImageId'])
            amiList.append(AMIid['ImageId'])
            print("Retaining AMI %s of instance %s for %d days" % (AMIid['ImageId'],instance['InstanceId'],retention_days,))

    for retention_days in to_tag.keys():
        delete_date = datetime.date.today() + datetime.timedelta(days=retention_days)
        delete_fmt = delete_date.strftime('%m-%d-%Y')
        print("Will delete %d AMIs on %s" % (len(to_tag[retention_days]), delete_fmt))

        ec.create_tags(
            Resources=to_tag[retention_days],
            Tags=[
                {'Key': 'DeleteOn', 'Value': delete_fmt}
                #,
                #{'Key': 'Name', 'Value': 'yeni-test'}
            ]
        )

    snapshotMaster = []
    time.sleep(10)
    print(amiList)
    for ami in amiList:
        print(ami)
        snapshots = ec.describe_snapshots(DryRun=True, OwnerIds=[accountNumber],
            Filters=[
                {
                    'Name': 'description',
                    'Values': [
                        '*'+ami+'*'
                    ]
                }
            ]
        ).get(
            'Snapshots', []
        )
        print("****************")

        for snapshot in snapshots:
            print(snapshot['SnapshotId'])
            ec.create_tags(
                Resources=[snapshot['SnapshotId']],
                Tags=[
                    {'Key': 'DeleteOn', 'Value': delete_fmt}
                    #,
                    #{'Key': 'Name', 'Value': 'yeni-test'}
                ]
            )



lambda_handler()