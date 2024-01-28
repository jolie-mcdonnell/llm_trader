#!/bin/bash

if [ "$1" = "generate_trades" ]; then
    exec python generate_trades.py
elif [ "$1" = "execute_trades" ]; then
    exec python execute_trades.py
else
    echo "Unknown command"
    exit 1
fi
