#!/usr/bin/env python3
"""
pyp - Python Virtual Environment Manager
A lightweight, secure tool for managing Python virtual environments

pyp version 3

Usage:
    pyp -b myproject         Build/create a new virtual environment
    pyp -a myproject         Activate it (opens new safe shell)
    pyp -d                   Deactivate (clears tracking)
    pyp -l                   List all your environments
"""

import os
import sys
import argparse
import subprocess
import shutil
import json
import re
from pathlib import Path
from typing import Optional

class PyPManager:
    """Secure manager for Python virtual environments using pyp command"""
    
    def __init__(self):
        self.config_file = Path.home() / ".pyp_config.json"
        self.envs_dir = Path.home() / ".pyp_envs"
        self.envs_dir.mkdir(exist_ok=True, mode=0o700)  # Fix 1: only you can read/write/enter
        self.load_config()

    def load_config(self):
        """Load configuration safely - if broken, start empty"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.config = {}  # corrupt file → start fresh (safe)
        else:
            self.config = {}

    def save_config(self):
        """Save configuration with correct permissions"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            self.config_file.chmod(0o600)  # Fix 2: only you can read it
        except IOError as e:
            print(f"Warning: Could not save configuration: {e}")

    def is_valid_env_name(self, name: str) -> bool:
        """Fix 3: only allow safe characters (prevents weird names)"""
        if not name or not name.strip():
            return False
        # Only letters, numbers, underscore, hyphen (very safe for files + shell)
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', name))

    def get_current_env(self) -> Optional[str]:
        """Get currently active pyp environment safely"""
        venv_path = os.environ.get('VIRTUAL_ENV')
        if venv_path:
            for env_name, env_path in self.config.get('environments', {}).items():
                if Path(venv_path).resolve() == Path(env_path).resolve():  # Fix 4: use resolve to stop symlink tricks
                    return env_name
        return os.environ.get('PYP_CURRENT_ENV')

    def build_environment(self, env_name: str, python_version: Optional[str] = None, 
                         system_site_packages: bool = False, upgrade: bool = False) -> bool:
        if not self.is_valid_env_name(env_name):  # Fix 3 applied here
            print("Error: Environment name can only contain letters, numbers, - and _")
            print("Example: myproject, work-2025, py311")
            return False

        env_path = self.envs_dir / env_name

        # Fix 5: prevent TOCTOU race by creating directory first (atomic)
        try:
            env_path.mkdir(exist_ok=True)  # creates empty folder immediately
        except Exception as e:
            print(f"Error: Cannot create directory {env_path}: {e}")
            return False

        if env_path.exists() and any(env_path.iterdir()) and not upgrade:  # now safe check
            print(f"Error: Environment '{env_name}' already exists. Use --upgrade to recreate.")
            return False

        if upgrade and env_path.exists():
            print(f"Removing existing environment '{env_name}'...")
            shutil.rmtree(env_path)  # now safe because we created it just above

        try:
            cmd = [sys.executable, "-m", "venv", str(env_path)]
            if python_version:
                python_cmd = f"python{python_version}"
                try:
                    subprocess.run([python_cmd, "--version"], capture_output=True, check=True)
                    cmd = [python_cmd, "-m", "venv", str(env_path)]
                except:
                    print(f"Warning: Python {python_version} not found → using current Python")

            if system_site_packages:
                cmd.append("--system-site-packages")

            print(f"Creating secure virtual environment '{env_name}'...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Error creating environment: {result.stderr}")
                return False

            # Store in config (path is always inside ~/.pyp_envs → safe)
            if 'environments' not in self.config:
                self.config['environments'] = {}
            self.config['environments'][env_name] = str(env_path.resolve())  # Fix 4: store resolved path

            if 'default_env' not in self.config:
                self.config['default_env'] = env_name

            self.save_config()
            print(f"✓ Created secure environment '{env_name}' at {env_path}")

            if upgrade:
                self.upgrade_environment(env_name)
            return True

        except Exception as e:
            print(f"Error: {e}")
            return False

    def upgrade_environment(self, env_name: str) -> bool:
        env_path = self.config.get('environments', {}).get(env_name)
        if not env_path:
            print(f"Environment '{env_name}' not found")
            return False

        pip_path = Path(env_path) / ("Scripts" if sys.platform == "win32" else "bin") / ("pip.exe" if sys.platform == "win32" else "pip")
        
        if not pip_path.exists():
            print(f"pip not found in '{env_name}'")
            return False

        try:
            print("Upgrading pip + setuptools securely...")
            subprocess.run([str(pip_path), "install", "--upgrade", "pip", "setuptools"], check=True)
            print("✓ Upgrade finished")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Upgrade failed: {e}")
            return False

    def activate_environment(self, env_name: str) -> bool:
        if not env_name:
            env_name = self.config.get('default_env')
            if not env_name:
                print("Error: No name given and no default environment set")
                return False

        env_path = self.config.get('environments', {}).get(env_name)
        if not env_path or not Path(env_path).exists():
            print(f"Environment '{env_name}' not found or was deleted")
            self.list_environments()
            return False

        env_path = Path(env_path).resolve()  # Fix 4: always use real path

        if sys.platform == "win32":
            activate_script = env_path / "Scripts" / "activate.bat"
            activate_cmd = f'call "{activate_script}"'
            shell_cmd = f'cmd /k "{activate_cmd}"'
        else:
            activate_script = env_path / "bin" / "activate"
            activate_cmd = f'source "{activate_script}"'
            shell_cmd = f'bash -c \'{activate_cmd} && export PYP_CURRENT_ENV={env_name} && exec bash\''  # Fix: also sets variable inside shell

        os.environ['PYP_CURRENT_ENV'] = env_name

        print(f"✓ Activating secure environment '{env_name}'")
        print(f"Location: {env_path}")
        print(f"Python: {env_path / ('Scripts' if sys.platform=='win32' else 'bin') / ('python.exe' if sys.platform=='win32' else 'python')}")

        print("\nNew shell opened with environment active!")
        print("When finished type 'exit' to return here\n")

        try:
            subprocess.run(shell_cmd, shell=True)
        except KeyboardInterrupt:
            print("\nActivation stopped safely")

        return True

    def deactivate_environment(self) -> bool:
        current = self.get_current_env()
        if not current:
            print("No pyp environment is active right now")
            return False

        if 'PYP_CURRENT_ENV' in os.environ:
            del os.environ['PYP_CURRENT_ENV']

        print(f"✓ Deactivated '{current}'")
        print("Type 'deactivate' if you are inside a manual shell")
        return True

    def list_environments(self) -> bool:
        environments = self.config.get('environments', {})
        if not environments:
            print("No environments yet. Create one:  pyp -b myproject")
            return False

        print("Your secure environments:")
        print("-" * 50)
        default = self.config.get('default_env')
        current = self.get_current_env()

        for name, path in environments.items():
            p = Path(path)
            mark = "✓ Active" if name == current else ""
            def_mark = " (default)" if name == default else ""
            exists = "✓" if p.exists() else "✗ (deleted)"
            print(f"{exists} {name}{def_mark} {mark}")
            print(f"   {p}")
            print()
        return True

    def remove_environment(self, env_name: str):
        if env_name not in self.config.get('environments', {}):
            print(f"'{env_name}' not found")
            return

        path = Path(self.config['environments'][env_name])
        if path.exists():
            answer = input(f"Really delete '{env_name}' at {path}? [y/N]: ")
            if answer.lower() not in ['y', 'yes']:
                print("Cancelled – nothing deleted")
                return
            shutil.rmtree(path)
            print(f"Deleted folder {path}")

        del self.config['environments'][env_name]
        if self.config.get('default_env') == env_name:
            self.config['default_env'] = next(iter(self.config['environments']), None)
        self.save_config()
        print(f"✓ Removed '{env_name}' completely")

def main():
    parser = argparse.ArgumentParser(description="pyp - Secure Python Environment Manager")
    parser.add_argument('-b', '--build', metavar='NAME', help='Create new environment')
    parser.add_argument('-a', '--activate', metavar='NAME', help='Activate environment')
    parser.add_argument('-d', '--deactivate', action='store_true', help='Deactivate')
    parser.add_argument('-l', '--list', action='store_true', help='List all')
    parser.add_argument('--remove', metavar='NAME', help='Delete environment')
    parser.add_argument('--python', help='Use specific Python version (example: 3.11)')
    parser.add_argument('--system-site-packages', action='store_true')
    parser.add_argument('--upgrade', action='store_true')
    parser.add_argument('--set-default', metavar='NAME', help='Make this default')

    args = parser.parse_args()
    manager = PyPManager()

    if args.remove:
        manager.remove_environment(args.remove)
        return

    if args.set_default:
        if args.set_default in manager.config.get('environments', {}):
            manager.config['default_env'] = args.set_default
            manager.save_config()
            print(f"✓ '{args.set_default}' is now default")
        else:
            print(f"'{args.set_default}' not found")
        return

    if args.build:
        success = manager.build_environment(
            args.build,
            python_version=args.python,
            system_site_packages=args.system_site_packages,
            upgrade=args.upgrade
        )
        sys.exit(0 if success else 1)

    if args.activate:
        success = manager.activate_environment(args.activate)
        sys.exit(0 if success else 1)

    if args.deactivate:
        success = manager.deactivate_environment()
        sys.exit(0 if success else 1)

    if args.list:
        manager.list_environments()
        return

    # default: show list
    manager.list_environments()

if __name__ == "__main__":
    main()
