# pyp - Python Virtual Environment Manager

A lightweight and intuitive tool for managing Python virtual environments with a simple command-line interface.

## Features

- **Simple Commands**: Easy-to-remember commands for all venv operations
- **Multiple Python Versions**: Support for creating environments with specific Python versions
- **System Integration**: Seamless integration with existing Python installations
- **Configuration Management**: Automatic tracking of environments and settings
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Full venv Compatibility**: Includes all standard virtual environment functionality

## Installation

1. Download the `pyp.py` script
2. Make it executable:
   ```bash
   chmod +x pyp.py
   ```
3. Move it to your PATH or create a symlink:
   ```bash
   sudo ln -s /path/to/pyp.py /usr/local/bin/pyp
   ```
   Or add an alias to your shell profile:
   ```bash
   alias pyp='python3 /path/to/pyp.py'
   ```

## Usage

### Building Virtual Environments

Create a new virtual environment:
```bash
pyp -b myenv
```

Create with a specific Python version:
```bash
pyp -b myenv --python 3.11
```

Create with system site packages:
```bash
pyp -b myenv --system-site-packages
```

Create and automatically upgrade pip/setuptools:
```bash
pyp -b myenv --upgrade
```

### Activating Environments

Activate a specific environment:
```bash
pyp -a myenv
```

Activate the default environment:
```bash
pyp -a
```

### Deactivating Environments

Deactivate the current environment:
```bash
pyp -d
```

### Managing Environments

List all environments:
```bash
pyp -l
```

Show detailed information about an environment:
```bash
pyp -i myenv
```

Set an environment as default:
```bash
pyp --set-default myenv
```

Remove an environment:
```bash
pyp --remove myenv
```

## Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `pyp -b <name>` | Build/create environment | `pyp -b myenv` |
| `pyp -a <name>` | Activate environment | `pyp -a myenv` |
| `pyp -d` | Deactivate environment | `pyp -d` |
| `pyp -l` | List environments | `pyp -l` |
| `pyp -i <name>` | Show environment info | `pyp -i myenv` |
| `pyp --set-default <name>` | Set default environment | `pyp --set-default myenv` |
| `pyp --remove <name>` | Remove environment | `pyp --remove myenv` |

## Options

| Option | Description |
|--------|-------------|
| `--python VERSION` | Specify Python version (e.g., 3.11) |
| `--system-site-packages` | Include system site packages |
| `--upgrade` | Upgrade pip and setuptools after creation |
| `--help, -h` | Show help information |

## Configuration

pyp automatically creates a configuration file at `~/.pyp_config.json` that stores:
- Environment locations and names
- Default environment setting
- Environment metadata

## Workflow Examples

### Basic Development Workflow

1. Create a new project environment:
   ```bash
   pyp -b myproject --python 3.11
   ```

2. Activate it:
   ```bash
   pyp -a myproject
   ```

3. Install packages:
   ```bash
   pip install requests flask
   ```

4. When done:
   ```bash
   pyp -d
   ```

### Multiple Python Versions

```bash
# Create environments with different Python versions
pyp -b project-py39 --python 3.9
pyp -b project-py310 --python 3.10
pyp -b project-py311 --python 3.11

# Switch between them
pyp -a project-py39
pyp -a project-py310
pyp -a project-py311
```

### Production Environment

```bash
# Create a production-like environment
pyp -b prod-env --system-site-packages --upgrade
pyp --set-default prod-env
```

## Benefits Over Standard venv

1. **Simpler Commands**: No need to remember the full `python -m venv` syntax
2. **Automatic Management**: Built-in environment tracking and configuration
3. **Default Environments**: Easily set and switch between default environments
4. **Cross-Platform Activation**: Handles shell differences automatically
5. **Integrated Listing**: See all your environments at once
6. **Quick Operations**: One command to activate, build, or deactivate

## Requirements

- Python 3.6 or higher
- Standard library modules only (no external dependencies)
- Works on Windows, macOS, and Linux

## Troubleshooting

### Environment not found
- Check available environments: `pyp -l`
- Verify the environment path exists
- Re-create if necessary: `pyp -b <name> --upgrade`

### Activation issues
- Make sure you're using the correct shell command
- Try manual activation if automatic fails
- Check environment exists: `pyp -i <name>`

### Permission errors
- Ensure you have write access to `~/.pyp_envs/`
- Check file permissions on the environment directory

## Contributing

Feel free to submit issues, feature requests, or improvements to this tool.

## License

This tool is provided as-is for educational and development purposes.