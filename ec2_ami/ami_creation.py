# Script to take the AMI of ec2 instances based on tags. This script will find all the instances with tag 
# <tagName> = <TagValue> and will take the AMI of that. It will also put deleteOn date on AMI based on user defined 
# retention days, the same will be removed by CleanUp lambda function.

import boto3
import collections
import datetime
import os
import time
import logging
import itertools

#profile="some profile"
ec = boto3.client('ec2', region_name='ca-central-1')
print(ec)

#def lambda_handler(event, context):
def lambda_handler():
    accountNumber = "12345678900987" # aws account number 
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

    to_tag = collections.defaultdict(None)
    amiList = []
    ec2List = []
    for instance in instances:
        print(instance)
        try:
            retention_days = [int(t.get('Value')) for t in instance['Tags']
                if t['Key'] == 'Retention'][0]
            print("-----------------------",retention_days)
        except IndexError:

            retention_days = retentionDays
            print("dsfasdfsdd", retention_days)
            create_time = datetime.datetime.now()
            create_fmt = create_time.strftime('%Y-%m-%d-%H-%M-%S')

            for tag in instance['Tags']:
                if tag['Key'] == 'Name':
                    amiName = tag['Value']
                    break

            AMIid = ec.create_image(InstanceId=instance['InstanceId'], Name= amiName + " " + instance['InstanceId'] + " " + create_fmt, Description="Lambda created AMI of instance " + instance['InstanceId'] + " on " + create_fmt, NoReboot=True, DryRun=False)

            to_tag[AMIid['ImageId']] = retention_days
            amiList.append(AMIid['ImageId'])
            ec2List.append(amiName)
            print("Retaining AMI %s of instance %s for %d days" % (AMIid['ImageId'],instance['InstanceId'],retention_days,))
    print("234567890 ",to_tag.values(),ec2List)
    for amis,retention_days,ename in itertools.zip_longest(to_tag.keys(),to_tag.values(),ec2List):
        print(retention_days, ename)
        delete_date = datetime.date.today() + datetime.timedelta(days=retention_days)
        delete_fmt = delete_date.strftime('%m-%d-%Y')
        print("Will delete %d AMIs on %s" % (len(amis), delete_fmt))

        ec.create_tags(
            Resources=[amis],
            Tags=[
                {'Key': 'DeleteOn', 'Value': delete_fmt},
                {'Key': 'Name', 'Value': ename+"_"+str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))}
            ]
        )

    snapshotMaster = []
    time.sleep(10)
    print(amiList, ec2List)
    for (ami,ename) in itertools.zip_longest(amiList,ec2List):
        print(ami, ename)
        snapshots = ec.describe_snapshots(DryRun=False, OwnerIds=[accountNumber],
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
                    {'Key': 'DeleteOn', 'Value': delete_fmt},
                    {'Key': 'Name', 'Value': ename+"_"+str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))}
                ]
            )

lambda_handler()
