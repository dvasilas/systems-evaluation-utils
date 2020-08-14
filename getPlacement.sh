#!/bin/bash

set -e

for service in $(docker service ls --format '{{ .Name}}')
do
	task_id=$(docker service ps --filter 'desired-state=running' $service -q)
	node_id=$(docker inspect --format '{{ .NodeID }}' $task_id)
	echo $service: $(docker node inspect --format '{{ .Description.Hostname }}' $node_id)
done
