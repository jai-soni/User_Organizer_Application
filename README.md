# CSYE 6225 - Spring 2019

## Team Information

| Name | NEU ID | Email Address |
| --- | --- | --- |
| Jai Soni| 001822913|soni.j@husky.neu.edu |
| Krapali Rai| 001813750 | rai.k@husky.neu.edu |
| Riddhi Kakadiya| 001811354 | kamlesh.r@husky.neu.edu |
| Sreerag Mandakathil Sreenath| 001838559| mandakathil.s@husky.neu.edu|


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
cd csye6225-spring2019/webapp
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

## To run test

```bash
cd csye6225-spring2019/webapp/WebProject/
python3 manage.py test
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
Pre-requisites: You need to have "Postman" installed

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


## Deploy Instructions


```bash
aws configure set region us-east-1 && aws deploy create-deployment --application-name csye6225-webapp --deployment-config-name CodeDeployDefault.OneAtATime --deployment-group-name csye6225-webapp-deployment --description "My demo deployment" --s3-location bucket=$S3_BUCKET,bundleType=zip,key=webapp.zip 
```

## Running Tests


## CI/CD


