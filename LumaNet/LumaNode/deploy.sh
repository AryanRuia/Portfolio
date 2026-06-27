#!/bin/bash

echo "Building LumaNet..."
cd ~/lumanet/server
npm run build

echo "Building client..."
cd ~/lumanet/client
npm run build

echo "Restarting service..."
sudo systemctl restart lumanet

echo "Checking status..."
sudo systemctl status lumanet --no-pager

echo "Deployment complete!"
