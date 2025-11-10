from .function_directory import FunctionDirectory
from .variable_table import VariableTable
from .semantic_cube import check_binary_op, check_unary_op, can_assign


class SemanticAnalyzer:
    def __init__(self):
        self.function_directory = FunctionDirectory()
        self.variable_table = VariableTable()
        self.errors = []
        self.current_function = None
    
    def add_error(self, message):
        self.errors.append(message)
    
    def analyze(self, ast):
        self.errors = []
        
        try:
            self.visit_programa(ast)
        except Exception as e:
            self.add_error(str(e))
        
        if self.errors:
            print("\nErrores semánticos encontrados:")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
            return False
        
        print("Análisis semántico completado sin errores")
        return True
    
    # Punto neuralgico 1: Coordinacion general
    def visit_programa(self, node):
        _, prog_name, vars_list, funcs_list, main_body = node
        
        # Punto neuralgico 2: Llenar tabla de variables globales
        self.visit_vars_list(vars_list, is_global=True)
        
        # Punto neuralgico 3: Llenar directorio de funciones
        self.register_functions(funcs_list)
        
        # Punto neuralgico 4: Llenar tablas de variables locales
        self.visit_funcs_list(funcs_list)
        
        self.visit_body(main_body)
    
    def visit_vars_list(self, node, is_global=False):
        _, vars_blocks = node
        for vars_block in vars_blocks:
            self.visit_vars(vars_block, is_global)
    
    def visit_vars(self, node, is_global=False):
        _, id_plus, type_node, vars_plus = node
        
        tipo = type_node[1]
        ids = id_plus[1]
        
        for id_node in ids:
            var_name = id_node[1]
            try:
                if is_global:
                    self.variable_table.add_global_variable(var_name, tipo)
                else:
                    self.variable_table.add_local_variable(var_name, tipo)
            except Exception as e:
                self.add_error(str(e))
        
        _, more_vars = vars_plus
        for grupo in more_vars:
            if len(grupo) >= 2:
                more_ids = grupo[0]
                more_type = grupo[1]
                tipo_extra = more_type[1]
                
                for id_node in more_ids[1]:
                    var_name = id_node[1]
                    try:
                        if is_global:
                            self.variable_table.add_global_variable(var_name, tipo_extra)
                        else:
                            self.variable_table.add_local_variable(var_name, tipo_extra)
                    except Exception as e:
                        self.add_error(str(e))
    
    def register_functions(self, node):
        _, funcs = node
        for func in funcs:
            self.register_function(func)
    
    def register_function(self, node):
        _, func_name, params_node, _, _ = node
        
        try:
            func_info = self.function_directory.add_function(func_name, return_type='void')
            
            _, param_list = params_node
            for param in param_list:
                param_name = param[1]
                param_type = param[2][1]
                
                try:
                    func_info.add_param(param_name, param_type)
                except Exception as e:
                    self.add_error(str(e))
        
        except Exception as e:
            self.add_error(str(e))
    
    def visit_funcs_list(self, node):
        _, funcs = node
        for func in funcs:
            self.visit_func(func)
    
    def visit_func(self, node):
        _, func_name, params_node, vars_list, body = node
        
        self.current_function = func_name
        func_info = self.function_directory.get_function(func_name)
        
        self.variable_table.enter_scope(func_name)
        
        _, param_list = params_node
        for param in param_list:
            param_name = param[1]
            param_type = param[2][1]
            try:
                self.variable_table.add_parameter(param_name, param_type)
            except Exception as e:
                self.add_error(str(e))
        
        self.visit_vars_list(vars_list, is_global=False)
        
        for var_name, var_info in self.variable_table.get_current_scope_vars().items():
            if var_info.kind == 'var':
                try:
                    func_info.add_local_var(var_name, var_info.type)
                except:
                    pass
        
        self.visit_body(body)
        
        self.variable_table.exit_scope()
        self.current_function = None
    
    def visit_body(self, node):
        _, stmts_node = node
        self.visit_statement_plus(stmts_node)
    
    def visit_statement_plus(self, node):
        _, stmts = node
        for stmt in stmts:
            self.visit_statement(stmt)
    
    def visit_statement(self, node):
        stmt_type = node[0]
        
        if stmt_type == 'assign':
            self.visit_assign(node)
        elif stmt_type == 'if_stmt':
            self.visit_if_stmt(node)
        elif stmt_type == 'while_do':
            self.visit_while(node)
        elif stmt_type == 'call':
            self.visit_call(node)
        elif stmt_type == 'print':
            self.visit_print(node)
    
    # Punto neuralgico 6: Validacion de asignaciones
    def visit_assign(self, node):
        _, var_name, expr = node
        
        var_type = self.variable_table.get_variable_type(var_name)
        if var_type is None:
            self.add_error(f"Variable '{var_name}' no declarada")
            return
        
        expr_type = self.visit_expresion(expr)
        if expr_type is None:
            return
        
        if not can_assign(var_type, expr_type):
            self.add_error(f"No se puede asignar {expr_type} a {var_type} en variable '{var_name}'")
    
    def visit_if_stmt(self, node):
        _, if_node = node
        _, condition, then_body, else_opt = if_node
        
        self.visit_expresion(condition)
        self.visit_body(then_body)
        
        _, else_body = else_opt
        if else_body is not None:
            self.visit_body(else_body)
    
    def visit_while(self, node):
        _, condition, body = node
        self.visit_expresion(condition)
        self.visit_body(body)
    
    # Punto neuralgico 7: Validacion de llamadas a funciones
    def visit_call(self, node):
        _, func_name, args = node
        
        if not self.function_directory.function_exists(func_name):
            self.add_error(f"Función '{func_name}' no declarada")
            return
        
        func_info = self.function_directory.get_function(func_name)
        expected_params = func_info.params
        
        if len(args) != len(expected_params):
            self.add_error(f"Función '{func_name}' espera {len(expected_params)} argumentos, pero recibió {len(args)}")
            return
        
        for i, (arg, (param_name, param_type)) in enumerate(zip(args, expected_params)):
            arg_type = self.visit_expresion(arg)
            if arg_type and not can_assign(param_type, arg_type):
                self.add_error(f"Argumento {i+1} de '{func_name}': se esperaba {param_type}, se obtuvo {arg_type}")
    
    def visit_print(self, node):
        _, args = node
        
        for arg in args:
            if arg[0] == 'string':
                continue
            else:
                self.visit_expresion(arg)
    
    # Punto neuralgico 5: Validacion de tipos en expresiones
    def visit_expresion(self, node):
        if node is None:
            return None
        
        expr_type = node[0]
        
        if expr_type == 'cmp':
            _, op, left, right = node
            left_type = self.visit_expresion(left)
            right_type = self.visit_expresion(right)
            
            if left_type is None or right_type is None:
                return None
            
            result_type = check_binary_op(left_type, right_type, op)
            if result_type is None:
                self.add_error(f"Operación inválida: {left_type} {op} {right_type}")
                return None
            return result_type
        
        elif expr_type == 'bin':
            _, op, left, right = node
            left_type = self.visit_expresion(left)
            right_type = self.visit_expresion(right)
            
            if left_type is None or right_type is None:
                return None
            
            result_type = check_binary_op(left_type, right_type, op)
            if result_type is None:
                self.add_error(f"Operación inválida: {left_type} {op} {right_type}")
                return None
            return result_type
        
        elif expr_type == 'un':
            _, op, operand = node
            operand_type = self.visit_expresion(operand)
            
            if operand_type is None:
                return None
            
            result_type = check_unary_op(operand_type, op)
            if result_type is None:
                self.add_error(f"Operación unaria inválida: {op}{operand_type}")
                return None
            return result_type
        
        elif expr_type == 'id':
            _, var_name = node
            var_type = self.variable_table.get_variable_type(var_name)
            if var_type is None:
                self.add_error(f"Variable '{var_name}' no declarada")
                return None
            return var_type
        
        elif expr_type == 'cte_int':
            return 'int'
        
        elif expr_type == 'cte_float':
            return 'float'
        
        else:
            self.add_error(f"Tipo de expresión desconocido: {expr_type}")
            return None
    
