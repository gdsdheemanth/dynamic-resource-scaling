from kubernetes import client, config

config.load_kube_config()
batch_v1 = client.BatchV1Api()

job_manifest = {
    "apiVersion": "batch/v1",
    "kind": "Job",
    "metadata": {"name": "distributed-training"},
    "spec": {
        "template": {
            "spec": {
                "containers": [{
                    "name": "training-container",
                    "image": "tensorflow/tensorflow:2.9.0",
                    "command": ["python", "/app/mnist_training.py"]
                }],
                "restartPolicy": "Never"
            }
        }
    }
}

batch_v1.create_namespaced_job(namespace="training", body=job_manifest)
