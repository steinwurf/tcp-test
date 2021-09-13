class RelyTunnel(object):
    def __init__(
        self,
        shell,
        rely_path,
    ):
        self.shell = shell
        self.path = rely_path

    def start_tunnel(
        self, name, tunnel_ip, tunnel_in, tunnel_out, packet_size, cwd=None
    ):
        self.shell.run(
            cmd=f"{self.path} add tun --id {name} --tun-name {name} --packet-size {packet_size} --tunnel-in {tunnel_in} --tunnel-out {tunnel_out} --tun-ip {tunnel_ip}",
            cwd=cwd,
        )
        self.shell.run(cmd=f"{self.path} {name} start", cwd=cwd)

    def set_repair(self, name, repair_interval=5, repair_target=1, cwd=None):

        cmd = f"{self.path} {name} set_repair {repair_interval} {repair_target}"

        self.shell.run(cmd=cmd, cwd=cwd)

    def set_encoder_timeout(self, name, timeout=60, cwd=None):

        cmd = f"{self.path} {name} set_encoder_timeout {timeout}"

        self.shell.run(cmd=cmd, cwd=cwd)

    def set_decoder_timeout(self, name, timeout=60, cwd=None):

        cmd = f"{self.path} {name} set_decoder_timeout {timeout}"

        self.shell.run(cmd=cmd, cwd=cwd)

    def terminate(self, cwd=None):
        self.shell.run(f"{self.path} terminate", cwd=cwd)
