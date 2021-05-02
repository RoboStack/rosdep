# Copyright (c) 2021, Tobias Fischer
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Willow Garage, Inc. nor the names of its
#       contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Author Tobias Fischer/info@tobiasfischer.info
import subprocess

from rospkg.os_detect import OS_ROBOSTACK

from ..installers import PackageManagerInstaller

CONDA_INSTALLER = 'conda'


def is_mamba_installed():
    try:
        subprocess.Popen(['mamba'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        return True
    except OSError:
        return False


def register_installers(context):
    context.set_installer(CONDA_INSTALLER, CondaInstaller())


def register_platforms(context):
    context.add_os_installer_key(OS_ROBOSTACK, CONDA_INSTALLER)
    context.set_default_os_installer_key(OS_ROBOSTACK, lambda self: CONDA_INSTALLER)


def conda_detect_single(p):
    return not subprocess.call(['conda', 'list', '-c', '-f', p], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def conda_detect(packages):
    return [p for p in packages if conda_detect_single(p)]


class CondaInstaller(PackageManagerInstaller):
    def __init__(self):
        super(CondaInstaller, self).__init__(conda_detect)

    def get_install_command(self, resolved, interactive=True, reinstall=False, quiet=False):
        packages = self.get_packages_to_install(resolved, reinstall=reinstall)
        if not packages:
            return []
        if is_mamba_installed:
            installer_cmd = 'mamba'
        else:
            installer_cmd = 'conda'
        base_cmd = [installer_cmd, 'install']
        if not interactive:
            base_cmd.append('-y')
        if quiet:
            base_cmd.append('-q')
        if reinstall:
            base_cmd.append('--force-reinstall')

        return [base_cmd + packages]

    def get_version_strings(self):
        return subprocess.check_output(('conda', '--version'))
