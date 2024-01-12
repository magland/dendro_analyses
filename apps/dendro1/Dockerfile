FROM python:3.9

RUN mkdir /src

# Install pynwb
RUN pip install pynwb==2.5.0

# Install pynapple
RUN pip install pynapple==0.5.0

# Install dendro
RUN pip install dendro==0.1.24

# Copy files into the container
RUN mkdir /app
COPY apps/dendro1/*.py /app/
