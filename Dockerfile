FROM python:3.12

# Set working directory
WORKDIR /code

# Install Python dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy Python source code
COPY ./src /code/app

# Create temporary directory
RUN mkdir tmp

# Expose port
EXPOSE 8080 

# Run FastAPI
CMD ["fastapi", "run", "app/main.py", "--port", "80"]