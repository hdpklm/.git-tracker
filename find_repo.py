import os
import sys
import json
from collections import defaultdict

def build_hierarchical_tree(repos):
	"""Construye una estructura jerárquica de árbol"""
	tree = {}
	
	for path, name in repos.items():
		parts = path.split('/')
		
		# Construir la jerarquía
		current = tree
		for i, part in enumerate(parts[:-1]):  # Todas excepto el último (que es el repo)
			if part not in current:
				current[part] = {'_repos': [], '_dirs': {}}
			current = current[part]['_dirs']
		
		# Agregar el repositorio al final
		if parts[-1] not in current:
			current[parts[-1]] = {'_repos': [], '_dirs': {}}
		current[parts[-1]]['_repos'].append((name, path))
	
	return tree

def print_hierarchical_tree(tree, prefix="", is_last=True, id_map=None, current_id=None):
	"""Imprime el árbol jerárquico con IDs consistentes"""
	if id_map is None:
		id_map = {}
		current_id = [0]
	
	# Separar directorios y repositorios
	dirs = {}
	repos = []
	
	for key, value in tree.items():
		if isinstance(value, dict):
			if value['_repos']:
				repos.append((key, value['_repos']))
			if value['_dirs']:
				dirs[key] = value['_dirs']
	
	# Imprimir directorios primero
	for dir_name in sorted(dirs.keys()):
		is_last_item = (dir_name == sorted(dirs.keys())[-1] and not repos)
		current_prefix = "└── " if is_last_item else "├── "
		print(f"{prefix}{current_prefix}{dir_name}/")
		
		next_prefix = prefix + ("    " if is_last_item else "│   ")
		print_hierarchical_tree(dirs[dir_name], next_prefix, is_last_item, id_map, current_id)
	
	# Imprimir repositorios
	for repo_name, repo_paths in sorted(repos):
		is_last_repo = (repo_name == sorted([r[0] for r in repos])[-1])
		repo_prefix = "└── " if is_last_repo else "├── "
		
		# Aquí es donde asignamos el ID
		current_id_val = current_id[0] if isinstance(current_id, list) else current_id
		print(f"{prefix}{repo_prefix}[{current_id_val}] 📦 {repo_name}")
		id_map[current_id_val] = repo_paths
		
		if isinstance(current_id, list):
			current_id[0] += 1
		else:
			current_id += 1

def generate_repos_list(repos):
	"""Genera el archivo git-repos-list.json con IDs y estructura treeview"""
	tree = build_hierarchical_tree(repos)
	
	repos_list = {
		"total": len(repos),
		"structure": tree
	}
	
	# Generar una lista plana con IDs
	repos_list["by_id"] = {}
	repo_id = 0
	
	def extract_repos_with_ids(subtree):
		nonlocal repo_id
		for key, value in subtree.items():
			if isinstance(value, dict):
				for repo_name, repo_paths in value.get('_repos', []):
					repos_list["by_id"][repo_id] = {
						"name": repo_name,
						"path": repo_paths
					}
					repo_id += 1
				if value.get('_dirs'):
					extract_repos_with_ids(value['_dirs'])
	
	extract_repos_with_ids(tree)
	
	try:
		script_dir = os.path.dirname(os.path.abspath(__file__))
		file_path = os.path.join(script_dir, "git-repos-list.json")
		with open(file_path, 'w') as f:
			json.dump(repos_list, f, indent=2)
		return True
	except Exception as e:
		print(f"Error al generar git-repos-list.json: {e}")
		return False

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
		# Mostrar todos en formato árbol jerárquico
		generate_repos_list(repos)
		print("\n📁 Estructura de repositorios:\n")
		tree = build_hierarchical_tree(repos)
		print_hierarchical_tree(tree)
	else:
		# Buscar coincidencias
		filtered_repos = {}
		for path, name in repos.items():
			if search_term.lower() in name.lower() or search_term.lower() in path.lower():
				filtered_repos[path] = name
		
		if filtered_repos:
			print(f"\n🔍 Resultados para '{search_term}':\n")
			tree = build_hierarchical_tree(filtered_repos)
			print_hierarchical_tree(tree)
		else:
			print(f"No se encontraron repositorios que coincidan con '{search_term}'")

if __name__ == "__main__":
	search = sys.argv[1] if len(sys.argv) > 1 else None
	find_repos(search)