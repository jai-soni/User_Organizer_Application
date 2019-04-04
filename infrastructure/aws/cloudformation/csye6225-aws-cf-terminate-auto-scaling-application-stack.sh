#!/bin/bash


# echo "The following are the regions available for deleting stacks : "

# REGIONS=$(aws ec2 describe-regions | jq '.Regions')
# echo $REGIONS | jq -c '.[]'  | while read i; do
#   REGION=$(echo $i | jq -r '.RegionName')
#       echo "$REGION"
# done

# echo "Lets first configure your AWS account"
# aws configure

StackList=$(aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_IN_PROGRESS CREATE_IN_PROGRESS --query 'StackSummaries[].StackName' --output text )

if [[ -z "$StackList" ]]
then
  echo " Empty Stack List!"
  exit 1
else
  echo "Available stacks :"
  echo $StackList
  echo "Enter Stack name to be deleted"
  read StackName
fi

#Check if user has entered correct Stack Name
flag=0

# if [[ stacknameLen -eq stacklistlen ]]
#   then
    if [[ " ${StackList[*]} " = *$StackName* ]]; then
          flag=1
      else
        echo "Invalid parameter provided, please input again"
    fi
#fi
    if [ $flag == 0 ]
      then
        echo "Error: Invalid StackName - $StackName"
        exit
    fi
echo "Deleting Stack $StackName"
ResponseDelete=$(aws cloudformation delete-stack --stack-name $StackName)
if [ $? -ne "0" ]
then
  echo "$StackName stack is not deleted....."
  echo "$ResponseDelete"
  exit 1
else
  echo "Stack deletion is in process! Please wait!"
fi

ResponseSuccess=$(aws cloudformation wait stack-delete-complete --stack-name $StackName)
if [[ -z "$Success" ]]
then
  echo "Stack $StackName is deleted successfully"
else
  echo "Failed to delete stack $StackName ! Please try again!"
  echo "$ResponseSuccess"
  exit 1
fi

