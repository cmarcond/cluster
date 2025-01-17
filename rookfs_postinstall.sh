#!/bin/bash

set -e

# Clone the Rook repository
echo "Cloning the Rook repository..."
git clone --single-branch --branch v1.12.8 https://github.com/rook/rook.git
cd rook/deploy/examples

# Deploy Rook CRDs, common resources, and operator
echo "Deploying Rook CRDs, common resources, and operator..."
kubectl create -f crds.yaml -f common.yaml -f operator.yaml
cd ../../..

# Generate the Rook Ceph cluster YAML configuration
echo "Generating the Rook Ceph cluster configuration..."
python3 generate_rook_yaml.py

# Deploy the Rook Ceph cluster
echo "Deploying the Rook Ceph cluster..."
kubectl create -f rook_ceph_cluster.yaml

# Deploy the Rook toolbox
echo "Deploying the Rook toolbox..."
kubectl create -f rook/deploy/examples/toolbox.yaml

# Wait for Rook-Ceph pods to be running
echo "Waiting for Rook-Ceph pods to be in running state..."
while true; do
    NOT_RUNNING=$(kubectl get pods -n rook-ceph --no-headers | awk '$3 != "Running" {print $1}')
    if [ -z "$NOT_RUNNING" ]; then
        echo "All Rook-Ceph pods are running."
        break
    else
        echo "Waiting for pods to be in running state..."
        sleep 10
    fi
done
