class Session(object):
    def __init__(self, client_factory, server_factory):
        self.client_factory = client_factory
        self.server_factory = server_factory

    def run(self, log, client_config, server_config):

        # Build the client and server from the configs

        client = self.client_factory(log=log, **client_config)
        server = self.server_factory(log=log, **server_config)

        server.run()
        result = client.run()

        return result
