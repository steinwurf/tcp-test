#!/bin/bash
usage="$(basename "$0") [-h] [-tries p] [-throughput n] [-rely bool] -- program to initiate the Server in tcp_test

where:
    -tries           set the number of packets to transfer       (default: 10000)
    -throughput      set the throughput from server to client    (default: 1MB/s) (shortcut: -tp)

"
tries=10000
throughput=1
rely=false

while [ "$1" != "" ]; do
   case $1 in
      -h | -help)
         echo "$usage"
         exit
         ;;

      -tries)
         shift
         tries=$1
         ;;

      -tp | -throughput)
         shift
         throughput=$1
         ;;

      -rely)
         shift
         rely=$1
         ;;

      \?) printf "illegal option: -%s\n" "$OPTARG" >&2
         echo "$usage" >&2
         exit 1
         ;;
   esac
   shift
done


python3 ./src/server.py --tries $tries --throughput $throughput --rely "$rely"