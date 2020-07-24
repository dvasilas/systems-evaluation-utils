#!/bin/bash

set -e

SCRIPT_NAME=$(basename $(test -L "$0" && readlink "$0" || echo "$0" ) .sh);

usage() {
  cat <<EOF
usage: $SCRIPT_NAME -s <service> -- <command>
EOF
}

while getopts ":hs:" option; do
    case "$option" in
        s)  SERVICE=$2;;
        h)  usage; exit 1;;
        :)  echo "Option -$OPTARG requires an argument" >&2;;
        \?) echo "Unsupported option: -$OPTARG !" >&2;;
    esac
done
shift $(($OPTIND - 1));

[ -z $SERVICE ] && {
    usage
    exit 1
}

TASK_ID=$(docker service ps --filter 'desired-state=running' $SERVICE -q)
NODE_ID=$(docker inspect --format '{{ .NodeID }}' $TASK_ID)
CONTAINER_ID=$(docker inspect --format '{{ .Status.ContainerStatus.ContainerID }}' $TASK_ID)
NODE_HOST=$(docker node inspect --format '{{ .Description.Hostname }}' $NODE_ID)

ssh -tt $NODE_HOST docker exec -ti $CONTAINER_ID $@