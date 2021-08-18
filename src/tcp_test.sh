#!/bin/bash
# Fail hard and fast if any intermediate command pipeline fails
set -e

usage="$(basename "$0") [-help] [-mode] [-tries p] [-serverdelay m]
                        [-clientdelay n] [-throughput t] [-rely bool]
       -- program to simulate TCP transfer with Server-Client setup

where the arguments are:
    -mode         choose to either plot a histogram of added  (default: hist)
                  latency with -mode hist or collect samples of
                  average throughput for the given parameters (throughput).

    -tries        set the number of packets to transfer       (default: 1000)

    -serverdelay  set the delay value from server to client   (default: 60ms)
    (shortcut: -sd)

    -clientdelay  set the delay value from client to server   (default: 60ms)
    (shortcut: -cd)

    -throughput   set the throughput from server to client    (default: 1MB/s)
    (shortcut: -tp)

    -rely         simulates using rely if true                (default: false)

    -help         display this help section
    (shortcut: -h)
"

# Default options:
mode=histogram
tries=2000
serverdelay=60
clientdelay=60
throughput=1
rely=false

while [ "$1" != "" ]; do
   case $1 in
      -mode)
         shift
         mode=$1
         ;;

      -tries)
         shift
         tries=$1
         ;;

      -sd | -serverdelay)
         shift
         serverdelay=$1
         ;;

      -cd | -clientdelay)
         shift
         clientdelay=$1
         ;;

      -tp | -throughput)
         shift
         throughput=$1
         ;;

      -rely)
         shift
         rely=$1
         ;;
      -h | -help)
         echo "$usage"
         exit
         ;;
      \?)
         printf "illegal option: -%s\n" "$OPTARG" >&2
         echo "$usage" >&2
         exit 1
         ;;
   esac
   shift
done


if [ "$mode" = "histogram" ]
   then
   for value in $(seq -f "%f" 0 0.5 1); do
      echo $value

      sh ./src/setup_ns.sh

      ip netns exec server tc qdisc add dev server_link root netem delay ${serverdelay}ms loss ${value}%
      ip netns exec client tc qdisc add dev client_link root netem delay ${clientdelay}ms

      if [ "$rely" = "true" ]
      then
         path=$(locate -r rely-app/build/linux/app/rely$)
         gnome-terminal -- ip netns exec server $path tun --local_endpoint 10.0.0.1:5000 --remote_endpoint 10.0.0.2:5000 --tunnel_ip 11.11.11.11
         gnome-terminal -- ip netns exec client $path tun --local_endpoint 10.0.0.2:5000 --remote_endpoint 10.0.0.1:5000 --tunnel_ip 11.11.11.22
      fi

      gnome-terminal -- ip netns exec server sh ./src/server.sh -tries $tries -tp $throughput -rely "$rely"
      ip netns exec client sh ./src/client.sh -mode "$mode" -tries $tries -sd $serverdelay -cd $clientdelay -pl ${value} -tp $throughput -rely "$rely"

      ip netns delete server && ip netns delete client

      if [ "$rely" = "true" ]
      then
         pid=$(pgrep rely)
         kill -- -$pid
      fi
   done
fi

if [ "$mode" = "throughput" ]
then
   for value in $(seq -f "%f" 0 0.1 1); do
      echo $value

      sh ./src/setup_ns.sh

      ip netns exec server tc qdisc add dev server_link root netem delay ${serverdelay}ms loss ${value}%
      ip netns exec client tc qdisc add dev client_link root netem delay ${clientdelay}ms

      path=$(locate -r rely/build/linux/app/rely$)
      gnome-terminal -- ip netns exec server $path tun --local_endpoint 10.0.0.1:5000 --remote_endpoint 10.0.0.2:5000 --tunnel_ip 11.11.11.11
      gnome-terminal -- ip netns exec client $path tun --local_endpoint 10.0.0.2:5000 --remote_endpoint 10.0.0.1:5000 --tunnel_ip 11.11.11.22

      gnome-terminal -- ip netns exec server sh ./src/server.sh -tries $tries -tp $throughput -rely "true"
      ip netns exec client sh ./src/client.sh -mode "$mode" -tries $tries -sd $serverdelay -cd $clientdelay -pl ${value} -tp $throughput -rely "true"

      pid=$(pgrep rely)
      kill -- -$pid

      ip netns delete server && ip netns delete client

   done
   for value in $(seq -f "%f" 0 0.1 1); do
      echo $value

      sh ./src/setup_ns.sh

      ip netns exec server tc qdisc add dev server_link root netem delay ${serverdelay}ms loss ${value}%
      ip netns exec client tc qdisc add dev client_link root netem delay ${clientdelay}ms

      gnome-terminal -- ip netns exec server sh ./src/server.sh -tries $tries -tp $throughput -rely "false"
      ip netns exec client sh ./src/client.sh -mode "$mode" -tries $tries -sd $serverdelay -cd $clientdelay -pl ${value} -tp $throughput -rely "false"

      ip netns delete server && ip netns delete client
   done
fi


if [ "$mode" = "throughput" ]
then
   python3 plot_throughput.py --throughput $throughput
fi




