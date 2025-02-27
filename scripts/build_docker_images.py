import os
import yaml
import subprocess

CONFIG_PATH = "config/docker_config.yaml"


def load_docker_config():
    """Load Docker configuration from YAML file."""
    with open(CONFIG_PATH, "r") as file:
        return yaml.safe_load(file)


def build_and_push_image(image_name, tag, dockerfile):
    """Build and push a Docker image to Google Container Registry (GCR)."""
    full_image_name = f"{image_name}:{tag}"
    print(f"📦 Building Docker Image: {full_image_name}...")

    # Build Docker image
    build_command = [
        "docker", "build", "-t", full_image_name, "-f", dockerfile, "."
    ]
    subprocess.run(build_command, check=True)

    # Authenticate with GCR before pushing
    subprocess.run(["gcloud", "auth", "configure-docker"], check=True)

    # Push Docker image to Google Container Registry
    push_command = ["docker", "push", full_image_name]
    subprocess.run(push_command, check=True)

    print(f"✅ Successfully built & pushed: {full_image_name}")

if __name__ == "__main__":
    config = load_docker_config()
    for service, details in config["images"].items():
        build_and_push_image(details["name"], details["tag"], details["dockerfile"])
