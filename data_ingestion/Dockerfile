# Use an official Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy dependencies file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app.py .

# Expose port
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
