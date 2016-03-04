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

  $ docker_ip=$(ip addr | awk '/inet/ && /docker0/{sub(/\/.*$/,"",$2); print $2}')

# Export the AUTH_URL

  $ export AUTH_URL=http://$docker_ip:8943

# start the auth-server-mock (on port 8943)

  $ cp "$TESTDIR/auth_mock.py" .
  $ ./auth_mock.py > /dev/null 2>&1 &
  $ MOCK_PID=$!
  $ echo $MOCK_PID
  \d+ (re)

# Give it a second to come online

  $ sleep 1


# start the jump-host and detatch it immediately
# (Assuming it has been built etc...)

  $ container_id=$(docker run -d -p 127.0.0.1:8080:8080 -e AUTH_URL=$AUTH_URL cbastion:latest)

# Give this 5 seconds to come online

  $ sleep 5

# Now, let's create a user

  $ ssh-keygen -t rsa -N "" -f integration_key > /dev/null 2>&1
  $ ls
  auth_mock.py
  integration_key
  integration_key.pub
  venv



  $ cbas -u  -p testing -k integration_key.pub -h localhost:8080 -s client_secret -a http://localhost:8080/oauth/token upload

# Stop the docker host

  $ docker stop $container_id
  * (glob)

# kill the auth-server mock

  $ kill $MOCK_PID
