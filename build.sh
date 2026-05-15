#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg
# Render's environment is Ubuntu-based
apt-get update && apt-get install -y ffmpeg
