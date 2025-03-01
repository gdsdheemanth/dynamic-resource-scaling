# gcloud container images delete gcr.io/dra-dml/rl_training:v1

# docker buildx build --platform=linux/amd64 -t gcr.io/dra-dml/rl_training:v1 -f docker/rl_training.Dockerfile --push .

# docker run --rm -it gcr.io/dra-dml/rl_training:v1 /bin/sh

kubectl delete job rl-training -n training
kubectl apply -f config/rl_training_job.yaml