import sys
from pathlib import Path
from .patito_parser import parse_text

def main():
    if len(sys.argv) > 1:
        src = Path(sys.argv[1]).read_text(encoding="utf-8")
    else:
        src = sys.stdin.read()
    ast = parse_text(src)
    print(ast)

if __name__ == "__main__":
    main()

