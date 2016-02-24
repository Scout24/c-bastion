#!/bin/bash

# This is a transient, ultra hacky shell script for quick and dirty
# exploration. Please delete it at your earliest convenience!!11!!

ssh_key=$(cat ~/.ssh/id_rsa.pub)
username=$1
jump_host_prefix=$2

echo "ssh_key: " $ssh_key
echo "username: " $username
echo "jump host: " $jump_host_prefix


if [ -z $jump_host_prefix ] || [ -z $username ] ; then
    echo "usage: test.sh <username> <jump_host_prefix>"
    exit 1
fi

CLIENT_SECRET='change-me'

echo -n "Password: "
read -s password
echo ""
echo "Get Token ..."

access_token=$(curl -s -X POST -d "client_id=jumpauth" -d "client_secret=$CLIENT_SECRET" -d "username=$username" -d "password=$password" -d "grant_type=password" https://<your-auth-server>/ | jq -r '.access_token')

echo $access_token

curl -X POST -H "Authorization: Bearer $access_token" -H "Content-Type: application/json" -H "Cache-Control: no-cache" -d "{
    \"pubkey\": \"$ssh_key\"
}" "$jump_host_prefix/create"
