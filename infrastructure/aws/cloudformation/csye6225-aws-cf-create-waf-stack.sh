#!/bin/bash

#Exit immediately if a command exits with a non-zero exit status.
set -e
##Get Load balacer ARN
LOADBALANCER=$(aws elbv2 describe-load-balancers | jq -c '.LoadBalancers[] | select(.LoadBalancerName == "csye6225LoadBalancer")' | jq -r '.LoadBalancerArn')

echo "ELBResourceARN: $LOADBALANCER"
##Creating Stack
echo "Creating Stack waf"
response=$(aws cloudformation create-stack --stack-name "waf" --template-body file://csye6225-cf-owasp.yaml --parameters ParameterKey=LOADBALANCER,ParameterValue=$LOADBALANCER) 
#response=$(aws cloudformation create-stack --stack-name "$1" --template-body file://csye6225-cf-networking.yaml)
echo "Waiting for Stack waf to be created"
echo "$response"
aws cloudformation wait stack-create-complete --stack-name "waf"
echo "Stack waf created successfully"

aws cloudformation describe-stack-resources --stack-name "waf"| jq '.StackResources' | jq -c '.[]' | jq '.PhysicalResourceId'