#!/usr/bin/env bash
# Helper script to activate environment and start JupyterLab
# Usage: bash scripts/start_jupyter.sh

ENV_NAME="phonepe-insights"

if conda env list | grep -q "${ENV_NAME}"; then
  echo "Activating conda env: ${ENV_NAME}"
  source "$(conda info --base)/etc/profile.d/conda.sh"
  conda activate "${ENV_NAME}"
else
  echo "Conda env ${ENV_NAME} not found. Starting jupyter in current environment."
fi

jupyter lab --no-browser --ip=0.0.0.0
