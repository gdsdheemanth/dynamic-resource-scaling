# Use Ray Train official image
FROM rayproject/ray:latest

# Install additional dependencies
RUN pip install tensorflow numpy pandas scikit-learn cloudpickle kubernetes gcsfs google-cloud-storage

# Set the working directory
WORKDIR /app

# Copy training script into the container
COPY distributed_training_jobs/mnist_training.py /app/train.py

# Define entrypoint for Ray Train
ENTRYPOINT ["python", "/app/train.py"]



