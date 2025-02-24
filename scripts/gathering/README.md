# Gathering Scripts

This directory contains scripts for gathering information and configurations from various servers in the homelab.

## Scripts

### `get_compose_from_server.sh`

This script copies `docker-compose.yml` files from a remote server to the local machine. Could be useful if you want to backup your compose files and you haven't done it yet. (shame on you)

#### Usage

```sh
./get_compose_from_server.sh <remote_server>
```

- `<remote_server>`: The SSH address of the remote server (e.g., `user@hostname`).

The script will find all docker-compose.yml files in the `/srv/docker/` directory on the remote server and copy them to corresponding directories on the local machine.

### get_infos.sh

This script gathers system information about the local machine and saves it to a YAML file.

#### Usage

```sh
./get_infos.sh
```

The script will generate a YAML file named `homelab_info_<hostname>.yml` containing details such as hostname, FQDN, DNS name, OS, uptime, hardware specifications, network interfaces, running services, Docker information, top processes, open ports, and recent logs. It is usefull for context when using LLM for instance.

## Notes

- Ensure that you have the necessary permissions to execute these scripts.
- The get_compose_from_server.sh script requires SSH access to the remote server.
- The get_infos.sh script requires various system utilities such as `lsb_release`, `lscpu`, `free`, `df`, `ip`, `systemctl`, `docker`, `ps`, `ss`, and `journalctl`.