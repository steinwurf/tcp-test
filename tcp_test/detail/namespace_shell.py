class NamespaceShell(object):
    def __init__(self, name, shell):
        self.name = name
        self.shell = shell

    def run(self, cmd, cwd):
        """Run a command.
        :param cmd: The command to run
        :param cwd: The current working directory i.e. where the command will
            run
        """

        return self.shell.run(cmd=f"ip netns exec {self.name} {cmd}", cwd=cwd)

    async def run_async(self, cmd, cwd):
        """Run a command in a shell asynchronously.
        :param cmd: The command to run
        :param cwd: The current working directory i.e. where the command will
            run
        """

        return await self.shell.run_async(
            cmd=f"ip netns exec {self.name} {cmd}", cwd=cwd
        )
