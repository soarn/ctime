#!/bin/bash
# Parse the DB_SECRET JSON and set CONNECTION_STRING
export CONNECTION_STRING="mysql+pymysql://$(echo $DB_SECRET | jq -r '.username'):$(echo $DB_SECRET | jq -r '.password')@$(echo $DB_SECRET | jq -r '.host'):3306/$(echo $DB_SECRET | jq -r '.dbname')"