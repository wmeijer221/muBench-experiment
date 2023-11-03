
# Install pip
cd ~
curl https://bootstrap.pypa.io/get-pip.py >> ./get-pip.py
python3 ./get-pip.py
alias pip3='python3 -m pip'

# Install kubectl
curl -O https://s3.us-west-2.amazonaws.com/amazon-eks/1.27.6/2023-10-17/bin/linux/amd64/kubectl
chmod +x ./kubectl
mkdir -p $HOME/bin && cp ./kubectl $HOME/bin/kubectl && export PATH=$HOME/bin:$PATH
echo 'export PATH=$HOME/bin:$PATH' >> ~/.bashrc
kubectl version --client

# Set kubectl config
echo Copy the config file of your k8s master node into ~/.kube/config
cd ~
mkdir .kube
cd .kube
touch config

# Clone repo
cd ~
git clone https://github.com/wmeijer221/muBench-experiment.git
cd muBench-experiment
pip3 install -r ./requirements.txt --no-binary :all:
export PYTHONPATH=~/muBench-experiment/
