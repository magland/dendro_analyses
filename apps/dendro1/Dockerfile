FROM python:3.9

RUN mkdir /src

# Install pynwb
RUN pip install pynwb==2.5.0

# Install pynapple
RUN pip install pynapple==0.5.0

# Install dendro
# RUN pip install dendro==0.1.24

# Install dendro from source
RUN git clone https://github.com/flatironinstitute/dendro.git /src/dendro && \
    echo "attempt1" && \
    cd /src/dendro && \
    git checkout folder-support && \
    cd python && \
    pip install -e .

# Copy files into the container
RUN mkdir /app
COPY apps/dendro1/*.py /app/
