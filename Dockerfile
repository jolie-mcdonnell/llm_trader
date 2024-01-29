# Use the official AWS Lambda base image for Python 3.9
FROM public.ecr.aws/lambda/python:3.9

# Copy the content of your Lambda function code into the container
COPY . /var/task
COPY src/ /var/task

# Set the working directory
WORKDIR /var/task

# Install the required packages using the requirements.txt
RUN pip install -r requirements.txt

# Set the entry point for the container
ENTRYPOINT ["/var/task/entrypoint.sh"]
