"""
CLI del Compilador Patito
Hecho para la clase de Compiladores

Comandos disponibles:
    patito compile <archivo.patito>  - Compila y genera .obj
    patito run <archivo.obj>         - Ejecuta un .obj
    patito execute <archivo.patito>  - Compila y ejecuta de un jalon
    patito <archivo.patito>          - Muestra analisis completo
"""

import sys
from pathlib import Path


def print_header(text):
    """Imprime un header bonito"""
    print("=" * 50)
    print(text)
    print("=" * 50)


def cmd_compile(source_path: str, output_path: str = None):
    """Compila un archivo .patito a .obj"""
    from .patito_parser import parse_and_validate
    from .obj_generator import ObjGenerator
    
    source_file = Path(source_path)
    
    if not source_file.exists():
        print(f"Error: No encontre el archivo '{source_path}'")
        sys.exit(1)
    
    # Si no me dan nombre de salida, uso el mismo nombre pero .obj
    if output_path is None:
        output_path = source_file.with_suffix('.obj')
    else:
        output_path = Path(output_path)
    
    print_header("Compilador Patito")
    print(f"\nArchivo: {source_file}")
    print(f"Salida:  {output_path}")
    
    # Leo el codigo
    src = source_file.read_text(encoding='utf-8')
    
    # Paso 1: Parsear
    print("\n[1/3] Parseando...")
    try:
        sdt = parse_and_validate(src)
        print("      OK!")
    except Exception as e:
        print(f"      Error de sintaxis: {e}")
        sys.exit(1)
    
    # Paso 2: Checar semantica
    print("[2/3] Checando semantica...")
    if sdt.has_errors():
        print(f"      Errores encontrados:")
        for i, error in enumerate(sdt.errors, 1):
            print(f"        {i}. {error}")
        sys.exit(1)
    print("      OK!")
    
    # Paso 3: Generar .obj
    print("[3/3] Generando .obj...")
    ObjGenerator.generate(sdt, str(output_path))
    print("      OK!")
    
    # Listo!
    print(f"\nCompilacion exitosa!")
    print(f"  Cuadruplos: {len(sdt.quadruples)}")
    print(f"  Funciones:  {len(sdt.func_dir.get_all_functions())}")
    print(f"  Archivo:    {output_path}")


def cmd_run(obj_path: str):
    """Ejecuta un archivo .obj"""
    from .obj_generator import ObjGenerator
    from .virtual_machine import VirtualMachine
    
    obj_file = Path(obj_path)
    
    if not obj_file.exists():
        print(f"Error: No encontre '{obj_path}'")
        sys.exit(1)
    
    print_header("Maquina Virtual Patito")
    print(f"\nEjecutando: {obj_file}")
    print("\n" + "-" * 30)
    print("Salida:")
    print("-" * 30 + "\n")
    
    try:
        obj_data = ObjGenerator.load(str(obj_file))
        vm = VirtualMachine(obj_data)
        output = vm.execute()
        
        # Salto de linea al final
        print("\n")
        print("-" * 30)
        print("Listo!")
        
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


def cmd_execute(source_path: str):
    """Compila y ejecuta un .patito de un jalon"""
    from .patito_parser import parse_and_validate
    from .virtual_machine import VirtualMachine
    
    source_file = Path(source_path)
    
    if not source_file.exists():
        print(f"Error: No encontre '{source_path}'")
        sys.exit(1)
    
    print_header("Patito - Compilar y Ejecutar")
    print(f"\nArchivo: {source_file}")
    
    # Leo el codigo
    src = source_file.read_text(encoding='utf-8')
    
    # Compilar
    print("\nCompilando... ", end="")
    try:
        sdt = parse_and_validate(src)
        
        if sdt.has_errors():
            print("ERROR")
            for error in sdt.errors:
                print(f"  - {error}")
            sys.exit(1)
        
        print("OK!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    
    # Ejecutar
    print("\n" + "-" * 30)
    print("Salida del programa:")
    print("-" * 30 + "\n")
    
    try:
        obj_data = sdt.to_obj()
        vm = VirtualMachine(obj_data)
        output = vm.execute()
        
        # Salto de linea al final para que se vea bien
        print("\n")
        print("-" * 30)
        print("Ejecucion terminada!")
        
    except Exception as e:
        print(f"\nError de ejecucion: {e}")
        sys.exit(1)


def cmd_analyze(source_path: str = None):
    """Muestra el analisis completo del programa"""
    from .patito_parser import parse_and_validate
    
    # Leo el archivo
    if source_path:
        src = Path(source_path).read_text(encoding="utf-8")
    else:
        src = sys.stdin.read()
    
    print_header("Analisis de Programa Patito")
    
    # Parsear
    print("\nParseando...")
    try:
        sdt = parse_and_validate(src)
        print("OK!")
    except Exception as e:
        print(f"Error de sintaxis: {e}")
        sys.exit(1)
    
    # Checar errores
    print("Checando semantica...")
    if sdt.has_errors():
        print(f"\nErrores encontrados:")
        for i, error in enumerate(sdt.errors, 1):
            print(f"  {i}. {error}")
        sys.exit(1)
    print("OK!")
    
    # Mostrar info
    print("\n" + "=" * 50)
    print("RESUMEN")
    print("=" * 50)
    
    # Variables globales
    global_vars = sdt.var_table.global_vars
    if global_vars:
        print(f"\nVariables globales ({len(global_vars)}):")
        for var_name, var_info in global_vars.items():
            addr = f"@{var_info.address}" if var_info.address else ""
            print(f"  {var_name}: {var_info.type} {addr}")
    
    # Funciones
    all_funcs = sdt.func_dir.get_all_functions()
    if all_funcs:
        print(f"\nFunciones ({len(all_funcs)}):")
        for func_name in all_funcs:
            func_info = sdt.func_dir.get_function(func_name)
            params = [f"{n}:{t}" for n, t in func_info.params]
            params_str = ", ".join(params)
            quad = f" [quad:{func_info.quad_start}]" if func_info.quad_start is not None else ""
            print(f"  {func_name}({params_str}) -> {func_info.return_type}{quad}")
            if func_info.local_vars:
                print(f"    Vars locales: {len(func_info.local_vars)}")
    
    # Cuadruplos
    if sdt.quadruples:
        print(f"\nCuadruplos ({len(sdt.quadruples)}):")
        for i, quad in enumerate(sdt.quadruples):
            op, arg1, arg2, res = quad
            a1 = str(arg1) if arg1 is not None else "-"
            a2 = str(arg2) if arg2 is not None else "-"
            r = str(res) if res is not None else "-"
            print(f"  {i:03}: ({op}, {a1}, {a2}, {r})")
    
    print("\n" + "=" * 50)
    print("Compilacion exitosa!")
    print("=" * 50)


def print_usage():
    """Muestra como usar el compilador"""
    print("""
Compilador Patito - Ayuda

Comandos:
  patito compile <archivo.patito> [salida.obj]
      Compila a .obj

  patito run <archivo.obj>
      Ejecuta un .obj

  patito execute <archivo.patito>
      Compila y ejecuta directo

  patito <archivo.patito>
      Muestra analisis (cuadruplos, tablas, etc)

  patito --help
      Esta ayuda

Ejemplos:
  patito compile mi_programa.patito
  patito run mi_programa.obj
  patito execute mi_programa.patito
""")


def main():
    """Main del CLI"""
    args = sys.argv[1:]
    
    if not args:
        cmd_analyze(None)
        return
    
    if args[0] in ['--help', '-h', 'help']:
        print_usage()
        return
    
    if args[0] == 'compile':
        if len(args) < 2:
            print("Error: Falta el archivo")
            print("Uso: patito compile <archivo.patito>")
            sys.exit(1)
        output = args[2] if len(args) > 2 else None
        cmd_compile(args[1], output)
    
    elif args[0] == 'run':
        if len(args) < 2:
            print("Error: Falta el archivo .obj")
            print("Uso: patito run <archivo.obj>")
            sys.exit(1)
        cmd_run(args[1])
    
    elif args[0] == 'execute':
        if len(args) < 2:
            print("Error: Falta el archivo")
            print("Uso: patito execute <archivo.patito>")
            sys.exit(1)
        cmd_execute(args[1])
    
    else:
        # Si no es un comando, asumo que es un archivo
        cmd_analyze(args[0])


if __name__ == "__main__":
    main()
