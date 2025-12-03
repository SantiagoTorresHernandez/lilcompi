from pathlib import Path
from lark import Lark
from .patito_sdt import PatitoSDT

GRAMMAR_PATH = Path(__file__).with_name("patito.lark")

with open(GRAMMAR_PATH, "r", encoding="utf-8") as f:
    _GRAMMAR = f.read()

_parser = Lark(_GRAMMAR, parser="lalr", maybe_placeholders=False)

def parse_text(text: str):
    return _parser.parse(text)


def parse_and_validate(text: str):
    """
    Parsea y valida semánticamente un programa Patito usando SDT.
    
    Retorna el objeto PatitoSDT que contiene:
    - var_table: tabla de variables
    - func_dir: directorio de funciones
    - errors: lista de errores semánticos encontrados
    """
    tree = _parser.parse(text)
    sdt = PatitoSDT()
    sdt.transform(tree)
    return sdt


