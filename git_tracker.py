import os
import sys
import json
import subprocess
from pathlib import Path
from collections import defaultdict
import datetime

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
	
	for path, repo_data in repos.items():
		name = repo_data.get("name", os.path.basename(path)) if isinstance(repo_data, dict) else repo_data
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
	# Solo construir el árbol con repositorios no ocultos
	visible_repos = {path: data for path, data in repos.items() if not data.get("hidden", False)}
	tree = build_hierarchical_tree(visible_repos)
	
	repos_list = {
		"total": len(visible_repos),
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

Uso: git repos [COMANDO|BÚSQUEDA]

COMANDOS de 'git repos':
  (sin nada)              Muestra todos los repositorios registrados
  [texto]                 Busca repositorios que coincidan con el texto (nombre o ruta)
  
  -s, --scan [PATH]       Escanea el disco o un PATH específico buscando repositorios
                          Ejemplo: git repos -s C:/Users/Hassan
  
  -a, --add [PATH]        Agrega un repositorio a partir del PATH actual o especificado
                          Ejemplo: git repos -a D:/projects/miproyecto
  
  -u, --update            Verifica que los repositorios registrados sigan existiendo
  
  -r, --remove [ID|PATH]  Oculta repositorios por ID o ruta (no los elimina del disco)
                          Ejemplo: git repos -r 0 2 4
                          
  -g, --goto [ID|TEXTO]   Cambia el directorio de CMD al repositorio especificado
                          Ejemplo: git repos -g 5
                          
  -v, --view [FLAGS]      Muestra metadata detallada de los repositorios encontrados
                          Flags combinables:
                            l (nombre), o (origin), p (path absoluto)
                            b (branch actual), m (fecha ult. commit), c (fecha creacion)
                            h (incluir ocultos), H (mostrar SOLO ocultos)
                          Ejemplo: git repos server -v lomp

EJEMPLOS:
  git repos                     # Listar todos
  git repos binance             # Buscar "binance"
  git repos -s                  # Escanear discos
  git repos -r 5                # Ocultar el ID 5
  git repos -g 5                # Navegar al repositorio 5
  git repos test -v lob         # Buscar "test" y ver origin y branch
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
				# Convertir formato antiguo (str) al nuevo (dict) de forma retrocompatible
				for path, value in list(repos.items()): # Use list() to allow modification during iteration
					if isinstance(value, str):
						repos[path] = {"name": value, "hidden": False}
					elif isinstance(value, dict) and "hidden" not in value:
						value["hidden"] = False
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
						repos[normalized_root] = {"name": repo_name, "hidden": False}
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
	
	repos[normalized_path] = {"name": repo_name, "hidden": False}
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
	for repo_path, repo_data in repos.items():
		if os.path.exists(repo_path) and is_git_repo(repo_path):
			existing_repos[repo_path] = repo_data
		else:
			missing_repos.append((repo_path, repo_data.get("name", os.path.basename(repo_path))))
	
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
	"""Crea un mapa consistente de ID -> ruta basado en el árbol jerárquico global"""
	# Generar IDs para TODOS los repos (incluyendo ocultos) para mantener IDs estables globales
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
			for repo_name, repo_path in sorted(repo_paths_list):
				id_map[repo_id[0]] = repo_path
				repo_id[0] += 1
	
	traverse_tree(tree)
	return id_map

def get_path_to_id_mapping(repos):
	"""Crea un mapa inverso consistente de ruta -> ID para repositorios NO ocultos"""
	id_to_path = get_id_to_path_mapping(repos)
	return {path: id for id, path in id_to_path.items()}

def hide_repos(args):
	"""Oculta repositorios por ID o ruta (en lugar de borrarlos)"""
	if not args:
		print("Error: Debes proporcionar al menos un número o ruta para ocultar")
		print("Ejemplo: git repos -r 0 1 2")
		print("O: git repos -r C:/path/to/repo")
		return

	repos = load_repos()
	if not repos:
		print("No hay repositorios para ocultar")
		return

	path_to_id_map = get_path_to_id_mapping(repos)
	id_to_path_map = get_id_to_path_mapping(repos)
	to_hide_paths = []

	for arg in args:
		# Si es un número (ID)
		if arg.isdigit():
			repo_id = int(arg)
			if repo_id in id_to_path_map:
				to_hide_paths.append(id_to_path_map[repo_id])
			else:
				print(f"[-] ID {repo_id} no encontrado (solo IDs de repositorios visibles)")
		# Si es una ruta
		else:
			clean_path = os.path.abspath(arg).replace('\\', '/')
			if clean_path in repos:
				to_hide_paths.append(clean_path)
			else:
				print(f"[-] Ruta '{arg}' no encontrada en los repositorios registrados")

	if to_hide_paths:
		for path in to_hide_paths:
			repo_data = repos.get(path, {})
			repo_name = repo_data.get("name", os.path.basename(path))
			repos[path]["hidden"] = True
			print(f"  - Ocultando: {repo_name} ({path})")
		
		if save_repos(repos):
			generate_repos_list(repos)
			print(f"\n[+] Se ocultaron {len(to_hide_paths)} repositorio(s)")
		else:
			print("[-] Error al guardar cambios")
	else:
		print("[-] Ningún repositorio válido para ocultar")

def goto_repo(args):
	"""Escribe la ruta del repositorio en .cd_path para que el wrapper haga cd"""
	if not args:
		print("Error: Debes proporcionar un número o nombre para ir")
		print("Ejemplo: git repos -g 5")
		return

	repos = load_repos()
	if not repos:
		print("No hay repositorios registrados.")
		return

	target_path = None
	arg = args[0]

	# Si es un número (ID)
	if arg.isdigit():
		repo_id = int(arg)
		id_to_path_map = get_id_to_path_mapping(repos)
		if repo_id in id_to_path_map:
			target_path = id_to_path_map[repo_id]
		else:
			print(f"[-] ID {repo_id} no encontrado (solo IDs de repositorios visibles)")
			return
	else:
		# Buscar por texto si no es ID
		search_term = arg.lower()
		matches = []
		for path, value in repos.items():
			name = value.get("name", "")
			hidden = value.get("hidden", False)
			if not hidden and (search_term in name.lower() or search_term in path.lower()):
				matches.append(path)
		
		if not matches:
			print(f"[-] No se encontró ningún repositorio visible coincidente con '{arg}'")
			return
		elif len(matches) == 1:
			target_path = matches[0]
		else:
			print(f"[-] Hay múltiples coincidencias para '{arg}'. Usa el ID exacto con 'git repos -g [ID]'.")
			return

	if target_path:
		script_dir = os.path.dirname(os.path.abspath(__file__))
		cd_file_path = os.path.join(script_dir, ".cd_path")
		try:
			# Normalizar a barras invertidas para CMD en Windows
			cmd_path = target_path.replace('/', '\\')
			with open(cd_file_path, "w") as f:
				f.write(cmd_path)
			print(f"[+] Cambiando directorio a: {cmd_path}")
		except Exception as e:
			print(f"[-] Error al preparar el cambio de directorio: {e}")

def fetch_git_details(repo_path, flags):
	"""Obtiene los detalles del repositorio usando comandos de git según las flags (lobmchH)"""
	details = {}
	original_dir = os.getcwd()
	
	try:
		os.chdir(repo_path)
		
		if 'o' in flags: # Origin
			try:
				result = subprocess.run(['git', 'remote', 'get-url', 'origin'], capture_output=True, text=True, check=True)
				details['o'] = result.stdout.strip()
			except subprocess.CalledProcessError:
				details['o'] = "Sin origin"
				
		if 'p' in flags: # Path
			details['p'] = os.path.abspath(repo_path)
			
		if 'b' in flags: # Branch
			try:
				result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], capture_output=True, text=True, check=True)
				details['b'] = result.stdout.strip()
			except subprocess.CalledProcessError:
				details['b'] = "Sin branch"
				
		if 'm' in flags: # Last modify
			try:
				result = subprocess.run(['git', 'log', '-1', '--format=%cd', '--date=short'], capture_output=True, text=True, check=True)
				details['m'] = result.stdout.strip()
			except subprocess.CalledProcessError:
				details['m'] = "Sin commits"

		if 'c' in flags: # Create at (first commit)
			try:
				# Obtenemos el commit root (el primero)
				result = subprocess.run(['git', 'log', '--reverse', '--format=%cd', '--date=short'], capture_output=True, text=True, check=True)
				primer_commit = result.stdout.strip().split('\n')[0]
				details['c'] = primer_commit if primer_commit else "Sin commits"
			except subprocess.CalledProcessError:
				details['c'] = "Sin commits"
				
	except Exception as e:
		pass
	finally:
		os.chdir(original_dir)
		
	return details

def view_repo(args):
	"""Muestra detalles de los repositorios según los argumentos o flags."""
	if not args:
		print("Error: Faltan argumentos para -v")
		return

	flags = ""
	search_term = ""
	
	# Usualmente: git repos [search_term] -v lomp
	# Pero si args tiene '-v' ya se ha filtrado en main, recibimos lo demás
	# Analizamos qué es flag y qué es término de búsqueda
	for arg in args:
		if set(arg).issubset(set("lobmpchH")):
			flags = arg
		else:
			search_term = arg

	repos = load_repos()
	if not repos:
		print("No hay repositorios registrados.")
		return

	id_to_path_map = get_id_to_path_mapping(repos)
	path_to_id_map = get_path_to_id_mapping(repos)
	
	# Determinar qué repos mostrar
	repos_to_show = {}
	
	if not search_term:
		repos_to_show = repos
	elif search_term.isdigit() and int(search_term) in id_to_path_map:
		path = id_to_path_map[int(search_term)]
		repos_to_show = {path: repos[path]}
	else:
		# Búsqueda por texto
		st_lower = search_term.lower()
		for path, value in repos.items():
			name = value.get("name", "")
			if st_lower in name.lower() or st_lower in path.lower():
				repos_to_show[path] = value
				
	if not repos_to_show:
		print(f"[-] No se encontró ningún repositorio coincidente con '{search_term}'")
		return

	# Filtrar ocultos según flags 'h' o 'H'
	include_hidden = 'h' in flags
	only_hidden = 'H' in flags
	
	filtered_repos = {}
	for path, value in repos_to_show.items():
		is_hidden = value.get("hidden", False)
		if only_hidden and not is_hidden:
			continue
		if not only_hidden and not include_hidden and is_hidden:
			continue
		filtered_repos[path] = value

	if not filtered_repos:
		print("[-] No hay repositorios que mostrar con los filtros actuales.")
		return

	# Diccionario para mapear flags a nombres legibles
	flag_names = {'o': 'Origin', 'p': 'Path', 'b': 'Branch', 'm': 'Last Modify', 'c': 'Created At'}
	# Flags solicitadas para recolección (ignoramos l, h, H para git_details)
	fetch_flags = [f for f in flags if f in flag_names]
	
	single_flag = len(fetch_flags) == 1
	
	print("\nDetalles de repositorios:")
	for path in sorted(filtered_repos.keys()):
		value = filtered_repos[path]
		repo_name = value.get("name", os.path.basename(path))
		repo_id = path_to_id_map.get(path, "?")
		is_hidden = value.get("hidden", False)
		
		# Prefijo de ID y estrella si está oculto
		prefix = f"[{repo_id}] "
		if is_hidden:
			prefix += "* "
			
		display_name = f"{prefix}{repo_name}"
		
		# Si solo es 'l' o ninguna de data extra, solo listamos
		if not fetch_flags:
			print(f"{display_name}")
			continue
			
		details = fetch_git_details(path, fetch_flags)
		
		if single_flag:
			# Mostrar en línea
			flag = fetch_flags[0]
			detail_val = details.get(flag, 'N/A')
			print(f"{display_name} {{{detail_val}}}")
		else:
			# Mostrar listado debajo
			print(display_name)
			for flag in fetch_flags:
				print(f"  |-- {flag_names[flag]}: {details.get(flag, 'N/A')}")
	print() # Empty line at the end

def find_repos(search_term=None):
	"""Busca repositorios en la lista guardada"""
	repos = load_repos()
	if not repos:
		print("No hay repositorios registrados.")
		print("Usa 'git repos -s' para escanear y agregar repositorios")
		return

	path_to_id_map = get_path_to_id_mapping(repos)

	if not search_term:
		# Preparar diccionarios filtrando los ocultos
		visible_repos = {p: v["name"] for p, v in repos.items() if not v.get("hidden", False)}
		
		if not visible_repos:
			print("[-] No hay repositorios visibles.")
			return
			
		# Mostrar todos en formato árbol jerárquico
		generate_repos_list(repos) # Generar lista con todos para mantener consistencia de ID
		print("\n[+] Estructura de repositorios:\n")
		tree = build_hierarchical_tree(visible_repos)
		print_hierarchical_tree(tree, external_id_map=path_to_id_map)
	else:
		# Buscar coincidencias solo en los visibles
		filtered_repos = {}
		for path, value in repos.items():
			name = value.get("name", "")
			hidden = value.get("hidden", False)
			if not hidden and (search_term.lower() in name.lower() or search_term.lower() in path.lower()):
				filtered_repos[path] = name

		
		if filtered_repos:
			print(f"\n[?] Resultados para '{search_term}':\n")
			tree = build_hierarchical_tree(filtered_repos)
			print_hierarchical_tree(tree, external_id_map=path_to_id_map)
		else:
			print(f"[-] No se encontraron repositorios que coincidan con '{search_term}'")

def main():
	"""Función principal para manejar la CLI"""
	if len(sys.argv) < 2:
		# Si no hay argumentos (ej: "git repos"), mostrar todos
		find_repos()
		return
	
	first_arg = sys.argv[1].lower()
	
	if first_arg in ["-h", "--help"]:
		show_help()
		return

	# Procesar subcomandos conocidos
	if first_arg in ["-s", "--scan"]:
		scan_path = sys.argv[2] if len(sys.argv) > 2 else None
		scan_repos(scan_path)
	elif first_arg in ["-a", "--add"]:
		add_path = sys.argv[2] if len(sys.argv) > 2 else None
		add_repo(add_path)
	elif first_arg in ["-u", "--update"]:
		update_repos()
	elif first_arg in ["-r", "--remove", "--hide"]:
		hide_repos(sys.argv[2:])
	elif first_arg in ["-g", "--goto"]:
		goto_repo(sys.argv[2:])
	elif first_arg in ["-v", "--view"]:
		view_repo(sys.argv[2:])
	else:
		# Si no es un comando directo, verificamos si contiene -v (ej: git repos server -v lomp)
		if "-v" in sys.argv or "--view" in sys.argv:
			try:
				v_idx = sys.argv.index("-v") if "-v" in sys.argv else sys.argv.index("--view")
				# Extraer los argumentos antes del -v (search term) y después del -v (flags)
				search_args = sys.argv[1:v_idx]
				flags_args = sys.argv[v_idx+1:]
				# Concatenar para view_repo (donde el primer argumento es asumido search_term si no es una flag de letras puras)
				view_repo(search_args + flags_args)
			except ValueError:
				pass
		else:
			# Si no es un comando, tratar todo como término de búsqueda
			search_term = " ".join(sys.argv[1:])
			find_repos(search_term)

if __name__ == "__main__":
	main()