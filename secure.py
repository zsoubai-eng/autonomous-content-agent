#!/usr/bin/env python3
import os
import sys
import subprocess
import re

# Sensitive patterns
SECRET_PATTERNS = [
    r"sk-[a-zA-Z0-9]{48}",      # OpenAI
    r"AIza[a-zA-Z0-9\-_]{35}",  # Google AIza
    r"ya29\.[a-zA-Z0-9\-_]+",   # Google OAuth
]

GIT_IGNORED_SECRETS = [
    ".env",
    "token.json",
    "credentials.json",
    "client_secrets.json",
    "session.json",
]

def check_gitignore():
    if not os.path.exists(".gitignore"):
        print("\033[91m❌ ERROR: .gitignore missing!\033[0m")
        return False
    
    with open(".gitignore", "r") as f:
        content = f.read()
    
    missing = []
    for secret in GIT_IGNORED_SECRETS:
        if secret not in content:
            missing.append(secret)
    
    if missing:
        print(f"\033[91m❌ ERROR: .gitignore is missing these required secrets: {', '.join(missing)}\033[0m")
        return False
    return True

def check_staged_secrets():
    try:
        staged_files = subprocess.check_output(["git", "diff", "--cached", "--name-only"], text=True).splitlines()
        for file in staged_files:
            if file in GIT_IGNORED_SECRETS:
                print(f"\033[91m❌ ERROR: Sensitive file '{file}' is staged for commit!\033[0m")
                return False
            
            # Check content of staged file if it's text
            try:
                content = subprocess.check_output(["git", "show", f":{file}"], text=True)
                for pattern in SECRET_PATTERNS:
                    if re.search(pattern, content):
                        print(f"\033[91m❌ SECRET DETECTED in staged file '{file}' – ABORT\033[0m")
                        return False
            except:
                pass # Binary or other error
    except subprocess.CalledProcessError:
        pass # Not a git repo or no staged files
    return True

def check_all_files():
    # Only check files that are NOT ignored by git
    try:
        # Get list of all files in repo (excluding ignored ones)
        tracked_files = subprocess.check_output(["git", "ls-files"], text=True).splitlines()
        untracked_files = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"], text=True).splitlines()
        
        for file in tracked_files + untracked_files:
            # Skip checking the secrets themselves (they are already in .gitignore)
            if any(secret in file for secret in GIT_IGNORED_SECRETS):
                continue
            
            if os.path.isfile(file):
                try:
                    with open(file, "r") as f:
                        content = f.read()
                        for pattern in SECRET_PATTERNS:
                            if re.search(pattern, content):
                                print(f"\033[91m❌ SECRET DETECTED in '{file}' – ABORT\033[0m")
                                return False
                except:
                    pass
    except subprocess.CalledProcessError:
        # Not a git repo, fall back to broad check (original logic)
        pass
    
    return True

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Post-run safety check")
    args = parser.parse_args()

    success = True
    
    if not check_gitignore():
        success = False
        
    if not check_staged_secrets():
        success = False
        
    if not check_all_files():
        success = False

    if success:
        print("\033[92m✅ Security check passed.\033[0m")
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
