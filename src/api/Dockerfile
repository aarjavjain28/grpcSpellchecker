ARG PYTHON_VERSION

FROM python:3.10.11-slim


RUN apt-get update && \
    apt-get install -y tree && \
    apt-get install -y wget && \
    apt-get install -y make && \
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda && \
    rm -f Miniconda3-latest-Linux-x86_64.sh && \
    /opt/conda/bin/conda clean -afy && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc

ENV PATH /opt/conda/bin:$PATH


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


RUN conda install -c conda-forge icu

ENV PATH="/opt/icu4c/bin:$PATH"
ENV PATH="/opt/icu4c/sbin:$PATH"


#RUN icu-config --version
#RUN echo icu-config --version
RUN export ICU_VERSION=70.1



ENV LC_ALL=en_US.utf8
#ENV LANG=en_US.utf8

#RUN yum install -y libicu
ENV CONFIG_FILE_PATH="config.yaml"

EXPOSE 8080
#RUN pwd

ENV PYTHONUNBUFFERED True


## Set shell to run subsequent commands in the Conda environment
#SHELL ["conda", "run", "-n", "app", "/bin/bash", "-c"]
#
## Generate Proto files and run service

#RUN apt-get install build-essential
#RUN conda run /bin/bash -c make
RUN make
RUN pip install pycld2==0.41 httptools grpcio grpcio-tools
CMD ["sh", "-c", "python service.py --port ${PORT}"]
