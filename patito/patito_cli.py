import sys
from pathlib import Path
from .patito_parser import parse_text
from .semantic_analyzer import SemanticAnalyzer

def main():
    if len(sys.argv) > 1:
        src = Path(sys.argv[1]).read_text(encoding="utf-8")
    else:
        src = sys.stdin.read()
    
    # Análisis léxico y sintáctico
    print("Iniciando analisis lexico y sintactico\n")
    try:
        ast = parse_text(src)
        print("Analisis sintactico exitoso\n")
    except Exception as e:
        print(f"Error de sintaxis: {e}\n")
        sys.exit(1)
    
    # Análisis semántico
    print("Iniciando analisis semantico\n")
    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(ast)
    
    if success:
        print("\nCompilacion exitosa\n")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()

