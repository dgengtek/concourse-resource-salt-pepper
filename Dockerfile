ARG dockerfile_from_image=debian:bullseye-slim
FROM ${dockerfile_from_image} as build

ARG http_proxy
ARG author
ARG version

ENV http_proxy=$http_proxy
ENV https_proxy=$http_proxy

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


FROM build
RUN apt-get purge -y make \
  && apt-get autoremove -y \
  && apt-get autoclean -y
