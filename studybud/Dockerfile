# Use an official Python runtime as a parent image
FROM python:3.11.5-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# create root directory for our project in the container
RUN mkdir /studybud


# Set the working directory to /studybud
WORKDIR /studybud

# Copy the current directory contents into the container at /music_service
ADD . /working/


# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt
# RUN pip install --cache-dir .pip_cache -r requirements.txt

# Expose the port the application will run on
EXPOSE 8000

# Define the command to run your application
CMD ["pipenv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
