# cluster: a Kubernetes lab on one machine

Scripts that turn a single physical machine into a multi-node Kubernetes cluster for teaching and
experiments. They size the virtual machines from the host's own RAM and CPU count, create them with
Vagrant and VirtualBox, install Kubernetes with Kubespray, and then add storage (Rook-Ceph), a service
mesh (Istio) and a sample workload (CTFd, a capture-the-flag platform).

## What happens when you run it

```sh
python3 bootstrap_k8s_cluster.py
```

runs these steps in order and stops at the first failure:

| Step | Script | What it does |
|---|---|---|
| 1 | `cluster_specs.py` | Reads the host's RAM and logical CPUs, reserves 4 GB and 2 CPUs for the host, and writes `cluster_config.yaml`: as many 8 GB VMs as fit, with an even number of cores each. The last two VMs get an extra disk for Ceph. |
| 2 | `Vagrantfile` (`vagrant up`) | Creates the VMs `node01`, `node02`, … from `cluster_config.yaml` and loads the `rbd` kernel module. If it fails, the VMs are destroyed. |
| 3 | `generate_inventory.py` | Collects each VM's address, creates an ssh key, installs it for root on every node, tests connectivity and writes the Kubespray `inventory.ini`. |
| 4 | `install_kubespray.sh` | Clones Kubespray, creates a Python virtual environment, checks that Ansible reaches every node and runs the cluster playbook. |
| 5 | `get_k8s_creds.sh` | Copies the admin kubeconfig from `node01`. |
| 6 | `install_kubectl.sh` | Installs `kubectl` and lists the nodes. |

## After the cluster is up

| Script | What it does |
|---|---|
| `generate_rook_yaml.py`, `rookfs_postinstall.sh`, `storageclass.yaml` | Generate the Rook-Ceph cluster definition from the running nodes, wait for the Ceph pods and create the storage class. |
| `istio_postinstall.py` | Runs `istioctl x precheck`, installs Istio with the chosen profile and prints the ingress gateway's routes. |
| `probe_volumes_to_annotate_velero.sh <namespace>` | Finds the volumes of the pods in a namespace and annotates them so that Velero backs them up. |
| `ctfd-k8s/` | Manifests for CTFd with MariaDB and Redis: namespace, config map, deployments and ingress. |

## Requirements

A Linux host with VirtualBox, Vagrant, Python 3 (`pyyaml`, `psutil`) and enough memory for at least one
8 GB VM beyond the 4 GB reserved for the host. The default box is `gutehall/ubuntu24-10`.

## Notes

- The database passwords in `ctfd-k8s/` are placeholders written in plain text. Change them, and move
  them to a Kubernetes Secret, before exposing the service.
- The generated files (`cluster_config.yaml`, `inventory.ini`, the Kubespray checkout and the
  kubeconfig) are ignored by git.
- Written in early 2025 as a small, self-contained way to stand up a cluster for a course or an
  experiment on a single server.
