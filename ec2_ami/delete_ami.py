# This script will Cleanup the Older AMI of instances based on their deleteOn tags.

import boto3
import datetime
import os
import time

accountNumber = "12345678987654" #os.environ['AWS_ACCOUNT_NUMBER']

ec = boto3.client('ec2', 'ca-central-1')

#def lambda_handler(event, context):
def lambda_handler():

    imagesResponse = ec.describe_images(
        DryRun=False,
        Owners=[accountNumber],
        Filters=[
            {'Name': 'tag-key', 'Values': ['DeleteOn']}
        ]
    ).get(
        'Images', []
    )

    amiList = []
    currentDate = datetime.datetime.now().strftime('%m-%d-%Y-%H-%M-%S')
    time.sleep(5)
    print(imagesResponse)
    for image in imagesResponse:
        deleteOn = ''
        for tag in image['Tags']:
            if tag['Key'] == 'DeleteOn':
                deleteOn = tag['Value']
                break
        if deleteOn == '':
            continue
        if deleteOn <= currentDate:
            print("\nCleaning up AMI %s" % (image['ImageId']))
            ec.deregister_image(
                DryRun=True,
                ImageId=image['ImageId']
            )
            amiList.append(image['ImageId'])
            snapshots = ec.describe_snapshots(
                DryRun=True,
                OwnerIds=[
                    accountNumber
                ],
                Filters=[
                    {
                        'Name': 'description',
                        'Values': [
                            '*'+image['ImageId']+'*'
                        ]
                    }
                ]
            ).get(
                'Snapshots', []
            )
            for snapshot in snapshots:
                print(">>Cleaning up Snapshot %s" % (snapshot['SnapshotId']))
                time.sleep(5)
                ec.delete_snapshot(
                    DryRun = False,
                    SnapshotId = snapshot['SnapshotId']
                )
        else:
            print("\n%s not yet scheduled for cleanup" % (image['ImageId']))
    if len(amiList)==0:
        print("\n\nNo AMIs were deleted")
    else:
        print("\n\n%d AMIs were deleted\nDeleted the following:" %(len(amiList)))
        for ami in amiList:
            print(ami)

lambda_handler()
