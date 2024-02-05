# Use the official Python image
FROM python:3.10-slim

# Create and set the working directory
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Create and activate a virtual environment
RUN python -m venv venv
SHELL ["/bin/bash", "-c"]
RUN source venv/bin/activate

# Upgrade pip and setuptools
RUN pip install --upgrade pip setuptools

# Install dependencies from requirements.txt
RUN pip install -r requirements.txt

# Install uvicorn
RUN pip install urllib3==1.26.6

# Copy the application code to the container
COPY . .

# Expose the port that your FastAPI application will run on
EXPOSE 8080

# Command to run the application using uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
