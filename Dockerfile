FROM alpine:edge

RUN apk add --no-cache \
    python3 \
    python3-dev

ADD src/bin /opt/resource/
ADD src/lib /opt/resource/
ADD requirements.txt /tmp

RUN chmod +x /opt/resource/* \
    && pip install -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# Do some clean up
RUN rm -rf /tmp/* \
  && rm -rf /var/cache/apk/* \
  && rm -rf /root/.cache/
