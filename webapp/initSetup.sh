#!/bin/bash
#Run with sudo permisions
echo Setingup Dev environment

while getopts k:u:p:d: option
do
case "${option}"
in
k) test=${OPTARG};;
u) user=${OPTARG};;
p) password=${OPTARG};;
d) databasename=${OPTARG};;
esac
done

echo $user
echo $password
echo $databasename

cat > WebProject/WebProject/config/my.cnf << EOF
# my.cnf
[client]
database = $databasename
user = $user
password = $password
default-character-set = utf8
EOF

sudo apt-get update
sudo apt-get install python3 virtualenv python3-pip mysql-server python3-dev libmysqlclient-dev -y
cd WebProject
virtualenv -p python3 djangoEnv

sudo mysql <<EOF
SELECT user,authentication_string,plugin,host FROM mysql.user;
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '$password';
FLUSH PRIVILEGES;
CREATE USER '$user'@'localhost' IDENTIFIED BY '$password';
GRANT ALL PRIVILEGES ON *.* TO '$user'@'localhost' WITH GRANT OPTION;
SELECT user,authentication_string,plugin,host FROM mysql.user;
CREATE DATABASE $databasename;
EOF


sudo rm -rf djangoEnv
virtualenv -p python3 djangoEnv
source djangoEnv/bin/activate
pip3 install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver

exit

