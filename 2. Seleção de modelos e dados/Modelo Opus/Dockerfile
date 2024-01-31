# Use the official Python 3.10 image as the base image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any dependencies specified in requirements.txt (if present)
RUN pip install --no-cache-dir -r requirements.txt

# Specify the command to run on container start
CMD ["python", "OPUS-PT-BR-NQ.py"]
