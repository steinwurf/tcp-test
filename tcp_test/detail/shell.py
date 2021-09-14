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

    async def run_async(self, cmd: str, daemon=False, delay=0, cwd=None):
        """Run an asynchronous command.
        :param cmd: The command to run
        :param cwd: The current working directory i.e. where the command will
            run
        """
        task = asyncio.current_task()
        task.cmd = cmd
        task.daemon = daemon

        if delay > 0:
            self.log.debug(f"Waiting {delay} seconds")
            await asyncio.sleep(delay)

        if self.sudo:
            cmd = "sudo " + cmd

        self.log.debug("Running " + cmd)

        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=cwd
        )

        self.log.debug("Launched")

        try:
            stdout, stderr = await proc.communicate()
        except asyncio.exceptions.CancelledError:
            if daemon:
                self.log.debug("Deamon shutting down")
            else:
                raise

        else:

            self.log.debug(f"[{cmd!r} exited with {proc.returncode}]")
            if stdout:
                self.log.info(f"[stdout]\n{stdout.decode()}")
            if stderr:
                self.log.info(f"[stderr]\n{stderr.decode()}")

            if daemon:
                raise RuntimeError("Deamon exit prematurely")

            if proc.returncode != 0:
                raise RuntimeError(f"{cmd} failed with exit code {proc.returncode}")
