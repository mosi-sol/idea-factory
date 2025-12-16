#!/usr/bin/env python3
"""
pyp - Python Virtual Environment Manager
A lightweight tool for managing Python virtual environments

Usage:
    pyp -b <env_name>    Build/create a new virtual environment
    pyp -a <env_name>    Activate a virtual environment
    pyp -d               Deactivate the current virtual environment
    pyp -h, --help       Show help information
"""

import os
import sys
import argparse
import subprocess
import shutil
import json
import re  # NEW: for environment name validation
from pathlib import Path
from typing import Optional, Dict, List


class PyPManager:
    """Manager for Python virtual environments using pyp command"""
    
    def __init__(self):
        self.config_file = Path.home() / ".pyp_config.json"
        self.envs_dir = Path.home() / ".pyp_envs"
        self.envs_dir.mkdir(exist_ok=True)
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.config = {}
        else:
            self.config = {}
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save configuration: {e}")
    
    def get_current_env(self) -> Optional[str]:
        """Get the name of the currently activated environment"""
        venv_path = os.environ.get('VIRTUAL_ENV')
        if venv_path:
            for env_name, env_path in self.config.get('environments', {}).items():
                if Path(venv_path) == Path(env_path):
                    return env_name
        
        pyp_env = os.environ.get('PYP_CURRENT_ENV')
        if pyp_env:
            return pyp_env
            
        return None
    
    # NEW: Helper function to validate environment names
    def is_valid_env_name(self, name: str) -> bool:
        """Check if environment name contains only safe characters: a-z, A-Z, 0-9, _, -"""
        if not name or not name.strip():
            return False
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.fullmatch(pattern, name))
    
    # IMPROVED: Added name validation
    def build_environment(self, env_name: str, python_version: Optional[str] = None, 
                         system_site_packages: bool = False, upgrade: bool = False) -> bool:
        """
        Build/create a new virtual environment
        """
        if not self.is_valid_env_name(env_name):
            print("Error: Invalid environment name.")
            print("Only letters, numbers, underscores (_), and hyphens (-) are allowed.")
            print("Example: my-project, env_01, fastapi_app")
            return False
        
        env_name = env_name.strip()
        env_path = self.envs_dir / env_name
        
        if env_path.exists() and not upgrade:
            print(f"Error: Environment '{env_name}' already exists. Use --upgrade to recreate it.")
            return False
        
        if upgrade and env_path.exists():
            print(f"Removing existing environment '{env_name}'...")
            # IMPROVED: Safer removal - handle errors gracefully
            try:
                shutil.rmtree(env_path)
            except Exception as e:
                print(f"Error removing old environment: {e}")
                return False
        
        try:
            cmd = [sys.executable, "-m", "venv", str(env_path)]
            
            if python_version:
                python_cmd = f"python{python_version}"
                try:
                    subprocess.run([python_cmd, "--version"], 
                                 capture_output=True, check=True)
                    cmd = [python_cmd, "-m", "venv", str(env_path)]
                except (subprocess.CalledProcessError, FileNotFoundError):
                    print(f"Warning: Python {python_version} not found, using current Python")
            
            if system_site_packages:
                cmd.append("--system-site-packages")
            
            print(f"Creating virtual environment '{env_name}'...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Error creating environment: {result.stderr}")
                return False
            
            if 'environments' not in self.config:
                self.config['environments'] = {}
            
            self.config['environments'][env_name] = str(env_path)
            
            if 'default_env' not in self.config:
                self.config['default_env'] = env_name
            
            self.save_config()
            
            print(f"✓ Successfully created environment '{env_name}' at {env_path}")
            
            if upgrade:
                self.upgrade_environment(env_name)
            
            return True
            
        except Exception as e:
            print(f"Error creating environment: {e}")
            return False
    
    def upgrade_environment(self, env_name: str) -> bool:
        """Upgrade pip and setuptools in the environment"""
        env_path = self.config.get('environments', {}).get(env_name)
        if not env_path:
            print(f"Error: Environment '{env_name}' not found")
            return False
        
        pip_path = Path(env_path) / "bin" / "pip"
        if sys.platform == "win32":
            pip_path = Path(env_path) / "Scripts" / "pip.exe"
        
        if not pip_path.exists():
            print(f"Error: pip not found in environment '{env_name}'")
            return False
        
        try:
            print("Upgrading pip and setuptools...")
            subprocess.run([str(pip_path), "install", "--upgrade", "pip", "setuptools"], 
                         check=True)
            print("✓ Upgrade completed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error upgrading environment: {e}")
            return False
    
    # IMPROVED: Added name validation for activation
    def activate_environment(self, env_name: str) -> bool:
        """
        Activate a virtual environment
        """
        if not env_name:
            env_name = self.config.get('default_env')
            if not env_name:
                print("Error: No environment name specified and no default environment set")
                return False
        
        # Validate name even if it comes from config (extra safety)
        if not self.is_valid_env_name(env_name):
            print(f"Error: Invalid environment name '{env_name}'")
            return False
        
        env_path = self.config.get('environments', {}).get(env_name)
        if not env_path:
            print(f"Error: Environment '{env_name}' not found")
            print("Available environments:")
            self.list_environments()
            return False
        
        env_path = Path(env_path)
        if not env_path.exists():
            print(f"Error: Environment '{env_name}' path does not exist: {env_path}")
            return False
        
        if sys.platform == "win32":
            activate_script = env_path / "Scripts" / "activate.bat"
            activate_cmd = f'call "{activate_script}"'
            shell_cmd = f'cmd /k "{activate_cmd}"'
        else:
            activate_script = env_path / "bin" / "activate"
            activate_cmd = f'source "{activate_script}"'
            shell_cmd = f'bash -c "{activate_cmd} && exec bash"'
        
        os.environ['PYP_CURRENT_ENV'] = env_name
        
        print(f"✓ Activating environment '{env_name}'")
        print(f"Environment location: {env_path}")
        print(f"Python: {env_path / 'bin' / 'python' if sys.platform != 'win32' else env_path / 'Scripts' / 'python.exe'}")
        
        if sys.platform == "win32":
            print(f"\nTo activate manually, run: {activate_cmd}")
        else:
            print(f"\nTo activate manually, run: {activate_cmd}")
        
        try:
            if sys.platform == "win32":
                subprocess.run([shell_cmd], shell=True)
            else:
                subprocess.run([shell_cmd], shell=True)
        except KeyboardInterrupt:
            print("\nEnvironment activation interrupted")
        
        return True
    
    def deactivate_environment(self) -> bool:
        """Deactivate the current virtual environment"""
        current_env = self.get_current_env()
        
        if not current_env:
            print("No pyp-managed environment is currently active")
            print("To deactivate a standard venv, use the 'deactivate' command directly")
            return False
        
        if 'PYP_CURRENT_ENV' in os.environ:
            del os.environ['PYP_CURRENT_ENV']
        
        print(f"✓ Deactivated pyp environment '{current_env}'")
        print("Note: If you activated the environment manually, you may need to run 'deactivate' in that shell")
        
        return True
    
    def list_environments(self) -> bool:
        """List all available environments"""
        environments = self.config.get('environments', {})
        default_env = self.config.get('default_env')
        
        if not environments:
            print("No environments found. Create one using: pyp -b <name>")
            return False
        
        print("Available environments:")
        print("-" * 50)
        
        for env_name, env_path in environments.items():
            env_path = Path(env_path)
            status = "✓ Active" if self.get_current_env() == env_name else ""
            default_marker = " (default)" if env_name == default_env else ""
            
            exists = "✓" if env_path.exists() else "✗"
            print(f"{exists} {env_name}{default_marker}")
            print(f"   Path: {env_path}")
            if status:
                print(f"   Status: {status}")
            print()
        
        return True
    
    def show_info(self, env_name: Optional[str] = None):
        """Show information about environments"""
        if env_name:
            env_path = self.config.get('environments', {}).get(env_name)
            if not env_path:
                print(f"Environment '{env_name}' not found")
                return
            
            env_path = Path(env_path)
            print(f"Environment: {env_name}")
            print(f"Path: {env_path}")
            print(f"Exists: {'Yes' if env_path.exists() else 'No'}")
            print(f"Active: {'Yes' if self.get_current_env() == env_name else 'No'}")
            
            if env_path.exists():
                python_path = (env_path / "bin" / "python" 
                             if sys.platform != "win32" 
                             else env_path / "Scripts" / "python.exe")
                if python_path.exists():
                    try:
                        result = subprocess.run([str(python_path), "--version"], 
                                              capture_output=True, text=True)
                        if result.returncode == 0:
                            print(f"Python: {result.stdout.strip()}")
                    except:
                        pass
        else:
            self.list_environments()


def main():
    """Main entry point for pyp command"""
    parser = argparse.ArgumentParser(
        description="pyp - Python Virtual Environment Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pyp -b myenv              # Create a new environment
  pyp -b myenv --python 3.11  # Create with specific Python version
  pyp -b myenv --upgrade   # Create and upgrade packages
  pyp -a myenv             # Activate environment
  pyp -d                   # Deactivate current environment
  pyp -l                   # List all environments
        """
    )
    
    parser.add_argument('-b', '--build', metavar='NAME', 
                       help='Build/create a new virtual environment')
    parser.add_argument('-a', '--activate', metavar='NAME',
                       help='Activate a virtual environment')
    parser.add_argument('-d', '--deactivate', action='store_true',
                       help='Deactivate the current virtual environment')
    parser.add_argument('-l', '--list', action='store_true',
                       help='List all available environments')
    parser.add_argument('-i', '--info', metavar='NAME',
                       help='Show information about an environment')
    parser.add_argument('--python', metavar='VERSION',
                       help='Python version to use (e.g., 3.11)')
    parser.add_argument('--system-site-packages', action='store_true',
                       help='Include system site packages')
    parser.add_argument('--upgrade', action='store_true',
                       help='Upgrade pip and setuptools after creation')
    parser.add_argument('--set-default', metavar='NAME',
                       help='Set an environment as default')
    parser.add_argument('--remove', metavar='NAME',
                       help='Remove an environment')
    
    args = parser.parse_args()
    
    manager = PyPManager()
    
    # IMPROVED: Added name validation for --remove and --set-default
    if args.remove:
        env_name = args.remove
        if not manager.is_valid_env_name(env_name):
            print(f"Error: Invalid environment name '{env_name}'")
            return
        
        if env_name in manager.config.get('environments', {}):
            env_path = Path(manager.config['environments'][env_name])
            if env_path.exists():
                response = input(f"Remove environment '{env_name}' at {env_path}? [y/N]: ")
                if response.lower() in ['y', 'yes']:
                    try:
                        shutil.rmtree(env_path)
                    except Exception as e:
                        print(f"Error removing environment: {e}")
                        return
                    del manager.config['environments'][env_name]
                    if manager.config.get('default_env') == env_name:
                        manager.config['default_env'] = list(manager.config['environments'].keys())[0] if manager.config['environments'] else None
                    manager.save_config()
                    print(f"✓ Removed environment '{env_name}'")
                else:
                    print("Removal cancelled")
            else:
                print(f"Environment '{env_name}' path does not exist")
                del manager.config['environments'][env_name]
                manager.save_config()
                print(f"✓ Removed environment '{env_name}' from config")
        else:
            print(f"Environment '{env_name}' not found")
        return
    
    if args.set_default:
        env_name = args.set_default
        if not manager.is_valid_env_name(env_name):
            print(f"Error: Invalid environment name '{env_name}'")
            return
        if env_name in manager.config.get('environments', {}):
            manager.config['default_env'] = env_name
            manager.save_config()
            print(f"✓ Set '{env_name}' as default environment")
        else:
            print(f"Environment '{env_name}' not found")
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
        success = manager.list_environments()
        sys.exit(0 if success else 1)
    
    if args.info:
        manager.show_info(args.info)
        return
    
    if not any([args.build, args.activate, args.deactivate, args.list, args.info]):
        manager.show_info()
        return


if __name__ == "__main__":
    main()
