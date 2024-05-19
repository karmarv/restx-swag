#!/bin/bash
# 
# __authors__     = ["Rahul Vishwakarma"]
# __contact__     = "_"
# __copyright__   = "_"
# __date__        = "2024/05/04"

# REST Web App Deployment Path and Packages
export APP_DEPLOYMENT_PATH=$PWD/
echo "App Deployment Path: ${APP_DEPLOYMENT_PATH}"


WORKER_ID=0
if [ "$#" -eq  "0" ]
  then
    echo "No worker number supplied in argument. Try using 0 in the argument !!"
    exit 1
  else
    WORKER_ID=$1
fi

#rq empty --all
WORKER_LOG_FILE=$APP_DEPLOYMENT_PATH/logs/rq-worker-$WORKER_ID.log
touch $WORKER_LOG_FILE

echo ">> List existing workers"
ps -eaf | grep /bin/rq

echo ">> Launch RQ Worker -> #$WORKER_ID with log at $WORKER_LOG_FILE"
cd $APP_DEPLOYMENT_PATH/src/ && python worker/work.py  2>&1 | tee -a $WORKER_LOG_FILE