# System evaluation scripts

Some scripts I have found useful when performing systems evaluations.

Mostly automating repetitive tasks.

## Docker exec over swarm

Currently, `docker exec` only works for containers running on the local machine.

This script implements `docker exec` over a container running as part of a swarm.

Usage

```(bash)
service-exec -s <service_name> -- <command>
```

where `service_name` is the name of the
[service](https://docs.docker.com/engine/swarm/how-swarm-mode-works/services/)
in whichq the container belongs to
(assuming an 1-to-1 mapping from service to container).

Note:
`service-exec` runs `docker exec` over ssh.
It requires appropriate ssh configuration so that swarms nodes can be accessed
through ssh.

## Import data to Google Sheets
