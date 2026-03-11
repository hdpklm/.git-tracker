import os
import sys
import json
from collections import defaultdict

def build_tree_structure(repos):
	"""Construye una estructura de árbol organizando repos por carpeta"""
	tree = defaultdict(list)
	
	for path, name in repos.items():
		# Obtener la carpeta padre
		parent = os.path.dirname(path)
		tree[parent].append((name, path))
	
	return tree

def generate_repos_list(repos):
	"""Genera el archivo git-repos-list.json con IDs y estructura treeview"""
	tree = build_tree_structure(repos)
	sorted_dirs = sorted(tree.keys())
	
	repos_list = {
		"total": len(repos),
		"by_folder": {}
	}
	
	repo_id = 0
	
	for parent_dir in sorted_dirs:
		repos_list["by_folder"][parent_dir] = []
		repos_in_dir = sorted(tree[parent_dir])
		
		for name, path in repos_in_dir:
			repos_list["by_folder"][parent_dir].append({
				"id": repo_id,
				"name": name,
				"path": path
			})
			repo_id += 1
	
	try:
		script_dir = os.path.dirname(os.path.abspath(__file__))
		file_path = os.path.join(script_dir, "git-repos-list.json")
		with open(file_path, 'w') as f:
			json.dump(repos_list, f, indent=2)
		return True
	except Exception as e:
		print(f"Error al generar git-repos-list.json: {e}")
		return False

def print_tree_view(repos, search_term=None):
	"""Imprime los repositorios en formato árbol con IDs"""
	if not repos:
		if search_term:
			print(f"No se encontraron repositorios que coincidan con '{search_term}'")
		else:
			print("No hay repositorios guardados. Usa 'git_tracker -s' para escanear.")
		return
	
	tree = build_tree_structure(repos)
	sorted_dirs = sorted(tree.keys())
	
	print("\n📁 Estructura de repositorios:\n")
	
	repo_id = 0
	for i, parent_dir in enumerate(sorted_dirs):
		# Mostrar carpeta padre
		is_last_dir = (i == len(sorted_dirs) - 1)
		dir_prefix = "└── " if is_last_dir else "├── "
		print(f"{dir_prefix}{parent_dir}/")
		
		# Mostrar repos en esta carpeta
		repos_in_dir = sorted(tree[parent_dir])
		for j, (name, path) in enumerate(repos_in_dir):
			is_last_repo = (j == len(repos_in_dir) - 1)
			spacing = "    " if is_last_dir else "│   "
			repo_prefix = "└── " if is_last_repo else "├── "
			print(f"{spacing}{repo_prefix}[{repo_id}] 📦 {name}")
			repo_id += 1
	
	print()

def find_repos(search_term=None):
	"""Busca repositorios en la lista guardada"""
	script_dir = os.path.dirname(os.path.abspath(__file__))
	json_file = os.path.join(script_dir, "gitrepos.json")
	
	try:
		if not os.path.exists(json_file):
			print(f"No se encontró el archivo {json_file}")
			print("Usa 'git_tracker -s' para escanear y agregar repositorios")
			return

		with open(json_file, 'r') as f:
			repos = json.load(f)
	except FileNotFoundError:
		print("No se encontró el archivo gitrepos.json")
		print("Usa 'git_tracker -s' para escanear y agregar repositorios")
		return
	
	if not search_term:
		# Mostrar todos en formato árbol
		generate_repos_list(repos)
		print_tree_view(repos)
	else:
		# Buscar coincidencias
		filtered_repos = {}
		for path, name in repos.items():
			if search_term.lower() in name.lower() or search_term.lower() in path.lower():
				filtered_repos[path] = name
		
		if filtered_repos:
			print(f"\n🔍 Resultados para '{search_term}':\n")
			print_tree_view(filtered_repos, search_term)
		else:
			print(f"No se encontraron repositorios que coincidan con '{search_term}'")

if __name__ == "__main__":
	search = sys.argv[1] if len(sys.argv) > 1 else None
	find_repos(search)