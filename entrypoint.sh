# entrypoint.sh

#!/bin/bash

if [ "$1" = "generate_trades" ]; then
    python generate_trades.py
elif [ "$1" = "execute_trades" ]; then
    python execute_trades.py
else
    echo "Unknown command"
    exit 1
fi
