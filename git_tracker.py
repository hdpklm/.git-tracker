import json
import os
from pathlib import Path

def update_repo_registry():
	repo_path = os.getcwd()
	repo_name = Path(repo_path).name
	json_file = "%USERPROFILE%/.git-tracker/gitrepos.json"
	
	try:
		with open(json_file, 'r') as f:
			repos = json.load(f)
	except FileNotFoundError:
		repos = {}
	
	repos[repo_name] = repo_path
	
	with open(json_file, 'w') as f:
		json.dump(repos, f, indent=2)

if __name__ == "__main__":
	update_repo_registry()