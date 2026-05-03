# Ansible

Les commandes ci-dessous sont a lancer depuis ce dossier pour utiliser `ansible.cfg` automatiquement.

```bash
cd /home/seb/Documents/homelab/ansible
```

## Commandes utiles

Afficher l'inventaire:

```bash
ansible-inventory --graph
```

Lister les hotes connus:

```bash
ansible all --list-hosts
```

Tester la connectivite:

```bash
ansible all -m ping
```

## Playbooks

### Installer les cles SSH

Sur tous les hotes:

```bash
ansible-playbook playbooks/install-ssh-keys.yml -k
```

Sur un seul hote:

```bash
ansible-playbook playbooks/install-ssh-keys.yml -k --limit <host>
```

Exemple:

```bash
ansible-playbook playbooks/install-ssh-keys.yml -k --limit vm-web-01
```

Note: `-k` demande le mot de passe SSH interactif, utile tant que les cles ne sont pas encore installees.

### Installer node_exporter

Sur tous les hotes eligibles:

```bash
ansible-playbook playbooks/install-node-exporter.yml
```

Sur un seul hote:

```bash
ansible-playbook playbooks/install-node-exporter.yml --limit <host>
```

Exemple:

```bash
ansible-playbook playbooks/install-node-exporter.yml --limit gw-main-01
```

Note: ce playbook n'installe `node_exporter` que sur les hotes qui ont `metrics.enabled: true` et `metrics.install` non desactive.
Note: avec `--list-hosts`, le second play peut afficher `0` hote car le groupe `metrics_enabled` est cree dynamiquement pendant l'execution.

### Installer les paquets de base

Sur tous les hotes:

```bash
ansible-playbook playbooks/install-base-packages.yml
```

Sur un seul hote:

```bash
ansible-playbook playbooks/install-base-packages.yml --limit <host>
```

Note: le playbook reference actuellement le role `base_packages`, alors que le dossier present dans `roles/` s'appelle `base_backages`.

### Installer qemu-guest-agent

Sur les groupes cibles du playbook:

```bash
ansible-playbook playbooks/install-qemu-guest-agent.yml
```

Sur un seul hote:

```bash
ansible-playbook playbooks/install-qemu-guest-agent.yml --limit <host>
```

### Generer les fichiers Prometheus file_sd

Rendre les fichiers localement dans `playbooks/rendered/file_sd/`:

```bash
ansible-playbook playbooks/generate-prometheus-file-sd.yml
```

Rendre puis publier vers `vm-mon-01`:

```bash
ansible-playbook playbooks/generate-prometheus-file-sd.yml -e publish_file_sd=true
```

## Rappels

- `--limit` doit utiliser le nom d'hote de l'inventaire (`vm-web-01`, `gw-main-01`, `pprd-hpv-pmx-01`, etc.), pas la valeur de `ansible_host`.
- Pour verifier les hotes cibles avant execution:

```bash
ansible-playbook playbooks/install-ssh-keys.yml --limit <host> --list-hosts
```

- Pour faire un dry run:

```bash
ansible-playbook playbooks/install-ssh-keys.yml -k --limit <host> --check --diff
```
