#!/bin/bash

# Create GKE cluster
# gcloud container clusters create "distributed-training-cluster" \
#     --num-nodes=3 --region=us-central1 \
#     --enable-autoscaling --min-nodes=1 --max-nodes=5

gcloud container clusters create "ml-cluster" \
    --num-nodes=2 --machine-type=e2-standard-4 --region=us-central1

# Get credentials
gcloud container clusters get-credentials "ml-cluster" --region=us-central1

# Create Namespaces
kubectl apply -f config/k8s_config.yaml

