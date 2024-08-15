FROM jgwill/jgt:fxcon
#jgwill/ubuntu:py3.10.14-ml

#RUN pip uninstall jgtfxcon -y && \
#RUN pip install -U --index-url https://test.pypi.org/simple/ jgtfxcon
RUN pip uninstall jgtfxcon -y &> /dev/null
WORKDIR /dist
RUN rm -rf *.tar.gz *.whl
COPY ./dist .
RUN pip install *.whl #--force-reinstall
WORKDIR /work

