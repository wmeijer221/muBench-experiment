#! /binbash

echo Installing K3S
curl -sfL https://get.k3s.io | sh -


echo Installing Helm
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh


echo Setting up full monitoring
cd ~/muBench-experiment/Monitoring/kubernetes-full-monitoring
chmod +x ./monitoring-install.sh
cd ~/muBench-experiment
./Monitoring/kubernetes-full-monitoring/monitoring-install.sh

