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

set -a # automatically export all variables
source .flaskenv
set +a

function prepare_artifacts(){
  echo "------ #1: Prepare Model/Weights ------"
  # [TODO] Copy anomaly weights to the params folder
  #cp descriptive/lookup_table.csv $APP_LOCAL_PATH/params/
}

function check_kill_process(){
  FILE_PID_JOB=$HOME/pid-job.nohup
  FILE_PID_RST=$HOME/pid-rest.nohup
  if [ -f "$FILE_PID_JOB" ] || [ -f "$FILE_PID_RST" ]; then
      echo "------ #0: Kill existing server (Flask) ------"
      echo "$FILE_PID_JOB exists."
      # Kill started flask process
      kill -9 `cat $FILE_PID_JOB`
      kill -9 `cat $FILE_PID_RST`
      # Ultimately devastate flask processes
      kill $(pgrep -f flask)
  else 
      echo "$FILE_PID_JOB does not exist."
  fi
  rm $FILE_PID_JOB
  rm $FILE_PID_RST
}

if [ "$1" ]; then
  echo "Stop"
  check_kill_process
else
  echo "Start and Deploy"
  # Copy and deploy artifacts for model execution
  prepare_artifacts
  check_kill_process
  echo "------ #2: Launch REST API ------"
  cd $APP_LOCAL_PATH/src/rest 
  nohup flask run --host=0.0.0.0 --port=5000   2>&1 | tee -a $SERVER_LOG_FILE &
  echo $! > $HOME/pid-rest.nohup
  echo "App Services: http://0.0.0.0:5000/api/v1/"
  
  echo "------ #3: Launch REST API ------"
  cd $APP_LOCAL_PATH/src/job 
  nohup flask run --host=0.0.0.0 --port=5001   2>&1 | tee -a $SERVER_LOG_FILE &
  echo $! > $HOME/pid-job.nohup
  echo "Job Services: http://0.0.0.0:5001/api/v1/"
fi

# TODO - replace above with NGINX -> https://stackoverflow.com/questions/24941791/starting-flask-server-in-background
