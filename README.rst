====================================================
`c-bastion` -- Cloud Bastion Host (a.k.a. jump-host)
====================================================

About
-----

``c-bastion`` allows you to create users in a docker container via a CLI tool
called ``cbas``, and then log in with these formerly created users.

The purpose of this project is to provide an EC2 instance with a Docker
container that can be used as a jump-host with dynamically created user. After
creation, the user is able to log in into the Docker container by using his/her
given SSH key.

The repo holds a ``test-stacks.yml`` file to create an AWS CFN stack with using
an EC2 instance with ``taupage``, in which a Docker container is set up to serve
as the jump-host. Make sure to edit both the ``test-stacks.yml`` and
``template.yml`` (included by the former) before syncing it. The templates are in
YAML format, understood by ``cfn-sphere``.

Architecture
------------

This project 

Configuration
-------------

There is a single configuration the URL of the auth-server

Local Testing
-------------

Cloud Deployment
----------------

Deployment process

- clone this repository

Docker ECR deployment:

- `VERSION=<version-number>`
- `IMAGE_NAME="your-preferred-image-name"`
- `REPO="123456789012.dkr.ecr.us-east-1.amazonaws.com"`
- `docker build -t "$IMAGE_NAME:$VERSION" .`
- `docker tag "$IMAGE_NAME:$VERSION" "$REPO/$IMAGE_NAME:$VERSION"`
- `docker tag "$IMAGE_NAME:$VERSION" "$REPO/$IMAGE_NAME:latest"`
- `docker push "$REPO/$IMAGE_NAME"`

Test the project:
- create your virtualenv and activate it
- `pip install cfn-sphere pybuilder`
- `pyb install_dependencies`
- `pyb -v`

Create/sync your AWS CFN stack:

- edit `test-stacks.yml` and `template.yml` to fit your needs
- sync the stack with `cf sync --confirm --parameter <your-preferred-stack-name>.dockerImageVersion=$VERSION test-stacks.yml`

A quick&dirty test script is provided in `test.sh`. The script AND the project uses an auth server. Change it in `oidc.py` and `test.sh` to use your own.

