class iPerfShell(object):
    def __init__(self, shell):
        self.shell = shell

    def run(self, cmd, cwd):
        """Run a command.
        :param cmd: The command to run
        :param cwd: The current working directory i.e. where the command will
            run
        """

        return self.shell.run(cmd=f"iperf {cmd}", cwd=cwd)

    async def run_async(self, cmd, daemon=False, delay=0, cwd=None):
        """Run a command in a shell asynchronously.
        :param cmd: The command to run
        :param cwd: The current working directory i.e. where the command will
            run
        """

        await self.shell.run_async(
            cmd=f"iperf3 {cmd}",
            daemon=daemon,
            delay=delay,
            cwd=cwd,
        )
