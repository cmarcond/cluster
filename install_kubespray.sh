git clone https://github.com/kubernetes-sigs/kubespray.git
cd kubespray
cp -rfp inventory/sample inventory/mycluster
cp ../inventory.ini inventory/mycluster/inventory.ini 

VENVDIR=kubespray-venv
KUBESPRAYDIR=kubespray
python3 -m venv $VENVDIR
source $VENVDIR/bin/activate
pip install -U -r requirements.txt

ansible -i inventory/mycluster/inventory.ini kube_node -m ping --private-key ~/.ssh/id_rsa_root -u root

ansible-playbook -i inventory/mycluster/inventory.ini cluster.yml -b -v --private-key=~/.ssh/id_rsa_root -u root
