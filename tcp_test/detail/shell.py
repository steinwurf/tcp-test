import subprocess


class Shell(object):
    """ A shell object for running commands """

    def __init__(self, log, sudo: bool):
        self.log = log
        self.sudo = sudo

    def run(self, cmd: str, cwd=None):
        """ Run a command.
        :param cmd: The command to run
        :param cwd: The current working directory i.e. where the command will
            run
        """

        if self.sudo:
            cmd = "sudo " + cmd

        self.log.debug(cmd)

        return subprocess.check_output(cmd, shell=True, cwd=cwd, text=True)
