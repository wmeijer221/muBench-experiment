#! /bin/bash

# When ran, it updates the Docker isolation rules to not
# block Container -> Minikube messages.

K8_INTERFACE=br-a730e7875f48
K8_IPv4=192.168.49.2
CON_IPv4=172.17.0.3

sudo iptables -I DOCKER-ISOLATION-STAGE-1 1 -p all -j RETURN -i docker0 -o $K8_INTERFACE -s $CON_IPv4 -d $K8_IPv4
sudo iptables -I DOCKER-ISOLATION-STAGE-1 1 -p all -j RETURN -i $K8_INTERFACE -o docker0 -s $K8_IPv4 -d $CON_IPv4
sudo iptables-save
