from pybuilder.core import use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")


name = "jump_auth"
default_task = "publish"


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

    project.set_property('coverage_break_build', False)
