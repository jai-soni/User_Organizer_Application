# CSYE 6225 - Spring 2019

## AWS CLI Scripts and Cloudformation Templates
This folder contains the shell scripts and Templates used to create and teardown an stack.

### Architecture 
The architecture contains networking resources such as Virtual Private Cloud (VPC), Internet Gateway, Route Table and Routes.

#### InfraStructure Setup

1. Create a Virtual Private Cloud (VPC) resource called STACK_NAME-csye6225-vpc.
2. Create subnets in your VPC. You must create 3 subnets, each in different availability zone in the same region under same VPC.
3. Create Internet Gateway resource.
4. Attach the Internet Gateway to STACK_NAME-csye6225-vpc VPC.
5. Create a public Route Table called STACK_NAME-csye6225-rt. Attach all subnets created above to the route table.
6. Create a public route in STACK_NAME-csye6225-rt route table with destination CIDR block 0.0.0.0/0 and the internet gateway as the target.
7. Modify the default security group for your VPC to remove existing rules and add new rules to only allow TCP traffic on port 22 and 80 from anywhere. No longer a requirement.

### Executing the scripts
#### To Create a Network Stack


```bash
cd csye6225-spring2019/infrastructure/aws/cloudformation/
./csye6225-aws-cf-create-stack.sh <STACK_NAME>
```
Example:

```bash
cd csye6225-spring2019/infrastructure/aws/cloudformation/
./csye6225-aws-cf-create-stack.sh MyStack
```

The example code will setup a stack named 'MyStack'. The paramaters required for the script can be configured in 'csye-6225-cf-networking-parameters.json'.

#### To Terminate a Network Stack

```bash
cd csye6225-spring2019/infrastructure/aws/cloudformation/
./csye6225-aws-cf-terminate-stack.sh
```

The above code will list available stacks and ask for the STACK_NAME to be deleted.


#### To Create a Application Stack

```bash
cd csye6225-spring2019/infrastructure/aws/cloudformation/
./csye6225-aws-cf-create-application-stack.sh <STACK_NAME>
```
Example:

```bash
cd csye6225-spring2019/infrastructure/aws/cloudformation/
./csye6225-aws-cf-create-application-stack.sh MyAppStack
```

The example code will setup a stack named 'MyAppStack'. The paramaters required for the script can be configured in 'csye-6225-cf-application-parameters.json'.

#### To create network and application stack using single script

```bash
cd csye6225-spring2019/infrastructure/aws/cloudformation/
./csye6225-aws-cf-create-stack
```
#### To create CICD stack

```bash
cd csye6225-spring2019/infrastructure/aws/cloudformation/
./csye6225-aws-cf-create-cicd-stack
```


#### To create network and application stack using single script along with the load balancer and Auto-scaling enabled

```bash
cd csye6225-spring2019/infrastructure/aws/cloudformation/
./create_network_application.sh
```

#### To create serverless stack

```bash
cd csye6225-spring2019/infrastructure/aws/cloudformation/
./csye6225-aws-cf-create-serverless-stack.sh
```

#### To Terminate a Application Stack

```bash
cd csye6225-spring2019/infrastructure/aws/cloudformation/
./csye6225-aws-cf-terminate-application-stack.sh
```


#### To Terminate a network and application stack using single script

```bash
cd csye6225-spring2019/infrastructure/aws/cloudformation/
./csye6225-aws-cf-terminate-stack.sh
```

#### To Terminate a CICD stack

```bash
cd csye6225-spring2019/infrastructure/aws/cloudformation/
./csye6225-aws-cf-terminate-cicd.sh
```

#### To trigger a build in CircleCI

Requires : 
CircleCI API Token, 
URL of repository

```bash
cd csye6225-spring2019/infrastructure/aws/cloudformation/
./trigger_build.sh
```


The above code will list available stacks and ask for the STACK_NAME to be deleted.

