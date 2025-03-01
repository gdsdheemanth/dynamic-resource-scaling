# Base image with Ray and RLlib
# Use Ray ML image for PyTorch support
FROM rayproject/ray-ml:latest

# Set working directory
WORKDIR /app

# Install additional dependencies
RUN pip install --no-cache-dir numpy pandas scikit-learn google-cloud-storage gymnasium 


# Copy RL training scripts
COPY src/rl_scaling /app/src/rl_scaling
COPY config/rl_config.json /app/config/rl_config.json

# Set environment variables
ENV RAY_DISABLE_MEMORY_MONITOR=1

# Run RL training script
CMD ["python", "/app/src/rl_scaling/rl_trainer.py"]
