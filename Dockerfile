FROM python:3.7

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code


# Install dependencies
RUN LIBMEMCACHED=/opt/local
RUN apt-get update && apt-get install -y \
        libmemcached11 \
        libmemcachedutil2 \
        libmemcached-dev \
        libz-dev \
        curl \
        gettext

COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . ./code/

