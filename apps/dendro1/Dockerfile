FROM python:3.9

RUN mkdir /src

# Install pynwb
RUN pip install pynwb==2.5.0

# Install spikeinterface
RUN pip install spikeinterface==0.99.1

# Install pynapple
RUN pip install pynapple==0.5.0

# Install mountainsort5
RUN pip install mountainsort5==0.5.3

# Install dendro
RUN pip install dendro==0.1.32

# # Install dendro from source
# RUN git clone https://github.com/flatironinstitute/dendro.git /src/dendro && \
#     echo "attempt1" && \
#     cd /src/dendro && \
#     git checkout folder-support && \
#     cd python && \
#     pip install -e .

# Copy files into the container
RUN mkdir /app
COPY apps/dendro1/*.py /app/
COPY apps/dendro1/folder_io/*.py /app/folder_io/
COPY apps/dendro1/quip/*.py /app/quip/
COPY apps/dendro1/tuning_curves_2d/*.py /app/tuning_curves_2d/
