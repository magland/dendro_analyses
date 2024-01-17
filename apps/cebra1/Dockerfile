FROM python:3.9

RUN pip install cebra==0.4.0

RUN pip install pynwb==2.5.0

RUN pip install nh5==0.1.0

RUN pip install git+https://github.com/magland/nlb_tools_fork.git

# Install dendro
RUN pip install dendro==0.1.30

# Copy files into the container
RUN mkdir /app
COPY apps/cebra1/*.py /app/
