#!/bin/bash
cd /home/kavia/workspace/code-generation/authtaskmanager-34938-54a51c74/task_management_frontend_workspace/task_management_frontend
npm run build
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
   exit 1
fi

