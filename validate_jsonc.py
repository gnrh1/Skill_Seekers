#!/usr/bin/env python3
"""
Validate JSONC (JSON with Comments) files used by Factory Droid
"""
import json
import re
import sys

def strip_json_comments(text):
    """Remove // and /* */ style comments from JSON text"""
    # Remove single-line comments
    text = re.sub(r'//.*?$', '', text, flags=re.MULTILINE)
    # Remove multi-line comments
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    return text

def validate_jsonc(filepath):
    """Validate a JSONC file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Strip comments
        clean_json = strip_json_comments(content)
        
        # Parse JSON
        data = json.loads(clean_json)
        
        print(f"✅ {filepath} is valid JSONC")
        print(f"   Keys: {', '.join(data.keys())}")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ {filepath} has JSON syntax error:")
        print(f"   {e}")
        return False
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return False
    except Exception as e:
        print(f"❌ Error validating {filepath}:")
        print(f"   {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 validate_jsonc.py <file.json>")
        print("\nValidating Factory config files...")
        files = [
            "~/.factory/settings.json",
            "~/.factory/config.json"
        ]
    else:
        files = sys.argv[1:]
    
    # Expand ~ to home directory
    import os
    files = [os.path.expanduser(f) for f in files]
    
    all_valid = True
    for filepath in files:
        if not validate_jsonc(filepath):
            all_valid = False
        print()
    
    sys.exit(0 if all_valid else 1)
