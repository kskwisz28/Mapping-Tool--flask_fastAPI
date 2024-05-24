#!/bin/bash

echo "Loading neo4j dump"
echo "=================="
/var/lib/neo4j/bin/neo4j-admin load --from=/neo4j-data/db.dump --force
echo "=================="
echo "Done"

/docker-entrypoint.sh neo4j
