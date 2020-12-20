FROM  apache/zeppelin:0.8.0 as builder
WORKDIR /zeppelin

LABEL maintainer = "James Troy"

FROM jtroy/spark-base:0.1
WORKDIR /zeppelin/
COPY --from=builder /zeppelin    .

RUN apt-get update -y && \
    apt-get upgrade -y

ENV SPARK_HOME "/usr/spark"
RUN echo '{ "allow_root": true }' > /root/.bowerrc

EXPOSE 8080 8443 4040

CMD ["/zeppelin/bin/zeppelin.sh"]
