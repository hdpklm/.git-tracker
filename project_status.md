# Project Status - Git Tracker v1.4

## New Features
- **Advanced View (`-v`)**: Added support for fetching and displaying repository metadata like origin, branch, paths, and dates using flags (`lobmpchH`).
- **Goto Directory (`-g`)**: Replaced `git repos` alias with a batch wrapper (`git-repos.bat`) that allows changing the CMD working directory to any repository via ID or name.
- **Hide instead of Remove (`-r`)**: Migrated the database schema to support a `hidden` flag. Deleted repos are now hidden instead of purged, keeping their Global IDs intact.
- **Pre-Commit Hook**: Silenced the global Git pre-commit hook to silently register repos without polluting the console.
- **Unified CLI**: All operations are now accessed through a single command `git repos`. Search and subcommands are handled automatically.
- **Simplified Setup**: Unused aliases like `git tracker` have been removed.
- **ID Consistency**: Repositories maintain their global IDs in search results, ensuring safe deletion.
- **Windows Compatibility**: Full ASCII tree view and output (removed Unicode/Emojis) for native CMD support.

## Project Structure
List of directories ignored during scanning to improve performance:
`Windows`, `Program Files`, `Program Files (x86)`, `AppData`, `node_modules`, `.cache`, `System Volume Information`, `$RECYCLE.BIN`, `msys64`, `Library`, `Local Settings`, `Temporary Internet Files`, `Application Data`, `.gemini`

Git Tracker is a command-line tool designed to help users manage and track multiple Git repositories across their system. It allows scanning disks for repositories, adding individual repositories, and searching through the registered ones.

## Architecture

The project consists of two main Python scripts:
- `git_tracker.py`: The main entry point for scanning, adding, updating, and removing repositories.
- `find_repo.py`: A helper script for specialized searching and displaying the repository list in a hierarchical tree format.

## File Index

### [git_tracker.py](file:///c:/Users/Hassan/.git-tracker/git_tracker.py)
- `get_common_roots(repos)`: Returns a list of unique root directories for the repositories.
- `build_hierarchical_tree(repos)`: Builds a nested dictionary representing the repository structure.
- `print_hierarchical_tree(tree, ...)`: Recursively prints the repository tree with IDs.
- `generate_repos_list(repos)`: Generates `git-repos-list.json` with tree structure and IDs.
- `show_help()`: Displays help information.
- `load_repos()`: Loads repositories from `gitrepos.json`.
- `save_repos(repos)`: Saves repositories to `gitrepos.json`.
- `is_git_repo(path)`: Checks if a directory is a Git repository.
- `scan_repos(start_path)`: Scans drives or a path for Git repositories.
- `add_repo(repo_path)`: Adds a single repository to the list.
- `update_repos()`: Verifies if registered repositories still exist.
- `get_id_to_path_mapping(repos)`: Creates a map of ID to repository paths.
- `remove_repos(args)`: Removes repositories by ID or path.

### [find_repo.py](file:///c:/Users/Hassan/.git-tracker/find_repo.py)
- `build_hierarchical_tree(repos)`: Same as in `git_tracker.py`.
- `print_hierarchical_tree(tree, ...)`: Same as in `git_tracker.py`.
- `generate_repos_list(repos)`: Same as in `git_tracker.py`.
- `find_repos(search_term)`: Searches for repositories in the registered list.

## Data Files
- `gitrepos.json`: Stores the flat map of repository paths to names.
- `git-repos-list.json`: Stores the hierarchical structure and ID mapping.
