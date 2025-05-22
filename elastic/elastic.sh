#!/bin/bash

set -e


wait_for_elasticsearch() {
  echo "Waiting for Elasticsearch to start..."
  until curl -s "http://elasticsearch:9200/_cat/health?h=status" | grep -E -q "(yellow|green)"; do
    sleep 2
  done
  echo "Elasticsearch started."
}


INDEXES_PATH="/opt/elastic/etl_indexes"


create_data_index() {
  local index_name="$1"


  local index_exists
  index_exists=$(curl -s -o /dev/null -w "%{http_code}" "http://elasticsearch:9200/${index_name}")

  if [ "$index_exists" -ne 200 ]; then
    echo "Creating index '${index_name}'..."


    if curl -XPUT "http://elasticsearch:9200/${index_name}" \
      -H "Content-Type: application/json" \
      --data-binary "@${INDEXES_PATH}/${index_name}.json"; then
      echo "Index '${index_name}' created successfully."
    else
      echo "Failed to create index '${index_name}'."
      exit 1
    fi
  else
    echo "Index '${index_name}' already exists. Skipping index creation."
  fi
}


if [ ! -d "${INDEXES_PATH}" ]; then
  echo "Directory '${INDEXES_PATH}' does not exist. Please check the path."
  exit 1
fi


wait_for_elasticsearch


for index_file in "${INDEXES_PATH}"/*.json; do
  index_name=$(basename "${index_file}" .json)
  create_data_index "${index_name}"
done


python /opt/elastic/main.py
