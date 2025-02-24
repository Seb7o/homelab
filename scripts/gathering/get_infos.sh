#!/bin/bash

OUTPUT_FILE="homelab_info_$(hostname).yml"

echo "hostname: \"$(hostname)\"" > $OUTPUT_FILE
echo "fqdn: \"$(hostname -f 2>/dev/null || echo 'Unknown')\"" >> $OUTPUT_FILE
echo "dns_name: \"$(nslookup $(hostname) 2>/dev/null | awk '/name =/ {print $4}' | sed 's/\.$//' || echo 'Unknown')\"" >> $OUTPUT_FILE
echo "os: \"$(lsb_release -d 2>/dev/null | awk -F'\t' '{print $2}' || cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d= -f2 | tr -d '\"')\"" >> $OUTPUT_FILE
echo "uptime: \"$(uptime -p)\"" >> $OUTPUT_FILE

echo "hardware:" >> $OUTPUT_FILE
echo "  model: \"$(cat /sys/devices/virtual/dmi/id/product_name 2>/dev/null)\"" >> $OUTPUT_FILE
echo "  cpu:" >> $OUTPUT_FILE
echo "    model: \"$(lscpu | grep 'Model name' | awk -F: '{print $2}' | sed 's/^ *//')\"" >> $OUTPUT_FILE
echo "    cores: $(nproc)" >> $OUTPUT_FILE
echo "  ram: \"$(free -h | awk '/Mem:/ {print $2}')\"" >> $OUTPUT_FILE
echo "  storage:" >> $OUTPUT_FILE
df -h | grep '^/dev/' | awk '{print "    - filesystem: \"" $1 "\"\n      size: \"" $2 "\"\n      used: \"" $3 "\"\n      available: \"" $4 "\"\n      mount: \"" $6 "\""}' >> $OUTPUT_FILE

echo "network:" >> $OUTPUT_FILE
ip -o -4 addr show | awk '{print "  - interface: \"" $2 "\"\n    address: \"" $4 "\""}' >> $OUTPUT_FILE

echo "running_services:" >> $OUTPUT_FILE
systemctl list-units --type=service --state=running --no-pager --plain | awk '{print "  - \"" $1 "\""}' >> $OUTPUT_FILE

echo "docker:" >> $OUTPUT_FILE
if command -v docker &> /dev/null; then
    echo "  version: \"$(docker --version)\"" >> $OUTPUT_FILE
    echo "  running_containers:" >> $OUTPUT_FILE
    docker ps --format "  - name: \"{{.Names}}\"\n    image: \"{{.Image}}\"\n    ports: \"{{.Ports}}\"\n    status: \"{{.Status}}\"" >> $OUTPUT_FILE
    echo "  compose_stacks:" >> $OUTPUT_FILE
    find / -name "docker-compose.yml" -exec dirname {} \; 2>/dev/null | awk '{print "  - \"" $1 "\""}' >> $OUTPUT_FILE
else
    echo "  installed: false" >> $OUTPUT_FILE
fi

echo "top_processes:" >> $OUTPUT_FILE
ps -eo pid,user,%cpu,%mem,command --sort=-%cpu | head -n 15 | awk '{if(NR>1) print "  - pid: \"" $1 "\"\n    user: \"" $2 "\"\n    cpu: \"" $3 "\"\n    memory: \"" $4 "\"\n    command: \"" $5 "\""}' >> $OUTPUT_FILE

echo "open_ports:" >> $OUTPUT_FILE
ss -tulnp | awk '{if(NR>1) print "  - protocol: \"" $1 "\"\n    local_address: \"" $4 "\"\n    process: \"" $7 "\""}' >> $OUTPUT_FILE

echo "logs:" >> $OUTPUT_FILE
echo "  recent:" >> $OUTPUT_FILE
journalctl -n 50 --no-pager | awk '{print "    - \"" $0 "\""}' >> $OUTPUT_FILE

echo "Report generated: $OUTPUT_FILE"
