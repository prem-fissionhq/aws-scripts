The Script `ami_creation.py` will create ami's of the instances which has Tag named `Backup=true`. The script will also going to add proper tags to the ami's and snapshots with the deleteOn_tag which has a date of deletion tagged to it.

The Script `delete_ami.py` will delete all the ami's which has tag named `deleteOn` and value is LessThanOrEqualTo CurrentDate.