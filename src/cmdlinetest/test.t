# This is the integration test for c-bastion. Essentially the idea is to launch
# the docker container that contains the jump-host and check that it works.

# The auth-server is mocked and it was a bit tricky to have the auth-server
# running on the localhost and the jump-host running inside docker. The problem
# was that the jump-host must connect to the mocked auth-server from inside the
# docker container. This is achieved by telling the auth-server-mock to run on
# all interfaces (0.0.0.0) which means it is also running on the 'docker0'
# bridge interface, which is reachable from inside the docker container.
# The IP-adress of this interface is then used as the AUTH_URL for the
# jump-host.

# Make a test home

  $ mkdir test-home
  $ export HOME=test-home

# Hack to get the current project version.
# Use $TESTDIR to get the location of the cram test file, then use git to get
# the location of the build.py and finally execute pybuilder to get the project
# version from the authoritative location.

  $ TOPLEVEL=$( cd $TESTDIR && git rev-parse --show-toplevel )
  $ CURRENT_VERSION=$( cd $TOPLEVEL && pyb -Q project_version)

# Create the virtualenv

  $ virtualenv venv > /dev/null 2>&1
  $ ls
  test-home
  venv

# Assuming it worked, activate it

  $ . venv/bin/activate
  $ which python
  */test.t/venv/bin/python (glob)

#  Update pip, just in cases.

  $ pip install -U pip setuptools > /dev/null 2>&1
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

# Start the auth-server-mock

  $ cp "$TESTDIR/auth_mock.py" .
  $ ./auth_mock.py > /dev/null 2>&1 &
  $ MOCK_PID=$!
  $ echo $MOCK_PID
  \d+ (re)

# Give it a second to come online

  $ sleep 1

# Start the jump-host and detatch it immediately
# (Assuming it has been built etc...)

  $ container_id=$(docker run -d \
  > -p 127.0.0.1:$JUMP_HTTP_PORT:8080 \
  > -p 127.0.0.1:$JUMP_SSH_PORT:22 \
  > -e AUTH_URL=$AUTH_URL c-bastion:$CURRENT_VERSION)

# Give this 2 seconds to come online

  $ sleep 2

# Now, let's create a user

  $ ssh-keygen -t rsa -N "" -f integration_key > /dev/null 2>&1
  $ ls
  auth_mock.py
  integration_key
  integration_key.pub
  test-home
  venv

# Use cbas to upload the key and create the user

  $ cbas -u integrationtestuser -p testing \
  > -k integration_key.pub \
  > -h http://localhost:$JUMP_HTTP_PORT \
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
  > -o UserKnownHostsFile=/dev/null \
  > -o BatchMode=yes \
  > -q -T \
  > "ls /data/home"
  integrationtestuser

# ensure that /tmp only contains the bottle lock

  $ ssh localhost \
  > -p $JUMP_SSH_PORT \
  > -l integrationtestuser \
  > -i integration_key \
  > -o StrictHostKeyChecking=no \
  > -o PasswordAuthentication=no \
  > -o UserKnownHostsFile=/dev/null \
  > -o BatchMode=yes \
  > -q -T \
  > "ls /tmp"
  bottle*lock (glob)

# Check that calling the create endpoint again doesn't error

  $ cbas -u integrationtestuser -p testing \
  > -k integration_key.pub \
  > -h http://localhost:$JUMP_HTTP_PORT \
  > -a http://localhost:$AUTH_PORT/oauth/token \
  > upload
  Will now attempt to obtain an JWT...
  Authentication OK!
  Access token was received.
  Will now attempt to upload your ssh-key...
  Upload OK!

# Delete the user again with cbas

  $ cbas -u integrationtestuser -p testing \
  > -k integration_key.pub \
  > -h http://localhost:$JUMP_HTTP_PORT \
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
  > -o UserKnownHostsFile=/dev/null \
  > -o BatchMode=yes \
  > -q -T \
  > "ls /data/home"
  [255]

# Stop the docker host

  $ docker stop $container_id
  * (glob)

# Kill the auth-server mock

  $ kill $MOCK_PID
