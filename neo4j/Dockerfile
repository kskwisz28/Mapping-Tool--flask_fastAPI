FROM neo4j:latest

ENV NEO4J_AUTH=neo4j/test123
ENV NEO4J_dbms_allow__upgrade=true
ENV NEO4J_ACCEPT_LICENSE_AGREEMENT=yes
EXPOSE 7474 7473 7687


COPY wrapper.sh wrapper.sh
RUN chmod +x wrapper.sh

ENTRYPOINT ["./wrapper.sh"]

# COPY dumps/db.dump /neo4j-data/db.dump
# RUN /var/lib/neo4j/bin/neo4j-admin load --from=/data/db.dump 

