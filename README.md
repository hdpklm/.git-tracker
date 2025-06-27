# Git Tracker

Tool that automatically tracks all your Git repositories on your local machine and allows easy searching.

## What It Does

- Automatically registers the location of all your Git repos
- Runs on every `git commit`, `git pull`, `git clone`, etc.
- Allows searching repos by name
- Prevents cloning the same repo multiple times

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/hdpklm/.git-tracker.git
cd .git-tracker
```

### 2. Run Installation

```cmd
setup.bat
```

This automatically configures Git to use the hooks and creates the `git repos` command.

## Usage

### Search Repositories

```bash
# List all repos
git repos

# Search specific repo
git repos code-example

# Get exact path
git repos my-project
```

### View Database

```cmd
type "%USERPROFILE%/.git-tracker/gitrepos.json"
```

Example:
```json
{
	"C:/Users/user-1/website/code-example": "code-example",
	"C:/dev/projects/my-project": "my-project",
	"C:/tools/utils": "utils"
}
```

## How It Works

Hooks run automatically on:
- `git commit`
- `git pull` 
- `git clone`
- `git checkout`
- `git merge`

## Uninstall

```bash
git config --global --unset core.hooksPath
git config --global --unset alias.repos
```

## Requirements

- Python 3.x
- Git for Windows
- Windows 10/11