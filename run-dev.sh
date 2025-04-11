#!/bin/bash

cleanup() {
    echo "Caught signal or exiting, stopping Flask..."
    if [ ! -z "$FLASK_PID" ] && ps -p $FLASK_PID > /dev/null; then
        echo "Sending SIGTERM to Flask process $FLASK_PID"
        kill $FLASK_PID
        sleep 2
        if ps -p $FLASK_PID > /dev/null; then
            echo "Flask process $FLASK_PID did not terminate gracefully, sending SIGKILL"
            kill -9 $FLASK_PID
        fi
    else
        echo "Flask process ($FLASK_PID) already stopped or not found."
    fi
    wait $FLASK_PID 2>/dev/null
    echo "Cleanup finished."
}

trap cleanup SIGINT SIGTERM EXIT

echo "Starting proxy..."
cd dev-proxy
flask run &

FLASK_PID=$!
echo "Flask running with PID: $FLASK_PID"

sleep 1
if ! ps -p $FLASK_PID > /dev/null; then
    echo "Error: Flask process failed to start."
    exit 1
fi

cd ..

echo "Starting sam local start-lambda in the foreground..."
sam local start-lambda --debug
 
exit 0