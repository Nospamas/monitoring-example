# FROM debian:buster-slim as build

# # Enable OpenRC
# ENV INITSYSTEM on 
# ENV VERSION "2.54.2+rev1.prod"

# WORKDIR /usr/src/app

# RUN apt-get update && apt-get install -y build-essential wget awscli bc flex libssl-dev bison curl

#
# TODO: Disabled for now. Work out how to build target specific module for audio...
#

#COPY build.sh .
#COPY workarounds.sh .
#COPY rpi0-i2s-audio/ ./rpi0-i2s-audio
#RUN ./build.sh build --device %%BALENA_MACHINE_NAME%% --os-version $VERSION --src rpi0-i2s-audio
#RUN find . -type f -name "*.ko" -exec cp {} . \;

#
# Target image
#

# NOTE: Must be built for Aarch64 to correctly run on pi 4

FROM debian:buster-slim as target

# Enable OpenRC
ENV INITSYSTEM on 
ENV UDEV=on

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential git zlib1g-dev libjpeg-dev libfreetype6-dev libffi-dev libportaudio2 alsa-utils python3 python3-pip

# Fix pip & install needed dependencies
RUN pip3 install --upgrade pip
RUN pip3 install -U setuptools RPI.gpio numpy spidev Pillow paho-mqtt smbus smbus2 sounddevice enviroplus
RUN pip3 install flask==2.2.*

#COPY --from=build /usr/src/app/*.ko .

# Pull in Enviroplus examples
RUN echo Pull repo...
RUN git clone https://github.com/DynamicDevices/enviroplus-python.git && cd enviroplus-python && git checkout 8d331d861a06764ad3bd216d17e4141e9f94d91e

# Copy our bits and bobs over
COPY ./src/ .
EXPOSE 8091
CMD python3 ./app.py