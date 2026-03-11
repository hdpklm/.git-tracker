import os
import sys
import json
from pathlib import Path
from collections import defaultdict

JSON_FILE = "gitrepos.json"
LIST_FILE = "git-repos-list.json"

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
		file_path = os.path.join(script_dir, LIST_FILE)
		with open(file_path, 'w') as f:
			json.dump(repos_list, f, indent=2)
		return True
	except Exception as e:
		print(f"Error al generar git-repos-list.json: {e}")
		return False

def print_tree_view(repos, show_paths=False):
	"""Imprime los repositorios en formato árbol"""
	if not repos:
		return
	
	tree = build_tree_structure(repos)
	sorted_dirs = sorted(tree.keys())
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
			
			if show_paths:
				print(f"{spacing}{repo_prefix}[{repo_id}] 📦 {name}")
				print(f"{spacing}     📍 {path}")
			else:
				print(f"{spacing}{repo_prefix}[{repo_id}] 📦 {name}")
			
			repo_id += 1

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

def scan_repos(start_path=None):
	"""Escanea un disco o carpeta buscando repositorios Git"""
	if start_path is None:
		# Escanea todas las unidades (en Windows)
		if sys.platform == "win32":
			drives = []
			for i in range(ord('A'), ord('Z') + 1):
				drive = chr(i) + ":"
				if os.path.exists(drive):
					drives.append(drive)
		else:
			drives = ["/"]
	else:
		start_path = os.path.abspath(start_path)
		if not os.path.exists(start_path):
			print(f"Error: El path '{start_path}' no existe")
			return
		drives = [start_path]

	repos = load_repos()
	found_count = 0
	
	print("Escaneando repositorios...")
	
	for drive in drives:
		print(f"Buscando en {drive}...")
		for root, dirs, files in os.walk(drive):
			# Saltar carpetas del sistema y muy profundas
			if ".git" in dirs:
				if is_git_repo(root):
					repo_name = os.path.basename(root)
					# Normalizar path con "/"
					normalized_root = root.replace("\\", "/")
					if normalized_root not in repos:
						repos[normalized_root] = repo_name
						print(f"  ✓ Encontrado: {repo_name} ({normalized_root})")
						found_count += 1
					# Evitar descender más en .git
					dirs.remove(".git")

	if save_repos(repos):
		generate_repos_list(repos)
		print(f"\n✓ Se encontraron y guardaron {found_count} nuevo(s) repositorio(s)")
	else:
		print("✗ Error al guardar repositorios")

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
	
	# Mostrar repos disponibles en formato árbol
	if existing_repos:
		print(f"\n✓ Repositorios disponibles ({len(existing_repos)}):\n")
		print_tree_view(existing_repos)
	
	# Mostrar repos faltantes
	if missing_repos:
		print(f"⚠ Se encontraron {len(missing_repos)} repositorio(s) que ya no existen:\n")
		for i, (path, name) in enumerate(missing_repos):
			print(f"  [{i}] {name}")
			print(f"      {path}")
		print(f"\nPara eliminarlos usa: git_tracker.py -r <números>")
	else:
		print("\n✓ Todos los repositorios están disponibles")
	
	# Guardar solo los repositorios existentes y generar lista
	if save_repos(existing_repos):
		generate_repos_list(existing_repos)
		print(f"\n✓ {len(existing_repos)} repositorio(s) guardado(s)")

def remove_repos(args):
	"""Elimina repositorios por path o número"""
	if not args:
		print("Error: Debes proporcionar al menos un path o número para eliminar")
		print("Ejemplo: git_tracker.py -r 0 1\nO: git_tracker.py -r C:/path/to/repo")
		return
	
	repos = load_repos()
	repos_list = list(repos.items())
	to_remove = []
	
	for arg in args:
		# Verificar si es un número
		if arg.isdigit():
			idx = int(arg)
			if 0 <= idx < len(repos_list):
				to_remove.append(repos_list[idx])
			else:
				print(f"Error: El índice {idx} está fuera de rango")
		else:
			# Es una ruta - normalizar para comparar
			arg_path = os.path.abspath(arg).replace("\\", "/")
			found = False
			for repo_path, repo_name in repos_list:
				if repo_path == arg_path:
					to_remove.append((repo_path, repo_name))
					found = True
					break
			if not found:
				print(f"Advertencia: No se encontró el repositorio con path: {arg_path}")
	
	if to_remove:
		print("Se van a eliminar los siguientes repositorios:")
		for repo_path, repo_name in to_remove:
			print(f"  - {repo_name}")
			print(f"    {repo_path}")
		
		# Eliminar
		for repo_path, _ in to_remove:
			del repos[repo_path]
		
		if save_repos(repos):
			generate_repos_list(repos)
			print(f"\n✓ Se eliminaron {len(to_remove)} repositorio(s)")
		else:
			print("✗ Error al guardar cambios")
	else:
		print("✗ No se encontraron repositorios para eliminar")

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