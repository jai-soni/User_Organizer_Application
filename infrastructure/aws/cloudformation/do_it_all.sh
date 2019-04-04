
EC2KEY="cloud-sree"
USERNAME="sreeragsreenath"
BRANCH="assignment8"
TOKEN="c18fdd17d3cbb353f7231e5e8f76cbc5d2bebdc1"

./create_network_application.sh network webapp $EC2KEY

./csye6225-aws-cf-create-serverless-stack.sh

curl -u $TOKEN: -d build_parameters[CIRCLE_JOB]=build https://circleci.com/api/v1.1/project/github/$USERNAME/csye6225-spring2019/tree/$BRANCH

curl -u $TOKEN: -d build_parameters[CIRCLE_JOB]=build https://circleci.com/api/v1.1/project/github/$USERNAME/csye6225-spring2019-lambda/tree/$BRANCH




