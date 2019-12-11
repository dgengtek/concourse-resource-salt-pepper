FROM docker.p.intranet.dgeng.eu/python:3.8-slim-buster AS resource

RUN apt-get update \
  && apt-get install -y make

ADD assets/ /opt/resource/
RUN chmod +x /opt/resource/*

WORKDIR /concsp
ADD . /concsp/
    
RUN make install && make clean

RUN rm -rf /tmp/* \
  && rm -rf /var/cache/apk/* \
  && rm -rf /root/.cache/


FROM resource AS tests
WORKDIR /concsp
RUN make test

FROM resource
RUN apt-get purge -y make \
  && apt-get autoremove -y \
  && apt-get autoclean -y
