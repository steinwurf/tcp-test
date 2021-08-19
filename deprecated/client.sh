#!/bin/bash

usage="$(basename "$0") [-help] [-mode] [-serverdelay m] [-clientdelay n]
                        [-packetloss l] [-throughput t] [-rely bool]
                        -- program to initiate the client in tcp_test

where:
    -mode         choose to either plot a histogram of added  (default: hist)
                  latency with -mode hist or collect samples of
                  average throughput for the given parameters.

    -tries        set the number of packets to transfer       (default: 10000)

    -serverdelay  set the delay value from server to client   (default: 60ms)
    (shortcut: -sd)

    -clientdelay  set the delay value from client to server   (default: 60ms)
    (shortcut: -cd)

    -packetloss   set the packet loss % from server to client (default:   0%)
    (shortcut: -pl)

    -throughput   set the throughput from server to client    (default: 1MB/s)
    (shortcut: -tp)

    -rely         simulates using rely if true                (default: false)

    -help         display this help section
"

# Default options:
mode=histogram
tries=10000
serverdelay=60
clientdelay=60
packetloss=0
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

      -pl | -packetloss)
         shift
         packetloss=$1
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

python3 ./src/client.py --mode "$mode" --tries $tries --server-latency $serverdelay --client-latency $clientdelay --packet-loss $packetloss --throughput $throughput --rely "$rely"