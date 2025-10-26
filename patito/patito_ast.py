from lark import Transformer, v_args, Token, Tree

@v_args(inline=True)
class PatitoAST(Transformer):
    # --- Utilidades
    def ID(self, t: Token):
        return ("id", t.value)

    def CTE_INT(self, t: Token):
        return ("cte_int", int(t.value))

    def CTE_FLOAT(self, t: Token):
        return ("cte_float", float(t.value))

    def STRING(self, t: Token):
        # preserva comillas/escapes si quieres
        return ("string", t.value)

    # --- Start rule (top level)
    def start(self, programa):
        return programa

    # --- Programa
    def programa(self, *items):
        # KW_PROG ID ; vars_list funcs_list KW_MAIN body KW_END
        _, prog_id, _, vars_l, funcs_l, _, body, _ = items
        return ("programa", prog_id[1], vars_l, funcs_l, body)

    # --- Vars
    def vars_list(self, *xs):
        return ("vars_list", [x for x in xs])

    def vars(self, *xs):
        # KW_VAR id_plus : type ; vars_plus
        _, idp, _, ty, _, vplus = xs
        return ("vars", idp, ty, vplus)

    def vars_plus(self, *xs):
        return ("vars_plus", list(xs))

    def id_plus(self, first, *rest):
        ids = [first] + list(rest[1::2]) if rest else [first]
        return ("id_plus", ids)

    def type(self, t):
        # KW_INT | KW_FLOAT
        return ("type", t.type.lower().replace("kw_", ""))  # int/float

    # --- Funcs
    def funcs_list(self, *xs):
        return ("funcs_list", list(xs))

    def func(self, *xs):
        # KW_VOID ID LP funcs_params RP LBR vars_list body RBR SEMI
        _, fid, _, params, _, _, vlist, body, _, _ = xs
        return ("func", fid[1], params, vlist, body)

    def funcs_params(self, *xs):
        # (param (COMMA param)*)?
        if not xs:
            return ("params", [])
        # normaliza en lista plana
        params = [xs[0]]
        if len(xs) > 1:
            tail = xs[1:]
            params += [p for (_, p) in zip(tail[0::2], tail[1::2])]
        return ("params", params)

    def param(self, idtok, _c, ty):
        return ("param", idtok[1], ty)

    # --- Body / statements
    def body(self, _lb, stmts, _rb):
        return ("body", stmts)

    def statement_plus(self, *xs):
        return ("stmts", list(xs))

    def statement(self, x):
        return x

    def assign(self, idtok, _eq, expr, _semi):
        return ("assign", idtok[1], expr)

    def condition(self, ifc, _semi):
        return ("if_stmt", ifc)

    def if_condition(self, _if, _lp, cond, _rp, then_body, else_opt, _semi):
        return ("if", cond, then_body, else_opt)

    def else_opt(self, *xs):
        return ("else", xs[1]) if xs else ("else", None)

    def cycle(self, _w, _lp, cond, _rp, _do, cuerpo, _semi):
        return ("while_do", cond, cuerpo)

    def cuerpo(self, body):
        return body

    def f_call(self, idtok, _lp, args, _rp, _semi):
        # args puede ser None (cuando no hay exp_plus)
        if isinstance(args, Tree) and args.data == "exp_plus":
            # lo transformará la regla exp_plus
            pass
        return ("call", idtok[1], args if args else [])

    def exp_plus(self, *xs):
        # (expresion (COMMA expresion)*)?
        if not xs:
            return []
        if len(xs) == 1:
            return [xs[0]]
        # a,b,c...
        acc = [xs[0]]
        tail = xs[1:]
        acc += [e for (_, e) in zip(tail[0::2], tail[1::2])]
        return acc

    def print_stmt(self, _p, _lp, args, _rp, _semi):
        return ("print", args)

    def print_args(self, *xs):
        # (STRING | expr) ( , (STRING|expr) )*
        acc = []
        i = 0
        while i < len(xs):
            acc.append(xs[i])
            i += 2
        return acc

    # --- Expresiones helpers
    def comparador(self, op):
        # Returns the operator token itself
        return op

    def signo(self, t):
        # Returns the token (PLUS or MINUS)
        return t
        
    def operador(self, op):
        # Returns the operator token itself
        return op
    
    # --- Expresiones
    def expr_cmp_opt(self, a, *rest):
        # a [op b]
        if not rest:
            return a
        op, b = rest
        # op is already a token from comparador
        return ("cmp", op.type, a, b)  # GT/LT/NEQ

    def expr_addsub(self, first, *pairs):
        # term (SIGNO term)*
        node = first
        i = 0
        while i < len(pairs):
            sign = pairs[i]
            term = pairs[i + 1]
            # sign is already a token from SIGNO
            node = ("bin", sign.type, node, term)  # PLUS/MINUS
            i += 2
        return node

    def expr_muldiv(self, first, *pairs):
        node = first
        i = 0
        while i < len(pairs):
            op = pairs[i]
            fac = pairs[i + 1]
            # op is already a token from operador
            node = ("bin", op.type, node, fac)    # MUL/DIV
            i += 2
        return node

    def factor(self, *args):
        # factor can be: LP expresion RP | SIGNO valor (->signed) | valor
        if len(args) == 3:
            # LP expresion RP - just return the expression
            _, expr, _ = args
            return expr
        elif len(args) == 1:
            # valor - just return it
            return args[0]
        else:
            # This shouldn't happen as signed is handled separately
            return args[0] if args else None

    def signed(self, sign, val):
        # sign is already a token from SIGNO
        return ("un", sign.type, val)

    def valor(self, v):
        return v

    def cte(self, v):
        return v

