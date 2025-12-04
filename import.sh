#!/bin/bash

SERVER="myserver"
DB="mydb"
USER="myuser"
PW='p$ssw0rd$!'   # single-quoted → literal $, no expansion
FOLDER="/path/to/sql"

for FILE in "$FOLDER"/*.sql; do
    echo "Running: $FILE"

    # Run sqlcmd and capture the output
    OUTPUT=$(sqlcmd -S "$SERVER" -d "$DB" -U "$USER" -P "$PW" -i "$FILE" 2>&1)
    EXIT_CODE=$?

    # Detect error
    if [ $EXIT_CODE -ne 0 ]; then
        echo "❌ ERROR detected in: $FILE"
        echo "----------------------------------"
        echo "$OUTPUT"
        echo "----------------------------------"

        # Try to extract the failing line number and print that line
        LINE=$(echo "$OUTPUT" | grep -oE "Line [0-9]+" | awk '{print $2}' | head -n 1)

        if [ -n "$LINE" ]; then
            echo "Failing line $LINE in $FILE:"
            sed -n "${LINE}p" "$FILE"
        else
            echo "Could not detect line number automatically."
        fi

        echo "Stopping script."
        exit 1
    fi
done

echo "✅ All SQL files imported successfully."
