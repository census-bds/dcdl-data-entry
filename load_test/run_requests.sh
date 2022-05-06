# !/bin/bash

# run some requests against DCDL test app 

set -e

for jbid in "jbid123" "jbid456" "jbid789" "jbid999"
do
    echo "making requests for $jbid..."
    python make_requests.py $jbid
done