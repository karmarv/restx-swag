#!/bin/bash
# 
# __authors__     = ["Rahul Vishwakarma"]
# __contact__     = "_"
# __copyright__   = "_"
# __date__        = "2024/05/04"

# REST Web App Deployment Path and Packages
export APP_LOCAL_PATH=$PWD/
echo "App Deployment Path: ${APP_LOCAL_PATH}"

SERVER_LOG_FILE=$APP_LOCAL_PATH/logs/rest.log
touch $SERVER_LOG_FILE

function deploy_artifacts(){
  echo "------ #0: Deploy Model/Weights (Flask) ------"
  # [TODO] Copy anomaly weights to the params folder
  #cp descriptive/lookup_table.csv $APP_LOCAL_PATH/params/
}

if [ "$1" ]; then
  echo "Stop"
  # Kill started flask process
  kill -9 `cat $HOME/pid-rest.nohup`
  kill -9 `cat $HOME/pid-job.nohup`
  rm $HOME/pid-rest.nohup
  rm $HOME/pid-job.nohup
  # Ultimately devastate flask processes
  kill $(pgrep -f flask)
else
  echo "Start and Deploy"
  # Copy and deploy artifacts for model execution
  deploy_artifacts
  echo "------ #1: Launch REST API ------"
  cd $APP_LOCAL_PATH/src/rest 
  nohup flask run --host=0.0.0.0 --port=5000   2>&1 | tee -a $SERVER_LOG_FILE &
  echo $! > $HOME/pid-rest.nohup
  
  echo "------ #2: Launch REST API ------"
  cd $APP_LOCAL_PATH/src/job 
  nohup flask run --host=0.0.0.0 --port=5001   2>&1 | tee -a $SERVER_LOG_FILE &
  echo $! > $HOME/pid-job.nohup
fi

# TODO - replace above with NGINX -> https://stackoverflow.com/questions/24941791/starting-flask-server-in-background
