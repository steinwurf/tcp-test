from pyroute2 import netns

# fmt: off
def setup_ns():
    current_namespaces = netns.listnetns()

    if 'server' in current_namespaces or 'client' in current_namespaces:
        netns.remove('client')
        netns.remove('server')

    netns.create('client')
    netns.create('server')

    print(netns.listnetns())

    netns.remove('client')
    netns.remove('server')
# fmt: on

if __name__ == "__main__":
    setup_ns()
