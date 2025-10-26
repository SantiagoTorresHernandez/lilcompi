from pathlib import Path
from lark import Lark
from .patito_ast import PatitoAST

GRAMMAR_PATH = Path(__file__).with_name("patito.lark")

with open(GRAMMAR_PATH, "r", encoding="utf-8") as f:
    _GRAMMAR = f.read()

_parser = Lark(_GRAMMAR, parser="lalr", maybe_placeholders=False)

def parse_text(text: str):
    """Devuelve un AST (tupla) a partir del programa Patito."""
    tree = _parser.parse(text)
    ast = PatitoAST().transform(tree)
    return ast

