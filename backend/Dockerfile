# Use Python image
FROM python:3.10-slim

# Set working dir
WORKDIR /app

# Install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Expose port Flask runs on
EXPOSE 5000

# Start the app
CMD ["python", "app.py"]
