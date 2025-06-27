import os
import sys
import json
from pathlib import Path

def update_repo_registry():
	if len(sys.argv) > 0:
		repo_path = sys.argv[1]
	else:
		repo_path = os.getcwd()

	print(f"Updating repository registry for: {repo_path}")
	repo_name = Path(repo_path).name
	json_file = "gitrepos.json"
	
	try:
		with open(json_file, 'r') as f:
			repos = json.load(f)
	except FileNotFoundError:
		repos = {}
	
	repos[repo_path] = repo_name
	
	with open(json_file, 'w') as f:
		json.dump(repos, f, indent=2)

if __name__ == "__main__":
	update_repo_registry()