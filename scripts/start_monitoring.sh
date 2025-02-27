#!/bin/bash

echo "Adding Prometheus and Grafana Helm repositories..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

echo "Creating monitoring namespace..."
kubectl create namespace monitoring || echo "Namespace already exists"

echo "Installing Prometheus and Grafana..."
helm install monitoring prometheus-community/kube-prometheus-stack --namespace monitoring

# Wait for the pods to be ready
echo "Waiting for Prometheus and Grafana pods to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/monitoring-grafana -n monitoring

echo "Prometheus and Grafana installation complete."

# Port forward Grafana
# echo "Access Grafana UI at http://localhost:3000"
# kubectl port-forward service/monitoring-grafana 3000:80 -n monitoring

# Port foreward Prometheus
# kubectl get svc -n monitoring | grep prometheus
# kubectl port-forward service/monitoring-kube-prometheus-prometheus 9090 -n monitoring
# sum(rate(container_cpu_usage_seconds_total[5m]))
# kubectl logs -l app=prometheus -n monitoring

kubectl apply -f config/service-monitor.yaml

# testing with test_job
# kubectl apply -f test_job.yaml

# kubectl get pods -n training
# kubectl logs cpu-intensive-job-7qpzx -n training
# kubectl delete job cpu-intensive-job -n training


