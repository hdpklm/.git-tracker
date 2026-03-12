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

def print_hierarchical_tree(tree, prefix="", is_last=True, id_map=None, current_id=None, external_id_map=None):
	"""Imprime el árbol jerárquico con IDs consistentes"""
	if id_map is None and external_id_map is None:
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
		print_hierarchical_tree(dirs[dir_name], next_prefix, is_last_item, id_map, current_id, external_id_map)
	
	# Imprimir repositorios
	for dir_name, repo_paths_list in sorted(repos):
		# Cada elemento en repo_paths_list es una tupla (repo_name, repo_path)
		for i, (repo_name, repo_path) in enumerate(sorted(repo_paths_list)):
			is_last_repo = (i == len(sorted(repo_paths_list)) - 1 and dir_name == sorted([r[0] for r in repos])[-1])
			repo_prefix = "└── " if is_last_repo else "├── "
			
			if external_id_map:
				current_id_val = external_id_map.get(repo_path, "?")
			else:
				current_id_val = current_id[0] if isinstance(current_id, list) else current_id
				if id_map is not None:
					id_map[current_id_val] = repo_path
				
				if isinstance(current_id, list):
					current_id[0] += 1
				else:
					current_id += 1
			
			print(f"{prefix}{repo_prefix}[{current_id_val}] {repo_name}")

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
		dirs = {}
		repos_items = []
		
		for key, value in subtree.items():
			if isinstance(value, dict):
				if value['_repos']:
					repos_items.append((key, value['_repos']))
				if value['_dirs']:
					dirs[key] = value['_dirs']
		
		# Procesar directorios primero
		for dir_name in sorted(dirs.keys()):
			extract_repos_with_ids(dirs[dir_name])
		
		# Procesar repositorios
		for dir_name, repo_paths_list in sorted(repos_items):
			for repo_name, repo_path in repo_paths_list:
				repos_list["by_id"][repo_id] = {
					"name": repo_name,
					"path": repo_path
				}
				repo_id += 1
	
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
	
	# Generar el mapa global de IDs para que las búsquedas mantengan IDs consistentes
	def get_global_path_to_id(all_repos):
		full_tree = build_hierarchical_tree(all_repos)
		path_to_id = {}
		repo_id = [0]
		
		def traverse(subtree):
			dirs = {}
			repos_items = []
			for key, val in subtree.items():
				if isinstance(val, dict):
					if val['_repos']: repos_items.append((key, val['_repos']))
					if val['_dirs']: dirs[key] = val['_dirs']
			for dir_name in sorted(dirs.keys()):
				traverse(dirs[dir_name])
			for dir_name, repo_paths_list in sorted(repos_items):
				for r_name, r_path in sorted(repo_paths_list):
					path_to_id[r_path] = repo_id[0]
					repo_id[0] += 1
		
		traverse(full_tree)
		return path_to_id

	path_to_id_map = get_global_path_to_id(repos)

	if not search_term:
		# Mostrar todos en formato árbol jerárquico
		generate_repos_list(repos)
		print("\n[+] Estructura de repositorios:\n")
		tree = build_hierarchical_tree(repos)
		print_hierarchical_tree(tree, external_id_map=path_to_id_map)
	else:
		# Buscar coincidencias
		filtered_repos = {}
		for path, name in repos.items():
			if search_term.lower() in name.lower() or search_term.lower() in path.lower():
				filtered_repos[path] = name
		
		if filtered_repos:
			print(f"\n[?] Resultados para '{search_term}':\n")
			tree = build_hierarchical_tree(filtered_repos)
			print_hierarchical_tree(tree, external_id_map=path_to_id_map)
		else:
			print(f"[-] No se encontraron repositorios que coincidan con '{search_term}'")

if __name__ == "__main__":
	search = sys.argv[1] if len(sys.argv) > 1 else None
	find_repos(search)