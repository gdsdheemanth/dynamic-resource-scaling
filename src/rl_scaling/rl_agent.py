import ray
import os
from ray.rllib.algorithms.ppo import PPOConfig
import kubernetes.client as k8s
from google.cloud import storage

GCS_BUCKET = "dra_dml_bucket"
GCS_MODEL_PATH = "rl_models/scaling_agent_checkpoint"
LOCAL_MODEL_DIR = "/app/models/scaling_agent_checkpoint"

def download_from_gcs(bucket_name, source_blob_name, local_dest):
    """Downloads model from GCS to local storage."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    
    os.makedirs(local_dest, exist_ok=True)
    blob.download_to_filename(os.path.join(local_dest, "checkpoint"))
    print(f"✅ Model downloaded from gs://{bucket_name}/{source_blob_name} to {local_dest}")

class RLScalingAgent:
    def __init__(self):
        download_from_gcs(GCS_BUCKET, GCS_MODEL_PATH, LOCAL_MODEL_DIR)
        config = (
            PPOConfig()
            .environment("KubernetesScalingEnv")
            .env_runners(num_env_runners=2)  # Updated API
            .framework("tf2")
        )
        self.trainer = config.build()
        self.trainer.restore(os.path.join(LOCAL_MODEL_DIR, "checkpoint"))
        self.api = k8s.CoreV1Api()

    def scale_pods(self, namespace="default", deployment="ml-training-job"):
        current_pods = self.get_pod_count(namespace, deployment)
        state = self.get_cluster_metrics()
        action = self.trainer.compute_single_action(state)

        if action == 0 and current_pods > 1:
            new_pods = current_pods - 1  # Scale down
        elif action == 1:
            new_pods = current_pods + 1  # Scale up
        else:
            return

        self.set_pod_count(namespace, deployment, new_pods)

    def get_pod_count(self, namespace, deployment):
        deployment_api = k8s.AppsV1Api()
        deployment = deployment_api.read_namespaced_deployment(deployment, namespace)
        return deployment.spec.replicas

    def set_pod_count(self, namespace, deployment, count):
        deployment_api = k8s.AppsV1Api()
        deployment_patch = {"spec": {"replicas": count}}
        deployment_api.patch_namespaced_deployment_scale(name=deployment, namespace=namespace, body=deployment_patch)
