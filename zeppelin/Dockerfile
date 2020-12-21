FROM  apache/zeppelin:0.8.0 as builder
WORKDIR /zeppelin

LABEL maintainer = "James Troy"

FROM jtroy/spark-base:0.1
WORKDIR /zeppelin/
COPY --from=builder /zeppelin    .

ENV SPARK_HOME "/usr/spark"
EXPOSE 8080 8443 4040
RUN apt-get update -y \
    && DEBIAN_FRONTEND=noninteractive apt-get install  python3-pip python-lxml python-html5lib  --no-install-recommends -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN echo '{ "allow_root": true }' > /root/.bowerrc
COPY requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir

RUN rm requirements.txt

#Add extra pip packages here if required
CMD ["bash", "/zeppelin/bin/zeppelin.sh"]
