export $(cat ../../.env-dev | sed 's/#.*//g' | xargs)
