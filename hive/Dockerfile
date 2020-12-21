FROM jtroy/spark-base:0.1
LABEL maintainer = "James Troy"


ENV HIVE_VERSION 3.1.2

ENV HIVE_HOME /opt/hive
ENV PATH ${HIVE_HOME}/bin:$PATH

WORKDIR /opt

# Install Hive and PostgreSQL JDBC
RUN apt-get update && \
	curl https://ftp.heanet.ie/mirrors/www.apache.org/dist/hive/hive-${HIVE_VERSION}/apache-hive-${HIVE_VERSION}-bin.tar.gz  -o apache-hive-$HIVE_VERSION-bin.tar.gz && \
	tar -xzvf apache-hive-$HIVE_VERSION-bin.tar.gz && \
	mv apache-hive-$HIVE_VERSION-bin hive && \
	rm apache-hive-${HIVE_VERSION}-bin.tar.gz && \
	curl https://jdbc.postgresql.org/download/postgresql-42.1.4.jar -o ${HIVE_HOME}/lib/postgresql-jdbc.jar && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/*


#Custom configuration goes here
ADD conf/hive-site.xml ${HIVE_HOME}/conf
ADD conf/beeline-log4j2.properties ${HIVE_HOME}/conf
ADD conf/hive-exec-log4j2.properties ${HIVE_HOME}/conf
ADD conf/hive-log4j2.properties ${HIVE_HOME}/conf
ADD conf/llap-daemon-log4j2.properties ${HIVE_HOME}/conf
ADD conf/ivysettings.xml ${HIVE_HOME}/conf
ADD conf/hive-env.sh ${HIVE_HOME}/conf

COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["bash", "/usr/local/bin/entrypoint.sh"]
