FROM  apache/zeppelin:0.8.0 as builder
WORKDIR /zeppelin

LABEL maintainer = "James Troy"

FROM gettyimages/spark
WORKDIR /zeppelin/
COPY --from=builder /zeppelin    .

RUN apt-get update -y && \
    apt-get upgrade -y

ENV SPARK_HOME "/usr/spark"
RUN echo '{ "allow_root": true }' > /root/.bowerrc

EXPOSE 8080
EXPOSE 8443
EXPOSE 4040

CMD ["/zeppelin/bin/zeppelin.sh"]
