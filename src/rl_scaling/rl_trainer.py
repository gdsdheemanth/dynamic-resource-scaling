import os
import ray
from ray.rllib.algorithms.ppo import PPOConfig
from google.cloud import storage
from rl_env import KubernetesScalingEnv

os.environ["PYOPENGL_PLATFORM"] = "egl"  # Use EGL instead of X11
os.environ["DISPLAY"] = ":0"  # Fake display
os.environ["MUJOCO_GL"] = "egl"  # Use EGL rendering

# Define GCS Bucket and Model Path
GCS_BUCKET = "dra_dml_bucket"
GCS_MODEL_PATH = "rl_models/scaling_agent_checkpoint"

def upload_to_gcs(local_checkpoint_path, bucket_name, destination_blob_name):
    """Uploads a checkpoint directory to Google Cloud Storage."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    for root, _, files in os.walk(local_checkpoint_path):
        for file in files:
            local_file_path = os.path.join(root, file)
            gcs_blob_path = os.path.join(destination_blob_name, file).replace("\\", "/")
            blob = bucket.blob(gcs_blob_path)

            blob.upload_from_filename(local_file_path)
            print(f"✅ Uploaded {local_file_path} to gs://{bucket_name}/{gcs_blob_path}")

# Initialize Ray
ray.init(ignore_reinit_error=True)

# Configure PPO Algorithm (Using New API)
config = (
    PPOConfig()
    .environment(KubernetesScalingEnv)  
    .framework("torch")  
    .training(lr=0.0001, gamma=0.99)
    .api_stack(enable_rl_module_and_learner=True, enable_env_runner_and_connector_v2=True)  
    .env_runners(num_env_runners=2)  
)

# Build PPO Trainer
trainer = config.build()

# Training loop
max_iters = 50  # Number of iterations
for i in range(max_iters):
    result = trainer.train()
    print(f"Iteration {i}: Reward = {result['episode_reward_mean']}")

    if i % 10 == 0:
        checkpoint_path = trainer.save()
        print(f"✅ Checkpoint saved at {checkpoint_path}")

# Final Checkpoint & Upload to GCS
final_checkpoint = trainer.save()
print(f"✅ Final checkpoint saved at {final_checkpoint}")

upload_to_gcs(final_checkpoint, GCS_BUCKET, GCS_MODEL_PATH)

# Shutdown Ray
ray.shutdown()
