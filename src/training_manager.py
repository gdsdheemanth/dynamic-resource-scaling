import os
import subprocess
from job_template import load_yaml_template, save_yaml_file

# Configurations
TEMPLATE_PATH = "config/ray_job_template.yaml"
OUTPUT_PATH = "generated_ray_job.yaml"

def delete_existing_job(job_name, namespace="training"):
    """Delete an existing Kubernetes job before reapplying it."""
    print(f"🗑️ Deleting existing job: {job_name} (if it exists)...")
    subprocess.run(["kubectl", "delete", "job", job_name, "-n", namespace], check=False)


def submit_training_job(job_name, docker_image, num_workers, cpu_limit, memory_limit):
    """Submit a distributed ML training job with configurable parameters."""
    delete_existing_job(job_name)  # Delete existing job before applying
    
    params = {
        "job_name": job_name,
        "docker_image": docker_image,
        "num_workers": num_workers,
        "cpu_limit": cpu_limit,
        "memory_limit": memory_limit
    }

    # Load template and generate final YAML file
    job_config = load_yaml_template(TEMPLATE_PATH, params)
    save_yaml_file(job_config, OUTPUT_PATH)

    # Apply job to Kubernetes
    print(f"Deploying job: {job_name} with {num_workers} workers...")
    subprocess.run(["kubectl", "apply", "-f", OUTPUT_PATH])

    return f"Job {job_name} submitted successfully."


# Example usage
if __name__ == "__main__":
    submit_training_job(
        job_name="ray-training",
        docker_image="gcr.io/dra-dml/ray-training",
        num_workers=1,
        cpu_limit="2",
        memory_limit="4Gi"
    )
