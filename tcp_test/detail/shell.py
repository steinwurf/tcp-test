import subprocess
import asyncio


class Shell(object):
    """A shell object for running commands"""

    def __init__(self, log, sudo: bool):
        self.log = log
        self.sudo = sudo

    def run(self, cmd: str, cwd=None):
        """Run a command.
        :param cmd: The command to run
        :param cwd: The current working directory i.e. where the command will
            run
        """

        if self.sudo:
            cmd = "sudo " + cmd

        self.log.debug(cmd)
        return subprocess.check_output(cmd, shell=True, cwd=cwd, text=True)

    async def run_async(self, cmd: str, is_daemon=False):
        """Run an asynchronous command.
        :param cmd: The command to run
        :param cwd: The current working directory i.e. where the command will
            run
        """

        if self.sudo:
            cmd = "sudo " + cmd

        self.log.debug(cmd)

        proc = await asyncio.create_subprocess_shell(
            cmd=cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        # One way of printing dynamically with async processes:
        try:
            while True:
                if is_daemon:
                    # Just print whenever output is available
                    line = await asyncio.wait_for(proc.stdout.readline(), None)
                else:
                    # Wait 10 seconds at most for a line
                    line = await asyncio.wait_for(proc.stdout.readline(), 10)

                print(line)

        except asyncio.TimeoutError as e:
            print(f"The command '{cmd}' timed out")
