from .namespace_shell import NamespaceShell


class NetNS(object):
    def __init__(self, shell, ip_factory):
        self.shell = shell
        self.ip_factory = ip_factory

    def list(self):
        output = self.shell.run(cmd="ip netns list", cwd=None)
        names = []

        for line in output.splitlines():
            # The name is the first word followed by a space
            name = line.split(" ")[0]
            names.append(name)

        return names

    def delete(self, name):
        self.shell.run(cmd=f"ip netns delete {name}", cwd=None)

    def add(self, name):
        self.shell.run(cmd=f"ip netns add {name}", cwd=None)

        shell = NamespaceShell(name=name, shell=self.shell)
        return self.ip_factory(shell)
