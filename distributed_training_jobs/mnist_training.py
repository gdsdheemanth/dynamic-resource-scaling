import ray
import os
from ray import train
import tensorflow as tf
from ray.train.tensorflow import TensorflowTrainer
from ray.train import ScalingConfig,RunConfig
import tensorflow.io.gfile as gfile
from google.cloud import storage

ray.init()
print("Ray Available Resources:", ray.available_resources())


# Define GCS Bucket & Model Path
GCS_BUCKET = "dra_dml_bucket"
GCS_MODEL_PATH = "distributed_trained_models/final_model.keras"

def upload_to_gcs(local_file, bucket_name, destination_blob_name):
    """Uploads a file to Google Cloud Storage."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(local_file)
    print(f"✅ Model successfully uploaded to gs://{bucket_name}/{destination_blob_name}")


def train_func(config=None):
    """Distributed training function for Ray Train"""
    if config is None:
        config = {}

    # Ensure default values exist
    epochs = config.get("epochs", 5)  # Default to 5 epochs if not provided
    batch_size = config.get("batch_size", 32)
    learning_rate = config.get("learning_rate", 0.001)

    print(f"Running training for {epochs} epochs with batch size {batch_size} and learning rate {learning_rate}")

    # Define distributed training strategy
    strategy = tf.distribute.MultiWorkerMirroredStrategy()

    with strategy.scope():
        model = tf.keras.Sequential([
            tf.keras.layers.Flatten(input_shape=(28, 28)),  # Flatten input to 1D
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(10, activation='softmax')
        ])
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
                      loss='sparse_categorical_crossentropy',
                      metrics=['accuracy'])

    # Load dataset
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
    x_train, x_test = x_train / 255.0, x_test / 255.0  # Normalize pixel values

    # Train model
    model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size)

    # Save model to a temporary local directory
    local_model_path = "/tmp/final_model.keras"
    model.save(local_model_path)

    # Upload to GCS
    upload_to_gcs(local_model_path, GCS_BUCKET, GCS_MODEL_PATH)

# trainer = TensorflowTrainer(train_loop_per_worker=train_func,scaling_config=ScalingConfig(num_workers=1))

trainer = TensorflowTrainer(
    train_loop_per_worker=train_func,
    scaling_config=ScalingConfig(num_workers=1),
    run_config=RunConfig(storage_path="/app/train_logs"),
    train_loop_config={"epochs": 5, "batch_size": 32, "learning_rate": 0.001}
)

trainer.fit()
