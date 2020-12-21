#FROM bigdata-docker-compose_master:latest
FROM jtroy/spark-base:0.1

ARG LIVY_VERSION=0.7.0-incubating
ENV LIVY_HOME /usr/livy
ENV LIVY_CONF_DIR "${LIVY_HOME}/conf"
RUN curl \
    "http://archive.apache.org/dist/incubator/livy/${LIVY_VERSION}/apache-livy-${LIVY_VERSION}-bin.zip" \
    -o "./apache-livy-${LIVY_VERSION}-bin.zip" \
  && unzip -qq "./apache-livy-${LIVY_VERSION}-bin.zip" -d /usr \
  && mv "/usr/apache-livy-${LIVY_VERSION}-bin" "${LIVY_HOME}" \
  && rm -rf "./apache-livy-${LIVY_VERSION}-bin.zip" \
  && mkdir "${LIVY_HOME}/logs"
WORKDIR ${LIVY_HOME}
COPY entrypoint.sh .

ENTRYPOINT ["bash", "./entrypoint.sh"]