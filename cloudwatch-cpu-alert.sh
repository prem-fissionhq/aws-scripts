#!/bin/bash

ids="i-04ad44a2fd761cc5b i-02eba7f6d9597360d i-0ab229ed1b22b346e i-0826361df8a2ee05e i-035bf567cf068881b i-0324e03ac3be00616 i-0fde9a8a0686206d5 i-0ace4cb860f69c273 i-0e8a1ff21de7860db i-0b18619583f167671"

for id in ${ids};
do 
	echo ${id}
	`aws cloudwatch put-metric-alarm --alarm-name CPUAlert_${id} --alarm-description "Alarm when CPU exceeds 70 percent" --metric-name CPUUtilization --namespace AWS/EC2 --statistic Average --period 300 --threshold 70 --comparison-operator GreaterThanThreshold  --dimensions "Name=InstanceId,Value=${id}" --evaluation-periods 3 --alarm-actions arn:aws:sns:us-east-2:783068214049:CloudWatch_Alarms_Topic --unit Percent --profile peopler`
done

