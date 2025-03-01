# Base image with Ray and RLlib
# Use Ray ML image for PyTorch support
FROM rayproject/ray-ml:latest

# Set working directory
WORKDIR /app

# Install additional dependencies
RUN pip install --no-cache-dir numpy pandas scikit-learn google-cloud-storage gymnasium kubernetes

# Copy RL training scripts
COPY src/rl_scaling /app/src/rl_scaling

# Set execution command
CMD ["python", "/app/src/rl_scaling/rl_agent.py"]
