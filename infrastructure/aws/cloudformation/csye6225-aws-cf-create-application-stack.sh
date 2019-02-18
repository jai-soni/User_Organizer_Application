#!/bin/bash

#Exit immediately if a command exits with a non-zero exit status.
set -e


##Check if enough arguements are passed
if [ $# -lt 1 ]; then
  echo "Please provide stack name ! Try Again."
  echo "e.g. ./csye6225-aws-cf-create-stack.sh <STACK_NAME>"
  exit 1
fi

# echo "The following are the regions available for creating VPC : "

# REGIONS=$(aws ec2 describe-regions | jq '.Regions')
# echo $REGIONS | jq -c '.[]'  | while read i; do
# 	REGION=$(echo $i | jq -r '.RegionName')
# 	    echo "$REGION"
# done

# echo ""
# echo "Lets first configure your AWS account"
# aws configure

##Creating Stack
echo "Creating Stack $1"
response=$(aws cloudformation create-stack --stack-name "$1" --template-body file://csye6225-cf-application.yaml --parameters file://csye-6225-cf-application-parameters.json)
#response=$(aws cloudformation create-stack --stack-name "$1" --template-body file://csye6225-cf-networking.yaml)
echo "Waiting for Stack $1 to be created"
echo "$response"
aws cloudformation wait stack-create-complete --stack-name $1
echo "Stack $1 created successfully"

aws cloudformation describe-stack-resources --stack-name $1| jq '.StackResources' | jq -c '.[]' | jq '.PhysicalResourceId'