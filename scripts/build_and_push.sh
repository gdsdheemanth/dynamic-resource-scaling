#!/bin/bash

echo "🚀 Authenticating with Google Cloud..."
gcloud auth configure-docker

echo "🚀 Starting Docker Image Build Process..."
python3 scripts/build_docker_images.py
echo "✅ All Docker Images Built and Pushed to GCR Successfully!"


# horovod-training-cvmn7
# kubectl exec -it horovod-training-6crmg -n training -- horovodrun --check-build

