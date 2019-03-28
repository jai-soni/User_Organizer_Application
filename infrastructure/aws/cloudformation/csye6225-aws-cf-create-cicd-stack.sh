#!/bin/bash

AWS_ACCOUNT_ID=$(aws sts get-caller-identity | jq -r '.Account')
AWS_REGION="us-east-1"
CODE_DEPLOY_APPLICATION_NAME="csye6225-webapp"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity | jq -r '.Account')
S3_BUCKET=$(aws s3api list-buckets | jq -r '.Buckets[] | select(.Name | startswith("code-deploy")).Name')
LAMBDA_BUCKET=$(aws s3api list-buckets | jq -r '.Buckets[] | select(.Name | startswith("lambda")).Name')

aws cloudformation create-stack --stack-name "$1" --template-body file://csye-6225-cf-cicd.yaml --capabilities CAPABILITY_NAMED_IAM --parameters ParameterKey=AWSAccountId,ParameterValue=$AWS_ACCOUNT_ID ParameterKey=CodeDeployApplicationName,ParameterValue=$CODE_DEPLOY_APPLICATION_NAME ParameterKey=AWSRegion,ParameterValue=$AWS_REGION ParameterKey=S3BucketNameCD,ParameterValue=$S3_BUCKET ParameterKey=LambdaBucketNameCD,ParameterValue=$LAMBDA_BUCKET

echo "Waiting for Stack $1 to be created"
echo "$response"
aws cloudformation wait stack-create-complete --stack-name $1
echo "Stack $1 created successfully"

if [ $? = "0" ]
then
	aws iam create-access-key --user-name circleci
else
	echo "Error : Creating user"
	exit
fi
echo "Webapp Bucket Name : "
echo $S3_BUCKET

echo "Lambda Bucket Name : "
echo $LAMBDA_BUCKET