#!/bin/bash

ip netns add server
ip netns add client

ip link add server_link type veth peer name client_link

ip link set 'server_link' netns 'server'
ip link set 'client_link' netns 'client'

ip netns exec server ip addr add 10.0.0.1/24 dev server_link
ip netns exec client ip addr add 10.0.0.2/24 dev client_link

ip netns exec server ip link set dev server_link up
ip netns exec client ip link set dev client_link up

ip netns exec server ip link set dev lo up
ip netns exec client ip link set dev lo up
