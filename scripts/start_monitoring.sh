#!/bin/bash

# Install Prometheus & Grafana
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install monitoring prometheus-community/kube-prometheus-stack --namespace monitoring

# Forward Grafana port
kubectl port-forward service/prometheus-grafana 3000:80 -n monitoring
