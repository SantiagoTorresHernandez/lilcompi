SEMANTIC_CUBE = {
    ('int', 'int', 'PLUS'): 'int',
    ('int', 'float', 'PLUS'): 'float',
    ('float', 'int', 'PLUS'): 'float',
    ('float', 'float', 'PLUS'): 'float',
    ('int', 'int', 'MINUS'): 'int',
    ('int', 'float', 'MINUS'): 'float',
    ('float', 'int', 'MINUS'): 'float',
    ('float', 'float', 'MINUS'): 'float',
    ('int', 'int', 'MUL'): 'int',
    ('int', 'float', 'MUL'): 'float',
    ('float', 'int', 'MUL'): 'float',
    ('float', 'float', 'MUL'): 'float',
    ('int', 'int', 'DIV'): 'int',
    ('int', 'float', 'DIV'): 'float',
    ('float', 'int', 'DIV'): 'float',
    ('float', 'float', 'DIV'): 'float',
    ('int', 'int', 'GT'): 'int',
    ('int', 'float', 'GT'): 'int',
    ('float', 'int', 'GT'): 'int',
    ('float', 'float', 'GT'): 'int',
    ('int', 'int', 'LT'): 'int',
    ('int', 'float', 'LT'): 'int',
    ('float', 'int', 'LT'): 'int',
    ('float', 'float', 'LT'): 'int',
    ('int', 'int', 'NEQ'): 'int',
    ('int', 'float', 'NEQ'): 'int',
    ('float', 'int', 'NEQ'): 'int',
    ('float', 'float', 'NEQ'): 'int',
}

UNARY_OPERATORS = {
    ('int', 'PLUS'): 'int',
    ('int', 'MINUS'): 'int',
    ('float', 'PLUS'): 'float',
    ('float', 'MINUS'): 'float',
}


def check_binary_op(left_type, right_type, operator):
    key = (left_type, right_type, operator)
    return SEMANTIC_CUBE.get(key, None)


def check_unary_op(operand_type, operator):
    key = (operand_type, operator)
    return UNARY_OPERATORS.get(key, None)


def can_assign(var_type, expr_type):
    if var_type == expr_type:
        return True
    if var_type == 'float' and expr_type == 'int':
        return True
    return False

