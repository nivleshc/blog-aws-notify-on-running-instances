# blog-aws-notify-on-running-instances

This repository contains code for monitoring AWS EC2 instances and sending slack notifications when any running instances are found.

## Prerequisites
Before running the commands, export the following environment variables

```
export AWS_PROFILE_NAME={aws profile to use}

export AWS_S3_BUCKET_NAME={name of aws s3 bucket to store SAM artefacts}

export SLACK_WEBHOOK_URL={slack webhook url to use for sending slack notifications}
```

## Commands

To deploy the code in this repo, use the following steps

```
make package
make deploy
```

If you make any changes to **template.yaml** then use the following command to validate it
```
make validate
```

After successful validation, use the following command to deploy the changes
```
make update
```
