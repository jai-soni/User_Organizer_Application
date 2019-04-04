#!/bin/bash

#Exit immediately if a command exits with a non-zero exit status.
set -e
##Check if enough arguements are passed
if [ $# -lt 1 ]; then
  echo "Please provide network stack name ! Try Again."
  echo "e.g. ./csye6225-aws-cf-create-stack.sh <NETWORK_STACK> <STACK_NAME> <KEY_PAIR>"
  exit 1
fi

if [ $# -lt 2 ]; then
  echo "Please provide application stack name ! Try Again."
  echo "e.g. ./csye6225-aws-cf-create-stack.sh <NETWORK_STACK> <STACK_NAME> <KEY_PAIR>"
  exit 1
fi

if [ $# -lt 3 ]; then
  echo "Please provide Key Pair ! Try Again."
  echo "e.g. ./csye6225-aws-cf-create-stack.sh <NETWORK_STACK> <STACK_NAME> <KEY_PAIR>"
  exit 1
fi

IMAGE_ID=$(aws ec2 describe-images --owners self --query 'sort_by(Images, &CreationDate)[].ImageId' | jq -r '.[0]')

S3_BUCKET=$(aws s3api list-buckets | jq -r '.Buckets[] | select(.Name | startswith("csye6225")).Name')

S3_BUCKET_CD=$(aws s3api list-buckets | jq -r '.Buckets[] | select(.Name | startswith("code-deploy")).Name')

./csye6225-aws-cf-create-stack.sh $1

# ./csye6225-aws-cf-create-application-stack.sh $2 $1 $IMAGE_ID $3 $S3_BUCKET $S3_BUCKET_CD

# ./csye6225-aws-cf-create-cicd-stack.sh $3
./csye6225-aws-cf-create-auto-scaling-application-stack.sh $2 $1 $IMAGE_ID $3 $S3_BUCKET $S3_BUCKET_CD
