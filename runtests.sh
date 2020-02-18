#!/usr/bin/env bash
echo "Hello this is first attempt to run bash script on github actions"
OS=$(cat /etc/*release | grep ^NAME | tr -d 'NAME="') 
ID=$(cat /etc/*release | grep ^ID | tr -d 'ID="') 
VERSION_ID=$(cat /etc/*release | grep ^VERSION_ID | tr -d 'VERSION_ID="') 

echo $OS
echo $ID
echo $VERSION_ID

if [ $VERSION_ID = "8" ]
then
    echo "This is centos8";
    yum install -y python3 epel-release which git;
    yum install -y python3-pip python3-flake8 python3-devel gcc;
elif [ $VERSION_ID = "7" ]
then
    echo "This is centos7";
    yum install -y python3 epel-release which git;
    yum install -y python-pip python3-pip python3-devel gcc;
    pip install flake8;
else
    echo "This is fedora"
    dnf install -y python3 git;
    dnf install -y python3-pip python3-flake8 python3-devel gcc which;
fi
