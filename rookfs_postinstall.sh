#!/bin/bash

set -e

# Function to wait for pods to be running with a timeout
wait_for_pods() {
    local namespace=$1
    local timeout=$2 # Timeout in seconds
    local interval=10 # Check interval in seconds
    local elapsed=0

    echo "Waiting for pods in namespace '$namespace' to be in running state (timeout: $timeout seconds)..."
    while true; do
        NOT_RUNNING=$(kubectl get pods -n "$namespace" --no-headers | awk '$3 != "Running" && $3 != "Complete" {print $1}')
        if [ -z "$NOT_RUNNING" ]; then
            echo "All relevant pods in namespace '$namespace' are in running or complete state."
            break
        fi

        if [ "$elapsed" -ge "$timeout" ]; then
            echo "Timeout reached while waiting for pods in namespace '$namespace'."
            echo "Remaining non-running pods:"
            echo "$NOT_RUNNING"
            exit 1
        fi

        echo "Waiting for pods to be in running or complete state..."
        sleep "$interval"
        elapsed=$((elapsed + interval))
    done
}

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

# Wait for Rook-Ceph pods to be running or complete with a timeout
wait_for_pods "rook-ceph" 600 # 600 seconds (10 minutes) timeout

# Deploy the Rook toolbox
echo "Deploying the Rook toolbox..."
kubectl create -f rook/deploy/examples/toolbox.yaml
