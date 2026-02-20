#!/usr/bin/env python3
"""
Fix logging statements in shutdown modules
Convert from logger.info("msg", key=value) to logger.info(f"msg: key={value}")
"""

import re
import sys

def fix_logging_in_file(filepath):
    """Fix logging statements in a file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern 1: logger.info("msg", key1=val1, key2=val2) -> logger.info(f"msg: key1={val1}, key2={val2}")
    # Pattern 2: logger.debug("msg", key=val) -> logger.debug(f"msg: key={val}")
    
    # Replace multi-line logging with keyword args
    def replace_multiline(match):
        indent = match.group(1)
        level = match.group(2)
        msg = match.group(3)
        args = match.group(4)
        
        # Parse keyword arguments
        arg_pattern = r'(\w+)=([^,\n]+)'
        arg_matches = re.findall(arg_pattern, args)
        
        if arg_matches:
            args_str = ", ".join([f"{k}={v}" for k, v in arg_matches])
            return f'{indent}logger.{level}(f"{msg}: {args_str}")'
        else:
            return f'{indent}logger.{level}("{msg}")'
    
    # Fix multi-line logging statements
    content = re.sub(
        r'(\s+)(logger\.(info|debug|warning|error))\(\s*\n?\s*"([^"]+)",\s*\n?\s*([^)]+)\)',
        replace_multiline,
        content
    )
    
    # Fix single-line logging with keyword args
    def replace_singleline(match):
        level = match.group(1)
        msg = match.group(2)
        args = match.group(3)
        
        # Parse keyword arguments
        arg_pattern = r'(\w+)=([^,\)]+)'
        arg_matches = re.findall(arg_pattern, args)
        
        if arg_matches:
            args_str = ", ".join([f"{k}={v}" for k, v in arg_matches])
            return f'logger.{level}(f"{msg}: {args_str}")'
        else:
            return f'logger.{level}("{msg}")'
    
    content = re.sub(
        r'logger\.(info|debug|warning|error)\("([^"]+)",\s+([^)]+)\)',
        replace_singleline,
        content
    )
    
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Fixed logging in {filepath}")
        return True
    else:
        print(f"No changes needed in {filepath}")
        return False

if __name__ == "__main__":
    files = [
        "/home/ubuntu/.openclaw/workspace/QA-FRAMEWORK/src/infrastructure/shutdown/connection_tracker.py",
        "/home/ubuntu/.openclaw/workspace/QA-FRAMEWORK/src/infrastructure/shutdown/shutdown_manager.py",
        "/home/ubuntu/.openclaw/workspace/QA-FRAMEWORK/src/infrastructure/shutdown/fastapi_integration.py",
        "/home/ubuntu/.openclaw/workspace/QA-FRAMEWORK/src/infrastructure/shutdown/standalone.py",
    ]
    
    for filepath in files:
        try:
            fix_logging_in_file(filepath)
        except Exception as e:
            print(f"Error fixing {filepath}: {e}")
