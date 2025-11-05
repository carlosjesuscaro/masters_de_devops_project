# Dockerfile

FROM python:3.10-slim as builder

# Setting environment variables for the application
ENV PYTHONUNBUFFERED=1 \
    APP_HOME=/app

# Creating the application directory
WORKDIR $APP_HOME

# Copying requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.10-slim-buster

# Setting the application home and copy required files from the builder stage
ENV APP_HOME=/app
WORKDIR $APP_HOME

# Copying the required files
COPY jokes_api /app/jokes_api
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt --prefix /usr/local
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Exposing the port the application runs on
EXPOSE 8000

# Setting environment variables for the application at runtime
ENV DB_HOST=db-service-name \
    DB_NAME=jokedb \
    DB_USER=joke_user \
    DB_PASS=joke_secret_pass

# The command to run the application
CMD ["python3", "-m", "uvicorn", "jokes_api.src.main:app", "--host", "0.0.0.0", "--port", "8000"]