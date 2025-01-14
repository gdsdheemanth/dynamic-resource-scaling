# dynamic-resource-scaling
A dynamic resource scaling system using RL and predictive models for distributed ML workloads.

## Overview
This project provides dynamic resource scaling for distributed ML workloads using reinforcement learning (RL) and predictive models.

## Prerequisites
- GCP Account with Kubernetes Engine API enabled
- Python 3.8+
- Kubernetes CLI (kubectl)
- Google Cloud SDK

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/dynamic-resource-scaling.git
cd dynamic-resource-scaling

### 2. setup cloud shell
```bash
sudo apt-get update
sudo apt-get install python3.8 python3-pip -y
sudo apt-get install virtualenv -y
virtualenv -p python3.8 venv
source venv/bin/activate
pip install -r requirements.txt

### 3. create a gke cluster
```bash
gcloud container clusters create ml-cluster \
  --num-nodes=2 \
  --machine-type=e2-standard-4 \
  --zone=us-central1-a

### 4. Verify GKE Cluster Setup
```bash
gcloud container clusters list
gcloud container clusters get-credentials ml-cluster --zone=us-central1-a
kubectl get nodes

