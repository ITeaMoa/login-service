# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

ARG AWS_REGION
ARG AWS_CLIENT_ID
ARG AWS_CLIENT_SECRET
ARG AWS_USER_POOL_ID

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV AWS_CLIENT_ID=$AWS_CLIENT_ID
ENV AWS_CLIENT_SECRET=$AWS_CLIENT_SECRET
ENV AWS_REGION=$AWS_DEFAULT_REGION
ENV AWS_USER_POOL_ID=$AWS_USER_POOL_ID

RUN echo "AWS_REGION is ${AWS_DEFAULT_REGION}" 
RUN echo "AWS_CLIENT_ID is $AWS_CLIENT_ID" 
RUN echo $AWS_CLIENT_ID

RUN apt-get update && apt-get install -y \
    python3-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, and wheel
RUN pip install --upgrade pip setuptools wheel

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app’s code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
