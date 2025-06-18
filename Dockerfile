FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py

# Fix port to 3000 (instead of 3002)
RUN sed -i 's/port=3002/port=3000/g' app.py

# Expose the port
EXPOSE 3000

# Command to run the application
CMD ["python", "app.py"]
