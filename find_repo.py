import os
import sys
import json

def find_repos(search_term=None):
	json_file = "gitrepos.json"
	
	try:
		with open(json_file, 'r') as f:
			repos = json.load(f)
	except FileNotFoundError:
		print("No se encontró el archivo gitrepos.json")
		return
	
	if not search_term:
		# Mostrar todos
		for path, name in repos.items():
			print(f"{name}\t{path}")
	else:
		# Buscar coincidencias
		for path, name in repos.items():
			if search_term.lower() in name.lower():
				print(f"{name}\t{path}")

if __name__ == "__main__":
	search = sys.argv[1] if len(sys.argv) > 1 else None
	find_repos(search)