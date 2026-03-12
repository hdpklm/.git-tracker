import os
import sys
import json
from pathlib import Path
from collections import defaultdict

JSON_FILE = "gitrepos.json"
LIST_FILE = "git-repos-list.json"

def get_common_roots(repos):
	"""Identifica las raíces comunes (primer nivel de carpetas)"""
	roots = set()
	for path in repos.keys():
		parts = path.split('/')
		if len(parts) > 1:
			# Tomar los primeros 2 niveles (ej: c:/Hassan)
			roots.add(f"{parts[0]}/{parts[1]}")
		else:
			roots.add(parts[0])
	return sorted(roots)

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
	for dir_name, repo_paths_list in sorted(repos):
		# Cada elemento en repo_paths_list es una tupla (repo_name, repo_path)
		for i, (repo_name, repo_path) in enumerate(sorted(repo_paths_list)):
			is_last_repo = (i == len(sorted(repo_paths_list)) - 1 and dir_name == sorted([r[0] for r in repos])[-1])
			repo_prefix = "└── " if is_last_repo else "├── "
			
			current_id_val = current_id[0] if isinstance(current_id, list) else current_id
			print(f"{prefix}{repo_prefix}[{current_id_val}] 📦 {repo_name}")
			id_map[current_id_val] = repo_path
			
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
		file_path = os.path.join(script_dir, LIST_FILE)
		with open(file_path, 'w') as f:
			json.dump(repos_list, f, indent=2)
		return True
	except Exception as e:
		print(f"Error al generar git-repos-list.json: {e}")
		return False

def show_help():
	"""Mostrar la ayuda con todos los argumentos disponibles"""
	help_text = """
Git Tracker - Gestor de repositorios Git

Uso: python git_tracker.py [COMANDO] [OPCIONES]

COMANDOS:
  -h, --help              Muestra esta ayuda
  
  -s, --scan [PATH]       Escanea el disco o un PATH específico buscando repositorios
                          (carpetas con .git/config) y los agrega al registro
                          Si no se proporciona PATH, escanea el disco completo
                          Ejemplo: git_tracker.py -s C:/Users/Hassan
  
  -a, --add [PATH]        Agrega un repositorio a partir de la carpeta actual o del PATH
                          Busca la carpeta .git/config en la ubicación especificada
                          Ejemplo: git_tracker.py -a
                          Ejemplo: git_tracker.py -a D:/projects/miproyecto
  
  -u, --update            Verifica que todos los repositorios guardados sigan existiendo
                          Muestra una lista numerada de los repositorios que ya no existen
                          para que puedas decidir cuáles eliminar
  
  -r, --remove [ARGS]     Elimina repositorios por número del ID (recomendado)
                          Puedes pasar múltiples IDs separados por espacio
                          Ejemplo: git_tracker.py -r 0 2 4
                          También puedes usar paths:
                          Ejemplo: git_tracker.py -r D:/proyecto1 C:/proyecto2

ARCHIVOS GENERADOS:
  - gitrepos.json         Archivo principal con todos los repositorios (clave-valor)
  - git-repos-list.json   Archivo con estructura treeview e IDs para fácil referencia

EJEMPLOS:
  git_tracker.py -h
  git_tracker.py -s
  git_tracker.py -s C:/Users/Hassan
  git_tracker.py -a
  git_tracker.py -a D:/mis_proyectos
  git_tracker.py -u
  git_tracker.py -r 0 1 2
  git repos                 Ver lista de repos con IDs
  git repos binance        Buscar repos que contengan "binance"
	"""
	print(help_text)

def load_repos():
	"""Carga los repositorios del archivo JSON"""
	try:
		script_dir = os.path.dirname(os.path.abspath(__file__))
		file_path = os.path.join(script_dir, JSON_FILE)
		if os.path.exists(file_path):
			with open(file_path, 'r') as f:
				repos = json.load(f)
				# Normalizar todos los paths a usar "/"
				return {k.replace("\\", "/"): v for k, v in repos.items()}
	except Exception as e:
		print(f"Error al cargar repositorios: {e}")
	return {}

def save_repos(repos):
	"""Guarda los repositorios en el archivo JSON"""
	try:
		script_dir = os.path.dirname(os.path.abspath(__file__))
		file_path = os.path.join(script_dir, JSON_FILE)
		with open(file_path, 'w') as f:
			json.dump(repos, f, indent=2)
		return True
	except Exception as e:
		print(f"Error al guardar repositorios: {e}")
		return False

def is_git_repo(path):
	"""Verifica si una carpeta contiene un repositorio Git válido"""
	git_config = os.path.join(path, ".git", "config")
	return os.path.exists(git_config)

EXCLUDE_DIRS = {
	"Windows", "Program Files", "Program Files (x86)", "AppData", "node_modules", 
	".cache", "System Volume Information", "$RECYCLE.BIN", "msys64", "Library",
	"Local Settings", "Temporary Internet Files", "Application Data", ".gemini"
}

def scan_repos(start_path=None):
	"""Escanea un disco o carpeta buscando repositorios Git"""
	if start_path is None:
		# Escanea todas las unidades (en Windows)
		if sys.platform == "win32":
			drives = []
			for i in range(ord('A'), ord('Z') + 1):
				drive = chr(i) + ":/"
				if os.path.exists(drive):
					drives.append(drive)
		else:
			drives = ["/"]
	else:
		start_path = os.path.abspath(start_path).replace("\\", "/")
		if not os.path.exists(start_path):
			print(f"Error: El path '{start_path}' no existe")
			return
		drives = [start_path]

	repos = load_repos()
	# Limpiar posibles entradas erróneas como "C:"
	if "C:" in repos:
		del repos["C:"]
	
	found_count = 0
	
	print("Escaneando repositorios (esto puede tardar, la primera vez)...")
	
	for drive in drives:
		print(f"Buscando en {drive}...")
		# Usamos os.walk con handling de errores para evitar permisos denegados
		for root, dirs, files in os.walk(drive, topdown=True, onerror=None):
			# Filtrar carpetas que no queremos escanear
			dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
			
			if ".git" in dirs:
				# Si root es una raíz de disco (ej: C:/), el basename es vacío
				repo_name = os.path.basename(root)
				if not repo_name:
					# Si es una raíz de disco, el nombre del repo no debería ser ""
					# A menos que el .git esté literalmente en C:/.git
					if is_git_repo(root):
						repo_name = f"Drive_{root[0]}"
					else:
						# Si no es un repo real en la raíz, lo ignoramos
						dirs.remove(".git")
						continue

				if is_git_repo(root):
					# Normalizar path con "/"
					normalized_root = root.replace("\\", "/")
					if normalized_root not in repos:
						repos[normalized_root] = repo_name
						print(f"  [+] Encontrado: {repo_name} ({normalized_root})")
						found_count += 1
					# Evitar descender más en .git
					dirs.remove(".git")

	if save_repos(repos):
		generate_repos_list(repos)
		print(f"\n[+] Se encontraron y guardaron {found_count} nuevo(s) repositorio(s)")
	else:
		print("[-] Error al guardar repositorios")

def add_repo(repo_path=None):
	"""Agrega un repositorio a la lista"""
	if repo_path is None:
		repo_path = os.getcwd()
	
	repo_path = os.path.abspath(repo_path)
	
	if not os.path.exists(repo_path):
		print(f"Error: El path '{repo_path}' no existe")
		return
	
	if not is_git_repo(repo_path):
		print(f"Error: '{repo_path}' no es un repositorio Git válido (no contiene .git/config)")
		return
	
	repos = load_repos()
	repo_name = os.path.basename(repo_path)
	# Normalizar path con "/"
	normalized_path = repo_path.replace("\\", "/")
	
	if normalized_path in repos:
		print(f"⚠ El repositorio ya está registrado: {repo_name}")
		return
	
	repos[normalized_path] = repo_name
	if save_repos(repos):
		generate_repos_list(repos)
		print(f"✓ Repositorio agregado: {repo_name}")
		print(f"  Ruta: {normalized_path}")
	else:
		print("✗ Error al agregar el repositorio")

def update_repos():
	"""Verifica que todos los repositorios existan en el disco"""
	repos = load_repos()
	missing_repos = []
	existing_repos = {}
	
	print("Verificando repositorios...")
	for repo_path, repo_name in repos.items():
		if os.path.exists(repo_path) and is_git_repo(repo_path):
			existing_repos[repo_path] = repo_name
		else:
			missing_repos.append((repo_path, repo_name))
	
	# Mostrar repos disponibles en formato árbol jerárquico
	if existing_repos:
		print(f"\n[+] Repositorios disponibles ({len(existing_repos)}):\n")
		tree = build_hierarchical_tree(existing_repos)
		print_hierarchical_tree(tree)
	
	# Mostrar repos faltantes
	if missing_repos:
		print(f"\n[!] Se encontraron {len(missing_repos)} repositorio(s) que ya no existen:\n")
		for i, (path, name) in enumerate(missing_repos):
			print(f"  [{i}] {name}")
			print(f"      {path}")
		print(f"\nPara eliminarlos usa: git_tracker.py -r <números>")
	else:
		print("\n[+] Todos los repositorios están disponibles")
	
	# Guardar solo los repositorios existentes y generar lista
	if save_repos(existing_repos):
		generate_repos_list(existing_repos)
		print(f"\n[+] {len(existing_repos)} repositorio(s) guardado(s)")

def get_id_to_path_mapping(repos):
	"""Crea un mapa consistente de ID -> ruta basado en el árbol jerárquico"""
	tree = build_hierarchical_tree(repos)
	id_map = {}
	repo_id = [0]  # Usar lista para poder modificar en función anidada
	
	def traverse_tree(subtree):
		dirs = {}
		repos_list = []
		
		for key, value in subtree.items():
			if isinstance(value, dict):
				if value['_repos']:
					repos_list.append((key, value['_repos']))
				if value['_dirs']:
					dirs[key] = value['_dirs']
		
		# Procesar directorios primero
		for dir_name in sorted(dirs.keys()):
			traverse_tree(dirs[dir_name])
		
		# Procesar repositorios
		for dir_name, repo_paths_list in sorted(repos_list):
			for repo_name, repo_path in repo_paths_list:
				id_map[repo_id[0]] = repo_path
				repo_id[0] += 1
	
	traverse_tree(tree)
	return id_map

def remove_repos(args):
	"""Elimina repositorios por número del ID o por ruta"""
	if not args:
		print("Error: Debes proporcionar al menos un número o ruta para eliminar")
		print("Ejemplo: git_tracker.py -r 0 1 2")
		print("O: git_tracker.py -r C:/path/to/repo")
		return
	
	repos = load_repos()
	id_map = get_id_to_path_mapping(repos)
	to_remove_paths = []
	
	for arg in args:
		# Verificar si es un número
		if arg.isdigit():
			idx = int(arg)
			if idx in id_map:
				to_remove_paths.append(id_map[idx])
			else:
				print(f"Error: El ID {idx} no existe")
		else:
			# Es una ruta - normalizar para comparar
			arg_path = os.path.abspath(arg).replace("\\", "/")
			if arg_path in repos:
				to_remove_paths.append(arg_path)
			else:
				print(f"[!] Advertencia: No se encontró el repositorio con path: {arg_path}")
	
	if to_remove_paths:
		print("Se van a eliminar los siguientes repositorios:")
		
		# Mostrar qué se va a eliminar
		for repo_path in to_remove_paths:
			repo_name = repos.get(repo_path, "Desconocido")
			print(f"  - {repo_name}")
			print(f"    {repo_path}")
		
		# Eliminar
		for repo_path in to_remove_paths:
			if repo_path in repos:
				del repos[repo_path]
		
		if save_repos(repos):
			generate_repos_list(repos)
			print(f"\n[+] Se eliminaron {len(to_remove_paths)} repositorio(s)")
		else:
			print("[-] Error al guardar cambios")
	else:
		print("[-] No se encontraron repositorios para eliminar")

def main():
	"""Función principal"""
	if len(sys.argv) < 2:
		show_help()
		return
	
	command = sys.argv[1].lower()
	args = sys.argv[2:] if len(sys.argv) > 2 else []
	
	if command in ["-h", "--help"]:
		show_help()
	elif command in ["-s", "--scan"]:
		scan_repos(args[0] if args else None)
	elif command in ["-a", "--add"]:
		add_repo(args[0] if args else None)
	elif command in ["-u", "--update"]:
		update_repos()
	elif command in ["-r", "--remove"]:
		remove_repos(args)
	else:
		print(f"Error: Comando '{command}' no reconocido")
		print("Usa 'git_tracker.py -h' para ver la ayuda")

if __name__ == "__main__":
	main()