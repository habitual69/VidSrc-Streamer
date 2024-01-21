# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV ALLOWED_ORIGINS "*"

# Run VidSrc Streamer when the container launches
CMD ["uvicorn", "m3u8parser:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
