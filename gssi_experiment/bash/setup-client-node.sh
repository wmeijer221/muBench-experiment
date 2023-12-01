#! /bin/bash

# Install pip
cd ~
sudo apt install python3-pip

# Install kubectl
curl -O https://s3.us-west-2.amazonaws.com/amazon-eks/1.27.6/2023-10-17/bin/linux/amd64/kubectl
chmod +x ./kubectl
mkdir -p $HOME/bin && cp ./kubectl $HOME/bin/kubectl && export PATH=$HOME/bin:$PATH
echo 'export PATH=$HOME/bin:$PATH' >> ~/.bashrc
kubectl version --client

# Clone repo
cd ~
git clone https://github.com/wmeijer221/muBench-experiment.git
cd muBench-experiment
# pip3 install -r ./requirements.txt --no-binary :all:
cat requirements.txt | xargs -n 1 pip3 install
export PYTHONPATH=~/muBench-experiment/

# Set kubectl config
echo Copy the config file of your k8s master node into ~/.kube/config
cd ~
mkdir .kube
cd .kube
touch config

chmod +x '/home/ubuntu/muBench-experiment/gssi_experiment/bash/*'
