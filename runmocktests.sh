#!/usr/bin/env bash
echo "Hello this is first attempt to run linchpin provisioning in github actions"

linchpin --version;

mkdir /tmp/workspace/;

cd /tmp/workspace/;

echo $PWD;

locale -a;

echo $LC_ALL;
export $LANG;

echo "RUNNING AWS MOCK TESTS";

linchpin init aws;
cd aws;
linchpin -vvvv up;
