FROM ubuntu:16.04

# Install updates and dependencies
RUN apt-get update -y && apt-get install --no-install-recommends -y -q curl python3 python3-pip python3-setuptools git ca-certificates imagemagick && apt-get clean && rm /var/lib/apt/lists/*_*

# prepare dirs
RUN mkdir /sitekicker && mkdir /source

# copy sitekicker code
COPY . /sitekicker

# install sitekicker
RUN pip3 install -e /sitekicker

# setup working dir
WORKDIR /source

ENTRYPOINT ["sitekicker"]
