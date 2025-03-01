import ray
from ray.rllib.algorithms.ppo import PPO
from kubernetes import client, config
from google.cloud import storage
from rl_env import KubernetesScalingEnv
import time

# Load Kubernetes config (inside the cluster)
config.load_incluster_config()
v1 = client.CoreV1Api()
apps_v1 = client.AppsV1Api()

# GCS Bucket and Model Path
GCS_BUCKET = "dra_dml_bucket"
GCS_MODEL_PATH = "rl_models/scaling_agent_checkpoint"
LOCAL_MODEL_PATH = "/tmp/scaling_agent_checkpoint"

def download_from_gcs(bucket_name, source_blob_name, destination_path):
    """Downloads model checkpoint from Google Cloud Storage."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_path)
    print(f"✅ Model downloaded from gs://{bucket_name}/{source_blob_name}")

# Download the trained model
download_from_gcs(GCS_BUCKET, GCS_MODEL_PATH, LOCAL_MODEL_PATH)

# Initialize Ray and Load Model
ray.init(ignore_reinit_error=True)
trainer = PPO(env=KubernetesScalingEnv, config={})
trainer.restore(LOCAL_MODEL_PATH)

# Initialize RL Environment
env = KubernetesScalingEnv({"max_pods": 10})
obs, _ = env.reset()

def get_deployment_replicas(namespace, deployment_name):
    """Fetches the current number of replicas of a deployment."""
    deployment = apps_v1.read_namespaced_deployment(deployment_name, namespace)
    return deployment.spec.replicas

def scale_deployment(namespace, deployment_name, replicas):
    """Scales Kubernetes Deployment."""
    patch = {"spec": {"replicas": replicas}}
    apps_v1.patch_namespaced_deployment_scale(deployment_name, namespace, patch)
    print(f"📌 Scaled {deployment_name} to {replicas} replicas.")

# RL Inference Loop - Periodically runs to scale the deployment
while True:
    action = trainer.compute_single_action(obs["agent_0"])

    # Mapping RL action to Kubernetes scaling decision
    current_replicas = get_deployment_replicas("ml-ops", "ml-training")

    if action == 0:  # Scale Down
        new_replicas = max(1, current_replicas - 1)
    elif action == 1:  # Scale Up
        new_replicas = min(env.max_pods, current_replicas + 1)
    else:  # Do nothing
        new_replicas = current_replicas

    # Apply Scaling Decision if there's a change
    if new_replicas != current_replicas:
        scale_deployment("ml-ops", "ml-training", new_replicas)
    
    # Update Observation
    obs, reward, done, _, _ = env.step({"agent_0": action})
    print(f"🛠 Action: {action}, Reward: {reward['agent_0']}, New Pods: {new_replicas}")

    time.sleep(30)  # Run inference every 30 seconds
