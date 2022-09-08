#!/usr/bin/env bash

set -eux


export ANSIBLE_INVENTORY_ENABLED="evgeni.duffy.inventory"
export ANSIBLE_INVENTORY=test.duffy.yml

ansible-playbook playbooks/test_inventory.yml
