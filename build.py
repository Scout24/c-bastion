from pybuilder.core import use_plugin, init, Author
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
