"""
THE CHIEF OF STAFF
System Audit Module: Performs comprehensive health check before production.

Audits all departments, tools, credentials, and storage before factory startup.
"""

import os
import shutil
import subprocess
from typing import Dict, List, Tuple


def check_folder(path: str, create_if_missing: bool = True) -> Tuple[bool, str]:
    """
    Check if a folder exists, optionally create it.
    
    Args:
        path: Folder path to check
        create_if_missing: If True, create folder if it doesn't exist
        
    Returns:
        Tuple of (exists, message)
    """
    if os.path.exists(path):
        return True, f"✓ {path}"
    elif create_if_missing:
        try:
            os.makedirs(path, exist_ok=True)
            return True, f"✓ {path} (created)"
        except Exception as e:
            return False, f"✗ {path} (failed to create: {e})"
    else:
        return False, f"✗ {path} (missing)"


def check_tool(tool_name: str, command: List[str] = None) -> Tuple[bool, str]:
    """
    Check if a system tool is accessible.
    
    Args:
        tool_name: Name of the tool
        command: Command to run for verification (default: [tool_name, '--version'])
        
    Returns:
        Tuple of (available, message)
    """
    if command is None:
        command = [tool_name, '--version']
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            timeout=5,
            text=True
        )
        if result.returncode == 0 or result.returncode == 1:  # Some tools return 1 for --version
            return True, f"✓ {tool_name} available"
        else:
            return False, f"✗ {tool_name} not accessible"
    except FileNotFoundError:
        return False, f"✗ {tool_name} not found"
    except subprocess.TimeoutExpired:
        return False, f"✗ {tool_name} timeout"
    except Exception as e:
        return False, f"✗ {tool_name} error: {e}"


def check_api_key(key_name: str, required: bool = False) -> Tuple[bool, str]:
    """
    Check if an API key exists in .env file.
    
    Args:
        key_name: Name of the API key variable
        required: If True, returns warning if missing
        
    Returns:
        Tuple of (exists, message)
    """
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        value = os.getenv(key_name)
        if value:
            return True, f"✓ {key_name} configured"
        elif required:
            return False, f"⚠️ {key_name} missing (required)"
        else:
            return True, f"⚠️ {key_name} missing (optional, fallback available)"
    except Exception as e:
        return False, f"✗ {key_name} check failed: {e}"


def check_disk_space(path: str = ".", min_gb: float = 1.0) -> Tuple[bool, str]:
    """
    Check available disk space.
    
    Args:
        path: Path to check
        min_gb: Minimum required GB
        
    Returns:
        Tuple of (sufficient, message)
    """
    try:
        stat = shutil.disk_usage(path)
        available_gb = stat.free / (1024 ** 3)
        
        if available_gb >= min_gb:
            return True, f"✓ {available_gb:.2f} GB available"
        else:
            return False, f"⚠️ {available_gb:.2f} GB available (recommend {min_gb} GB+)"
    except Exception as e:
        return True, f"⚠️ Could not check disk space: {e}"


def perform_system_audit() -> Dict[str, List[Tuple[bool, str]]]:
    """
    Perform comprehensive system audit.
    
    Returns:
        Dictionary with department names as keys and lists of (status, message) tuples
    """
    print("=" * 60)
    print("🔍 SYSTEM AUDIT - Chief of Staff Report")
    print("=" * 60)
    print()
    
    audit_results = {}
    
    # 1. INVENTORY: Check folders
    print("[📦 INVENTORY DEPT] Checking asset folders...")
    inventory_checks = []
    
    folders = [
        ("assets/music", True),
        ("assets/sfx", True),
        ("assets/sfx/risers", False),
        ("assets/sfx/impacts", False),
        ("assets/sfx/whooshes", False),
        ("fonts", True),
        ("temp", True),
        ("config", True),
        ("departments/intelligence", False),
        ("departments/production", False),
        ("departments/quality_control", False),
        ("departments/logistics", False),
    ]
    
    for folder_path, create_if_missing in folders:
        exists, message = check_folder(folder_path, create_if_missing)
        inventory_checks.append((exists, message))
        status_icon = "✅" if exists else "❌"
        print(f"   {status_icon} {message}")
    
    audit_results["Inventory"] = inventory_checks
    print()
    
    # 2. TOOLS: Check system tools
    print("[🛠️ TOOLS DEPT] Checking system tools...")
    tools_checks = []
    
    tools = [
        ("ffmpeg", ["ffmpeg", "-version"]),
        ("imagemagick", ["convert", "-version"]),
        ("piper", ["piper", "--version"]),
    ]
    
    for tool_name, command in tools:
        available, message = check_tool(tool_name, command)
        tools_checks.append((available, message))
        status_icon = "✅" if available else "⚠️"
        print(f"   {status_icon} {message}")
    
    audit_results["Tools"] = tools_checks
    print()
    
    # 3. CREDENTIALS: Check API keys
    print("[🔐 CREDENTIALS DEPT] Checking API keys...")
    credentials_checks = []
    
    api_keys = [
        ("GEMINI_API_KEY", True),  # Required
        ("GROQ_API_KEY", True),     # Required
        ("ELEVENLABS_API_KEY", False),  # Optional
        ("PEXELS_API_KEY", False),  # Optional
    ]
    
    for key_name, required in api_keys:
        exists, message = check_api_key(key_name, required)
        credentials_checks.append((exists, message))
        status_icon = "✅" if exists else "⚠️"
        print(f"   {status_icon} {message}")
    
    # Check YouTube API credentials
    client_secrets_exists = os.path.exists("client_secrets.json")
    credentials_checks.append((client_secrets_exists, 
                              "✓ client_secrets.json found" if client_secrets_exists 
                              else "⚠️ client_secrets.json missing (upload disabled)"))
    status_icon = "✅" if client_secrets_exists else "⚠️"
    print(f"   {status_icon} {'✓ client_secrets.json found' if client_secrets_exists else '⚠️ client_secrets.json missing (upload disabled)'}")
    
    audit_results["Credentials"] = credentials_checks
    print()
    
    # 4. STORAGE: Check disk space
    print("[💾 STORAGE DEPT] Checking disk space...")
    storage_checks = []
    
    sufficient, message = check_disk_space(".", min_gb=1.0)
    storage_checks.append((sufficient, message))
    status_icon = "✅" if sufficient else "⚠️"
    print(f"   {status_icon} {message}")
    
    audit_results["Storage"] = storage_checks
    print()
    
    # Summary
    print("=" * 60)
    print("📊 AUDIT SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for dept_name, checks in audit_results.items():
        dept_passed = all(status for status, _ in checks)
        status_icon = "✅" if dept_passed else "⚠️"
        print(f"{status_icon} {dept_name}: {'PASS' if dept_passed else 'WARNINGS'}")
        if not dept_passed:
            all_passed = False
    
    print()
    if all_passed:
        print("✅ SYSTEM READY FOR PRODUCTION")
    else:
        print("⚠️ SYSTEM READY (with warnings - fallbacks available)")
    
    print("=" * 60)
    print()
    
    return audit_results


if __name__ == "__main__":
    # Run audit standalone
    perform_system_audit()
