import ray
from ray.rllib.algorithms.ppo import PPOConfig
from google.cloud import storage
from rl_env import KubernetesScalingEnv
import os

# Define GCS Bucket and Model Path
GCS_BUCKET = "dra_dml_bucket"
GCS_MODEL_PATH = "rl_models/scaling_agent_checkpoint"


def upload_to_gcs(local_dir, bucket_name, destination_blob_name):
    """Uploads a folder to Google Cloud Storage manually."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # Check if it's a directory
    if os.path.isdir(local_dir):
        for file_name in os.listdir(local_dir):
            file_path = os.path.join(local_dir, file_name)
            blob = bucket.blob(f"{destination_blob_name}/{file_name}")
            blob.upload_from_filename(file_path)
            print(f"✅ Uploaded {file_path} to gs://{bucket_name}/{destination_blob_name}/{file_name}")
    else:
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(local_dir)
        print(f"✅ Model successfully uploaded to gs://{bucket_name}/{destination_blob_name}")

# Initialize Ray and Train PPO Model
ray.init(ignore_reinit_error=True)

config = (
    PPOConfig()
    .environment(KubernetesScalingEnv, env_config={"max_pods": 10})
    .framework("torch")
    .rollouts(num_rollout_workers=2)
    .training(lr=0.0001, gamma=0.99)
)

trainer = config.build()

for i in range(50):
    result = trainer.train()
    
    # ✅ Fix: Extract episode reward safely
    episode_rewards = result.get("hist_stats", {}).get("episode_reward", [])
    mean_reward = sum(episode_rewards) / len(episode_rewards) if episode_rewards else 0

    print(f"Iteration {i}: Mean Reward = {mean_reward}")

    if i % 10 == 0:
        checkpoint = trainer.save()
        print(f"✅ Checkpoint saved at {checkpoint}")

# Upload the final model to GCS
upload_to_gcs(checkpoint, GCS_BUCKET, GCS_MODEL_PATH)
