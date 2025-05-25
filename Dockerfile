FROM python:3.8-slim-buster

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Environment variables for MPI and prediction
ENV MODEL_PATH=fraud_rf_model.pkl
ENV QUEUE_URL=http://queue-daemon:7500
ENV INPUT_QUEUE=transactions
ENV OUTPUT_QUEUE=results
ENV TOKEN=AGENT_TOKEN_1

# Expose port 7500
EXPOSE 7500

# Install system dependencies for MPI
RUN apt-get update && apt-get install -y \
    openmpi-bin \
    openmpi-common \
    libopenmpi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app

# Switching to a non-root user, please refer to https://aka.ms/vscode-docker-python-user-rights
RUN useradd appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "queue_daemon/main.py"]
