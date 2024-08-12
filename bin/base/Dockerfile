FROM jgwill/jgt:base-miniconda
#FROM jgwill/ubuntu:py3.10.14-ml
#RUN apt update && apt install -y vim curl
#RUN pip install json2bash
#RUN pip install -U pip

WORKDIR /dist
COPY ./dist .
RUN pip install *.whl
WORKDIR /work