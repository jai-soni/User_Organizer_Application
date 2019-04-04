# CSYE 6225 - Spring 2019

## Team Information

| Name | NEU ID | Email Address | Domain |
| --- | --- | --- | --- |
| Jai Soni| 001822913|soni.j@husky.neu.edu | csye6225-spring2019-sonij.me |
| Krapali Rai| 001813750 | rai.k@husky.neu.edu | csye6225-spring2019-raik.me. |
| Riddhi Kakadiya| 001811354 | kamlesh.r@husky.neu.edu | csye6225-spring2019-kamleshr.me |
| Sreerag Mandakathil Sreenath| 001838559| mandakathil.s@husky.neu.edu| csye6225-s19-mandakathils.me |


## Technology Stack
The web application is build on Django-python based server backend and uses MySql for the relational database

## System Setup

### First Time Dev Setup
You may use the initSetup.sh to install all the required libraries and to start server

```bash
cd csye6225-spring2019/webapp
source initSetup.sh -u YOURUSERNAME -p YOURPASSWORD -d YOURDBNAME
```
#### Actions performed by initSetup.sh
1. Installs all the required softwares
2. Installs and setup MySQL user and database
3. Creates the database configuration file and stores it into csye6225-spring2019/webapp/WebProject/WebProject/config/my.cnf
4. Creates django environment called djangoEnv in csye6225-spring2019/webapp/
5. Installs all the required libraries to djangoEnv
6. Activates the django environment
7. Performs all the required Django migrations
8. Starts the server

### Dev Setup
1. To run django server
Navigate to csye6225-spring2019/webapp folder and activate the django environment
```bash
cd csye6225-spring2019/webapp/WebProject
source djangoEnv/bin/activate
```
2. To start the server navigate to csye6225-spring2019/webapp/WebProject/

```bash
cd csye6225-spring2019/webapp/WebProject
python3 manage.py runserver
```

3. To stop server
```bash
press Ctrl+c
```

4. To deactivate environment
```bash
deactivate
```

#### Other common commands
1. To make database migrations, navigate to csye6225-spring2019/webapp/WebProject/

```bash
cd csye6225-spring2019/webapp/WebProject/
python3 manage.py makemigrations
python3 manage.py migrate
```

2. To create super user, navigate to csye6225-spring2019/webapp/WebProject/
```bash
cd csye6225-spring2019/webapp/WebProject/
python3 manage.py createsuperuser
```


## Build Instructions
Pre-requisites: 
- You need to have "Postman" installed
- User need to have two S3 buckets:
  e.g. for webapp: yourdomain.tld 
       for code deploy: code-deploy.yourdomain.tld  
  where yourdomain.tld should be replaced with your domain name

1. Clone the git repository.
2. Traverse to the folder /csye6225-spring2019/webapp

```bash
curl -u c18fdd17d3cbb353f7231e5e8f76cbc5d2bebdc1 -d build_parameters[CIRCLE_JOB]=build https://circleci.com/api/v1.1/project/github/sreeragsreenath/csye6225-spring2019/tree/assignment5
```


## Instruction To run application
1. Make Unauthenticated HTTP Request Execute following command on your bash shell

```bash
$ curl http://{EC2_hostname}
```
Message Response:

{"message":"you are not logged in!!!"}


2. Authenticate for HTTP Request Execute following command on your bash shell

```bash
$ curl -u user:password http://{EC2_hostname}
```

where user is the username and password is the password. Expected Response:

{"message":"you are logged in. current time is Thu Mar 14 12:03:49 EDT 2019"}

Execute following command on your bash shell

```bash
$ curl -u user:password http://{EC2_hostname}/user/register
```

where user is the username and password is the password. Expected Response:

Registered successfully

3. To reset the password, use execute following command on your bash shell:
```bash
$ curl http://{EC2_hostname}/reset
```

## Web End-points

num | request type | path | required variables |Authorization type |
| --- | --- | --- | --- | --- |
| 1 | GET | / | NA | No auth required |
| 2 | POST | /user/register | username:"", Password: "" | No auth required |
| 3 | POST | /note | title:"", content: "" | Basic auth required |
| 4 | GET | /note | NA | Basic auth required |
| 5 | GET | /note/id | NA | Basic auth required |
| 6 | DELETE | /note/id | NA | Basic auth required |
| 7 | PUT | /note/id | title:"", content: "" | Basic auth required |
| 8 | POST | /note/attachments | attachment: ("attach-file") | Basic auth required |
| 9 | PUT | /note/attachments/id | attachment: ("attach-new file") | Basic auth required
| 10 | GET | /note/attachments/id | NA | Basic auth required |
| 11 | DELETE | /note/attachments/id | NA | Basic auth required |
| 12 | POST | /reset | email: "" | Basic auth required |
 ________________________________________________________________________________________________


## Deploy Instructions


```bash
aws configure set region us-east-1 && aws deploy create-deployment --application-name csye6225-webapp --deployment-config-name CodeDeployDefault.AllAtOnce --deployment-group-name csye6225-webapp-deployment --description "My demo deployment" --s3-location bucket=$S3_BUCKET,bundleType=zip,key=webapp.zip 
```

## Running Tests

```bash
cd csye6225-spring2019/webapp/WebProject/
python3 manage.py test
```

## CI/CD
Any changes made to master branch will trigger a new build


## LAMDA function 
Prerequsites: 
--User need to have a verified domain name
--Need to request for SES sandbox


## Checking UDP port for statsd streaming

_**Note:**_
To begin, use the command '$tcpdump -D' to see which interfaces are available for capture:
```bash
sudo tcpdump -D
sudo tcpdump -i lo udp port 8125 -A
```
