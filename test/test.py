import pytest
from patito.patito_parser import parse_text, parse_and_validate
from lark.exceptions import UnexpectedInput

def ok(src): parse_text(src)

def test_min_program():
    ok('programa P; main { } end')

def test_vars_and_assign_print():
    ok('programa P; var a,b: int; main { a = 1 + 2 * 3; print(a); } end')

def test_if_else():
    ok('programa P; main { if (a > 0) { print(a); } else { print(0); } ; } end')

def test_while_do():
    ok('programa P; main { while (a < 3) do { a = a + 1; } ; } end')

def test_func_and_call():
    ok('programa P; void f(x: int) [ var z: int; { print(x); } ] ; main { f(1); } end')

def test_print_string_and_expr_list():
    ok('programa P; main { print("hola", 1+2, "x"); } end')

def test_invalid_missing_paren():
    with pytest.raises(UnexpectedInput):
        ok('programa P; main { print(1 + 2; } end')


def test_assignment_quadruples():
    sdt = parse_and_validate('programa P; var a: int; main { a = 2 + 3 * 4; } end')
    # Ahora incluye GOTO al inicio y END al final
    assert len(sdt.quadruples) == 5
    # Verificar estructura: GOTO, MUL, PLUS, asignación, END
    assert sdt.quadruples[0][0] == 'GOTO'  # Salto a main
    assert sdt.quadruples[1][0] == 'MUL'
    assert sdt.quadruples[2][0] == 'PLUS'
    assert sdt.quadruples[3][0] == '='
    assert sdt.quadruples[4][0] == 'END'
    # Verificar que se usan direcciones virtuales (números enteros)
    # Constantes: 7000+, Variables globales: 1000+, Temporales: 5000+
    assert isinstance(sdt.quadruples[1][1], int)  # constante 3
    assert isinstance(sdt.quadruples[1][2], int)  # constante 4
    assert isinstance(sdt.quadruples[1][3], int)  # temporal
    assert sdt.quadruples[1][3] >= 5000  # temporal int
    assert isinstance(sdt.quadruples[3][3], int)  # variable a
    assert sdt.quadruples[3][3] >= 1000 and sdt.quadruples[3][3] < 2000  # global int


def test_print_and_relational_quads():
    src = ('programa P; var a: int; main { a = 1; if (a > 0) { print("hola", a + 1); } ; print(a); } end')
    sdt = parse_and_validate(src)
    # Ahora incluye GOTO al inicio y END al final
    assert len(sdt.quadruples) == 9
    # Verificar estructura de operadores (índices +1 por GOTO inicial)
    assert sdt.quadruples[0][0] == 'GOTO'  # Salto a main
    assert sdt.quadruples[1][0] == '='  # asignación
    assert sdt.quadruples[2][0] == 'GT'  # comparación
    assert sdt.quadruples[3][0] == 'GOTOF'  # salto condicional
    assert sdt.quadruples[4][0] == 'PRINT'  # print string
    assert sdt.quadruples[5][0] == 'PLUS'  # suma
    assert sdt.quadruples[6][0] == 'PRINT'  # print expresión
    assert sdt.quadruples[7][0] == 'PRINT'  # print variable
    assert sdt.quadruples[8][0] == 'END'  # fin programa
    # Verificar que se usan direcciones virtuales
    assert isinstance(sdt.quadruples[1][1], int)  # constante 1
    assert sdt.quadruples[1][1] >= 7000  # constante int
    assert isinstance(sdt.quadruples[1][3], int)  # variable a
    assert sdt.quadruples[1][3] >= 1000 and sdt.quadruples[1][3] < 2000  # global int
    assert isinstance(sdt.quadruples[2][3], int)  # temporal resultado GT
    assert sdt.quadruples[2][3] >= 5000  # temporal int
    assert isinstance(sdt.quadruples[3][1], int)  # dirección del temporal en GOTOF
    # Los strings se pasan directamente como valores (no direcciones virtuales)
    assert isinstance(sdt.quadruples[4][1], str)  # valor del string
