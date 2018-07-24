FROM alpine:edge AS resource

ARG http_proxy
ARG author

ENV http_proxy=$http_proxy
ENV https_proxy=$http_proxy

RUN echo -e "http_proxy=$http_proxy\nhttps_proxy=$https_proxy" >> /etc/environment

RUN apk add --no-cache \
    python3 \
    python3-dev \
    make

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
RUN apk remove make
