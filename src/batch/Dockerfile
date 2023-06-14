ARG PYTHON_VERSION

FROM nvcr.io/nvidia/nemo:1.6.1

ARG PROJECT_NAME
ARG ML_PRODUCT
ARG PYTHON_VERSION

ENV PROJECT_NAME=$PROJECT_NAME
ENV ML_PRODUCT=$ML_PRODUCT

COPY app/ /app/
WORKDIR /app/

# Nemo images comes with python 3.8 installed.
RUN conda create -n app python=$PYTHON_VERSION
RUN echo "source activate app" > ~/.bashrc
ENV PATH /opt/conda/envs/app/bin:$PATH

# Set shell to run subsequent commands in the Conda environment
SHELL ["conda", "run", "-n", "app", "/bin/bash", "-c"]

RUN pip install --upgrade pip
RUN pip install keyrings.google-artifactregistry-auth
RUN pip install -r /app/requirements.txt
