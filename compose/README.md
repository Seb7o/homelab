# Docker Compose Configurations

This directory contains Docker Compose configurations for various services in the homelab. Each subfolder represents a different service and contains the necessary files to deploy and manage the service using Docker Compose.

## Structure

- **[authentik](./authentik)**: Configuration for [Authentik](https://hub.docker.com/r/goauthentik/server), an open-source identity provider.
- **[bastion](./bastion)**: Configuration for [Bastion](https://github.com/nqngo/docker-bastion), Alpine-based jump host with OpenSSH Server (sshd) and GnuPG (gnupg).
- **[bookstack](./bookstack)**: Configuration for [BookStack](https://hub.docker.com/r/linuxserver/bookstack), a simple, self-hosted wiki platform.
- **[grafana](./grafana)**: Configuration for [Grafana](https://hub.docker.com/r/grafana/grafana), an open-source platform for monitoring and observability.
- **[graylog](./graylog)**: Configuration for [Graylog](https://hub.docker.com/r/graylog/graylog), a centralized log management solution.
- **[homarr](./homarr)**: Configuration for [Homarr](https://hub.docker.com/r/ajnart/homarr), a sleek and customizable dashboard for your homelab.
- **[it-tools](./it-tools)**: Configuration for [IT Tools](https://github.com/CorentinTh/it-tools), useful tools for developer and people working in IT.
- **[nginx](./nginx)**: Configuration for [Nginx Proxy Manager](https://hub.docker.com/r/jc21/nginx-proxy-manager), a simple way to manage reverse proxies.
- **[paperless](./paperless)**: Configuration for [Paperless ngx](https://github.com/paperless-ngx/paperless-ngx), a document management system that transforms your physical documents into a searchable online archive so you can keep, well, less paper.
- **[pihole](./pihole)**: Configuration for [Pi-hole](https://hub.docker.com/r/pihole/pihole), a network-wide ad blocker.
- **[rocketchat](./rocketchat)**: Configuration for [Rocket.Chat](https://hub.docker.com/r/rocketchat/rocket.chat), an open-source team communication platform.
- **[routr](./routr)**: Configuration for [Routr](https://hub.docker.com/r/fonoster/routr), a lightweight SIP proxy.
- **[shlink](./shlink)**: Configuration for [Shlink](https://hub.docker.com/r/shlinkio/shlink), a self-hosted URL shortener.
- **[stirling-pdf](./shtirling-pdf)**: Configuration for [Stirling PDF](https://github.com/Stirling-Tools/Stirling-PDF), a robust, locally hosted web-based PDF manipulation tool.
- **[trillium](./trillium)**: Configuration for [Trilium Notes](https://hub.docker.com/r/zadam/trilium), a hierarchical note-taking application.
- **[uptime-kuma](./uptime-kuma)**: Configuration for [Uptime Kuma](https://hub.docker.com/r/zadam/trilium), A fancy self-hosted monitoring tool.
- **[vaultwarden](./vaultwarden)**: Configuration for [Vaultwarden](https://github.com/louislam/uptime-kuma), an unofficial Bitwarden server implementation.
- **[zulip](./zulip)**: Configuration for [Zulip](https://hub.docker.com/r/zulip/zulip), an open-source team chat application.

## Usage

To deploy a service, navigate to the respective subfolder and run the following command:

```sh
docker-compose up -d
```
Ensure that you have Docker and Docker Compose installed on your system.

## Environment Variables
Each service may require specific environment variables. These are defined in `.env` files within each subfolder. Make sure to configure these variables according to your setup before deploying the services.