#!/bin/bash
# Simple script to fix logging - replaces multi-line structured logging with f-string logging

for file in connection_tracker.py shutdown_manager.py fastapi_integration.py standalone.py; do
    echo "Processing $file..."
    
    # Backup
    cp "$file" "${file}.bak"
    
    # Replace common patterns using Python for more complex transformations
    python3 << 'PYTHON' "$file"
import sys
import re

with open(sys.argv[1], 'r') as f:
    content = f.read()

# Replace logger.debug("msg", key=value) with logger.debug(f"msg: key={value}")
def fix_simple_log(match):
    level = match.group(1)
    msg = match.group(2)
    key = match.group(3)
    val = match.group(4)
    return f'logger.{level}(f"{msg}: {key}={{{val}}}")'

content = re.sub(
    r'logger\.(debug|info|warning|error)\("([^"]+)",\s+(\w+)=(.+)\)',
    fix_simple_log,
    content
)

# Replace multi-line logging
def fix_multiline_log(match):
    indent = match.group(1)
    level = match.group(2)
    msg = match.group(3)
    rest = match.group(4)
    
    # Extract key=value pairs
    pairs = re.findall(r'(\w+)=([^,\n]+)', rest)
    if pairs:
        args_str = ", ".join([f"{k}={{{v.strip()}}}" for k, v in pairs])
        return f'{indent}logger.{level}(f"{msg}: {args_str}")'
    else:
        return f'{indent}logger.{level}("{msg}")'

content = re.sub(
    r'(\s+)logger\.(debug|info|warning|error)\(\s*"([^"]+)",\s*\n([^)]+\))',
    fix_multiline_log,
    content
)

with open(sys.argv[1], 'w') as f:
    f.write(content)

PYTHON
done

echo "Done!"
