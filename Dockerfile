# Base image we are using is python:3.9-slim
FROM python:3.9-slim

# Copy the current working directory to the /app directory inside the container
COPY . /app

# Set /app as the working directory for the Python container
WORKDIR /app

# Install the required packages using the requirement.txt
RUN pip install -r requirements.txt

# Set the entry point for the container
ENTRYPOINT ["/app/entrypoint.sh"]