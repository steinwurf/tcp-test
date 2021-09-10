import re


class IP(object):
    def __init__(self, shell):
        self.shell = shell

    def link_veth_add(self, p1_name, p2_name):
        self.shell.run(
            cmd=f"ip link add {p1_name} type veth peer name {p2_name}", cwd=None
        )

    def link_set(self, namespace, interface):
        self.shell.run(cmd=f"ip link set {interface} netns {namespace}", cwd=None)

    def link_list(self):
        output = self.shell.run(cmd="ip link list", cwd=None)

        parser = re.compile(
            """
            \d+             # Match one or more digits
            :               # Followed by a colon
            \s              # Followed by a space
            (?P<name>[^:@]+)# Match all but : or @ (group "name")
            [:@]            # Followed by : or @
            .               # Followed by anything :)
        """,
            re.VERBOSE,
        )

        names = []

        for line in output.splitlines():
            # The name is the first word followed by a space
            result = parser.match(line)

            if result == None:
                continue

            names.append(result.group("name"))

        return names

    def link_delete(self, interface):
        self.shell.run(cmd=f"ip link delete {interface}", cwd=None)

    def addr_add(self, ip, interface):
        self.shell.run(f"ip addr add {ip} dev {interface}", cwd=None)

    def up(self, interface):
        self.shell.run(f"ip link set dev {interface} up", cwd=None)

    def route(self, ip):
        self.shell.run(f"ip route add default via {ip}", cwd=None)

    def run(self, cmd, cwd):
        return self.shell.run(cmd=cmd, cwd=cwd)

    async def run_async(self, cmd, daemon=False, delay=0):
        await self.shell.run_async(cmd=cmd, daemon=daemon, delay=delay)

    def tc_show(self, interface, cwd=None):
        return self.shell.run(cmd=f"tc qdisc show dev {interface}", cwd=cwd)

    def tc(self, interface, delay=None, loss=None, cwd=None):
        output = self.tc_show(interface=interface, cwd=cwd)
        if "netem" in output:
            action = "change"
        else:
            action = "add"
        cmd = f"tc qdisc {action} dev {interface} root netem "
        if delay:
            cmd += f"delay {delay}ms "
        if loss:
            cmd += f"loss {loss}%"
        self.shell.run(cmd=cmd, cwd=cwd)

    def tc_loss(self, interface, loss, cwd=None):
        output = self.tc_show(interface=interface, cwd=cwd)
        if "netem" in output:
            action = "change"
        else:
            action = "add"
        self.shell.run(
            cmd=f"tc qdisc {action} dev {interface} root netem loss {loss}%", cwd=cwd
        )

    def forward(self, from_interface, to_interface):
        self.shell.run(
            f"iptables -A FORWARD -o {from_interface} -i {to_interface} -j ACCEPT",
            cwd=None,
        )

    def nat(self, ip, interface):
        self.shell.run(
            f"iptables -t nat -A POSTROUTING -s {ip} -o {interface} -j MASQUERADE",
            cwd=None,
        )
