# create the virtualenv

  $ virtualenv venv > /dev/null 2>&1
  $ ls
  venv

# Assuming it worked, activate it

  $ . venv/bin/activate
  $ which python
  */test.t/venv/bin/python (glob)

#  Update pip, just in cases.

  $ pip install -U pip > /dev/null 2>&1
  $ which pip
  */test.t/venv/bin/pip (glob)

# Install dependencies of the auth-server-mock

  $ pip install bottle > /dev/null 2>&1

# Install cbas and check it worked

  $ pip install cbas > /dev/null 2>&1
  $ which cbas
  */test.t/venv/bin/cbas (glob)

# Get the ip of the docker0 interface

  $ DOCKER0_IP=$(ip addr | awk '/inet/ && /docker0/{sub(/\/.*$/,"",$2); print $2}')

# Create some predictable but uncommon port numbers

  $ export AUTH_PORT=8943
  $ export JUMP_HTTP_PORT=8762
  $ export JUMP_SSH_PORT=8228

# Export the AUTH_URL

  $ export AUTH_URL=http://$DOCKER0_IP:$AUTH_PORT

# start the auth-server-mock

  $ cp "$TESTDIR/auth_mock.py" .
  $ ./auth_mock.py > /dev/null 2>&1 &
  $ MOCK_PID=$!
  $ echo $MOCK_PID
  \d+ (re)

# Give it a second to come online

  $ sleep 1


# start the jump-host and detatch it immediately
# (Assuming it has been built etc...)

  $ container_id=$(docker run -d \
  > -p 127.0.0.1:$JUMP_HTTP_PORT:8080 \
  > -p 127.0.0.1:$JUMP_SSH_PORT:22 \
  > -e AUTH_URL=$AUTH_URL cbastion:latest)

# Give this 5 seconds to come online

  $ sleep 5

# Now, let's create a user

  $ ssh-keygen -t rsa -N "" -f integration_key > /dev/null 2>&1
  $ ls
  auth_mock.py
  integration_key
  integration_key.pub
  venv

# Use cbas to upload the key and create the user

  $ cbas -u integrationtestuser -p testing \
  > -k integration_key.pub \
  > -h localhost:$JUMP_HTTP_PORT \
  > -s client_secret \
  > -a http://localhost:$AUTH_PORT/oauth/token \
  > upload
  Will now attempt to obtain an JWT...
  Authentication OK!
  Access token was received.
  Will now attempt to upload your ssh-key...
  Upload OK!

# ssh into the jump host and check that users $HOME directory is there

  $ ssh localhost \
  > -p $JUMP_SSH_PORT \
  > -l integrationtestuser \
  > -i integration_key \
  > -o StrictHostKeyChecking=no \
  > -o PasswordAuthentication=no \
  > "ls /data/home"
  integrationtestuser

# Delete the user again with cbas

  $ cbas -u integrationtestuser -p testing \
  > -k integration_key.pub \
  > -h localhost:$JUMP_HTTP_PORT \
  > -s client_secret \
  > -a http://localhost:$AUTH_PORT/oauth/token \
  > delete
  Will now attempt to obtain an JWT...
  Authentication OK!
  Access token was received.
  Will now attempt to delete your user...
  Delete OK!

# Check that the user really has been deleted and can no longer log-in

  $ ssh localhost \
  > -p $JUMP_SSH_PORT \
  > -l integrationtestuser \
  > -i integration_key \
  > -o StrictHostKeyChecking=no \
  > -o PasswordAuthentication=no \
  > "ls /data/home"
  Permission denied (publickey,password).\r (esc)
  [255]

# Stop the docker host

  $ docker stop $container_id
  * (glob)

# kill the auth-server mock

  $ kill $MOCK_PID
