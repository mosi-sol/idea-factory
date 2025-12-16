#!/usr/bin/env python3
"""
Demo script showing how to use pyp - Python Virtual Environment Manager
This script demonstrates the key features and workflow
"""

import subprocess
import sys
import time
from pathlib import Path

def run_command(cmd, description):
    """Run a command and show the result"""
    print(f"\n🔧 {description}")
    print(f"Command: {cmd}")
    print("-" * 50)
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"Errors: {result.stderr}")
    print()

def main():
    print("🚀 pyp - Python Virtual Environment Manager Demo")
    print("=" * 55)
    
    print("""
This demo will show you how to use pyp for managing Python virtual environments.

pyp provides a simplified interface for:
- Creating virtual environments
- Activating/deactivating them
- Managing multiple environments
- Setting defaults
    """)
    
    # Show help
    run_command("python3 pyp.py --help", "Display help information")
    
    # Create first environment
    run_command("python3 pyp.py -b demo-env-1", "Create first demo environment")
    
    # Create second environment with upgrade
    run_command("python3 pyp.py -b demo-env-2 --upgrade", "Create second environment with upgrade")
    
    # List environments
    run_command("python3 pyp.py -l", "List all environments")
    
    # Show info about first environment
    run_command("python3 pyp.py -i demo-env-1", "Show detailed info about demo-env-1")
    
    # Set default environment
    run_command("python3 pyp.py --set-default demo-env-2", "Set demo-env-2 as default")
    
    # List again to show default
    run_command("python3 pyp.py -l", "List environments (showing default)")
    
    print("""
📋 Summary of pyp Commands:

Core Commands:
  pyp -b <name>        Create new environment
  pyp -a <name>        Activate environment  
  pyp -d               Deactivate current environment
  pyp -l               List all environments

Management:
  pyp -i <name>        Show environment info
  pyp --set-default <name>  Set default environment
  pyp --remove <name>  Remove environment

Options:
  --python VERSION     Use specific Python version
  --system-site-packages  Include system packages
  --upgrade           Upgrade pip/setuptools

🎯 Quick Start:
  1. Create:  pyp -b myproject
  2. Activate: pyp -a myproject  
  3. Work:     (install packages, run code)
  4. Deactivate: pyp -d

The environments are stored in ~/.pyp_envs/ and configuration
is saved in ~/.pyp_config.json
    """)
    
    # Show what was created
    print("\n📁 Files Created:")
    print(f"Configuration: ~/.pyp_config.json")
    print(f"Environments: ~/.pyp_envs/")
    
    # List the demo environments
    demo_envs_dir = Path.home() / ".pyp_envs"
    if demo_envs_dir.exists():
        print(f"\nDemo environments in {demo_envs_dir}:")
        for env_dir in demo_envs_dir.iterdir():
            if env_dir.is_dir() and env_dir.name.startswith("demo-env"):
                size = sum(f.stat().st_size for f in env_dir.rglob('*') if f.is_file())
                print(f"  📦 {env_dir.name} ({size:,} bytes)")

if __name__ == "__main__":
    main()