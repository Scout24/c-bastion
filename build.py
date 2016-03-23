import os

from pybuilder.core import use_plugin, init, Author, task, depends
from pybuilder.vcs import VCSRevision

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")
use_plugin("python.cram")
use_plugin("filter_resources")

name = 'c-bastion'
version = VCSRevision().get_git_revision_count()
summary = 'Cloud Bastion Host'
authors = [
    Author('Sebastian Spoerer', "sebastian.spoerer@immobilienscout24.de"),
    Author('Valentin Haenel', "valentin.haenel@immobilienscout24.de"),
    Author('Tobias Hoeynck', "tobias.hoeynck@immobilienscout24.de"),
    Author('Laszlo Karolyi', "laszlo@karolyi.hu"),
]
url = 'https://github.com/ImmobilienScout24/c-bastion'

default_task = "analyze"

docker_name = 'run-c-bastion-run'

@init
def initialize(project):
    project.depends_on("paste")
    project.depends_on('sh')
    project.depends_on("bottle")
    project.depends_on("request")
    project.depends_on("boto3")
    project.depends_on("pyyaml")

    project.build_depends_on("unittest2")
    project.build_depends_on("requests_mock")
    project.build_depends_on('mock')

    project.get_property('filter_resources_glob').extend(
        ['**/c_bastion/__init__.py'])


def docker_execute(command_list, logger):
    """ Run and tail a docker command. """
    import sh
    try:
        running_command = sh.docker(command_list, _iter=True)
        for line in running_command:
            logger.info(line.strip())
    except KeyboardInterrupt:
        logger.info("Requested to terminate running docker command.")
        running_command.process.terminate()


@task
def docker_run(project, logger):
    logger.info("Running the docker image.")
    AUTH_URL = os.environ['AUTH_URL']
    docker_execute(['run',
                    '-p', '8080:8080',
                    '-p', '2222:2222',
                    '-e', 'AUTH_URL={0}'.format(AUTH_URL),
                    '--name', docker_name,
                    'c-bastion:latest',
                    ], logger)


@task
@depends("package")
@depends("clean")
def docker_build(project, logger):
    logger.info("Building the docker image.")
    docker_execute(['build', '-t', 'cbastion', '.'], logger)


@task
@depends('run_cram_tests')
@depends('docker_build')
def system_tests():
    pass


@task
@depends('publish')
@depends('docker_build')
def all():
    pass
