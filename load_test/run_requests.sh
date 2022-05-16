# !/bin/bash

# run some requests against DCDL test app 

set -e

pid=""

# add another for loop with index, then inner for loop makes 16 concurrent processes
for i in {0..15}
do
    for jbid in "jbid123" "jbid456" "jbid789" "jbid999"
    do
        echo "making requests for $jbid..."
        python make_requests.py $jbid &
        pid=$! 
    done
    # wait $pid
done