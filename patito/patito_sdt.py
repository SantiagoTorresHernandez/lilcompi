from lark import Transformer, Visitor, v_args, Token
from .variable_table import VariableTable
from .function_directory import FunctionDirectory
from .semantic_cube import check_binary_op, check_unary_op, can_assign
from .memory_map import MemoryMap
from .constant_table import ConstantTable


class PatitoSDT:
    
    def __init__(self):
        self.var_table = VariableTable()
        self.func_dir = FunctionDirectory()
        self.memory_map = MemoryMap()
        self.constant_table = ConstantTable(self.memory_map)
        self.errors = []
        self.current_function = None
        self.program_name = None
        self.operator_stack = [] # pila de operadores
        self.operand_stack = []  # pila que almacena direcciones virtuales 
        self.type_stack = [] # pila de tipos
        self.quadruples = [] # lista de cuádruplos
        self.temp_counter = 0
        self.jump_stack = [] # pila de saltos
        self.main_goto_index = None  # Índice del GOTO a main
    
    def add_error(self, message):
        self.errors.append(message)
    
    def has_errors(self):
        return len(self.errors) > 0
    
    def transform(self, tree):
        # Generar GOTO main como primer cuádruplo
        self.main_goto_index = self.gen_quad('GOTO', None, None, None)
        
        registrar = _RegistrarDeclaraciones(self)
        registrar.visit(tree)
        
        validar = _ValidarSemantica(self)
        validar.visit(tree)
        
        return None
    
    def create_return_variable(self, func_name, return_type):
        """
        Crea una variable global para almacenar el valor de retorno de una función.
        
        Args:
            func_name: Nombre de la función
            return_type: Tipo de retorno ('int' o 'float')
        
        Returns:
            int: Dirección virtual de la variable de retorno
        """
        var_name = f"_return_{func_name}"
        address = self.memory_map.assign_global(return_type)
        self.var_table.add_global_variable(var_name, return_type, address=address)
        return address

    def new_temp(self, temp_type='int'):
        """
        Genera un nuevo temporal y retorna su dirección virtual.
        
        Args:
            temp_type: Tipo del temporal ('int' o 'float')
        
        Returns:
            int: Dirección virtual del temporal
        """
        return self.memory_map.assign_temp(temp_type)
    
    def gen_quad(self, op, left, right, result):
        self.quadruples.append((op, left, right, result))
        return len(self.quadruples) - 1
    
    def get_quad_counter(self):
        return len(self.quadruples)
    
    def fill_quad(self, index, value):
        if 0 <= index < len(self.quadruples):
            quad = self.quadruples[index]
            self.quadruples[index] = (quad[0], quad[1], quad[2], value)
    
    def to_obj(self):
        """
        Exporta los datos necesarios para el archivo .obj.
        
        Returns:
            dict: Diccionario con cuádruplos, constantes y funciones
        """
        # Convertir cuádruplos a formato serializable
        quads_list = []
        for op, arg1, arg2, result in self.quadruples:
            quads_list.append([op, arg1, arg2, result])
        
        # Obtener constantes (invertir diccionario para tener addr -> value)
        constants = {}
        for value, addr in self.constant_table.constants.items():
            # Solo incluir constantes numéricas (no strings)
            if isinstance(addr, int):
                constants[addr] = value
        
        return {
            'program_name': self.program_name,
            'quadruples': quads_list,
            'constants': constants,
            'functions': self.func_dir.to_dict()
        }


class _RegistrarDeclaraciones(Visitor):
    
    def __init__(self, sdt):
        super().__init__()
        self.sdt = sdt
    
    def __default__(self, tree):
        pass
    
   
    def programa(self, tree):
        prog_name = tree.children[1].value # PN1
        self.sdt.program_name = prog_name
        self.sdt.func_dir.set_program(prog_name)
        
        vars_list_tree = tree.children[3]
        self._process_global_vars(vars_list_tree)
    
    def _process_global_vars(self, tree):
        if tree is None or not hasattr(tree, 'children'):
            return
        
        for child in tree.children:
            if hasattr(child, 'data') and child.data == 'vars':
                self._process_vars_global(child)
    
    def _process_vars_global(self, tree):
        id_plus_tree = tree.children[1]
        type_tree = tree.children[3]
        
        ids = self._extract_ids(id_plus_tree)
        tipo = self._extract_type(type_tree)
        
        for var_name in ids: #PN2
            try:
                # Asignar dirección virtual
                address = self.sdt.memory_map.assign_global(tipo)
                self.sdt.var_table.add_global_variable(var_name, tipo, address=address)
            except Exception as e:
                self.sdt.add_error(str(e))
        
        vars_plus_tree = tree.children[5]
        self._process_vars_plus(vars_plus_tree, is_global=True)
    
    def vars(self, tree):
        pass
    
    
    def func(self, tree): #PN3
        # func_type está en children[0], func_name en children[1]
        func_type_tree = tree.children[0]
        func_name = tree.children[1].value
        params_tree = tree.children[3]
        
        # Extraer tipo de retorno de func_type
        return_type = self._extract_func_type(func_type_tree)
        
        try:
            func_info = self.sdt.func_dir.add_function(func_name, return_type=return_type)
            
            # Si la función no es void, crear variable global para valor de retorno
            if return_type != 'void':
                return_addr = self.sdt.create_return_variable(func_name, return_type)
                func_info.set_return_address(return_addr)
            
            params = self._extract_params(params_tree) #PN4
            for param_name, param_type in params:
                try:
                    func_info.add_param(param_name, param_type)
                except Exception as e:
                    self.sdt.add_error(str(e))
        except Exception as e:
            self.sdt.add_error(str(e))
    
    def _extract_func_type(self, tree):
        """Extrae el tipo de retorno de func_type (KW_VOID | KW_INT | KW_FLOAT)"""
        if tree is None:
            return 'void'
        if hasattr(tree, 'data') and tree.data == 'func_type':
            type_token = tree.children[0]
            return type_token.type.lower().replace("kw_", "")
        return 'void'
    
    def _extract_ids(self, tree):
        ids = []
        for child in tree.children:
            if isinstance(child, Token) and child.type == 'ID':
                ids.append(child.value)
        return ids
    
    def _extract_type(self, tree):
        type_token = tree.children[0]
        return type_token.type.lower().replace("kw_", "")
    
    def _process_vars_plus(self, tree, is_global=False):
        if tree is None or not hasattr(tree, 'children'):
            return
        i = 0
        children = tree.children
        while i + 3 < len(children):
            id_plus_tree = children[i]
            type_tree = children[i + 2]
            
            ids = self._extract_ids(id_plus_tree)
            tipo = self._extract_type(type_tree)
            
            for var_name in ids:
                try:
                    if is_global:
                        # Asignar dirección virtual global
                        address = self.sdt.memory_map.assign_global(tipo)
                        self.sdt.var_table.add_global_variable(var_name, tipo, address=address)
                    else:
                        # Asignar dirección virtual local
                        address = self.sdt.memory_map.assign_local(tipo)
                        self.sdt.var_table.add_local_variable(var_name, tipo, address=address)
                except Exception as e:
                    self.sdt.add_error(str(e))
            
            i += 4
    
    def _extract_params(self, tree):
        params = []
        for child in tree.children:
            if hasattr(child, 'data') and child.data == 'param':
                param_name = child.children[0].value
                param_type = self._extract_type(child.children[2])
                params.append((param_name, param_type))
        return params


class _ValidarSemantica(Visitor):
    
    def __init__(self, sdt):
        super().__init__()
        self.sdt = sdt
    
    def __default__(self, tree):
        pass
    
    def programa(self, tree):
        funcs_list_tree = tree.children[4]
        if funcs_list_tree and hasattr(funcs_list_tree, 'children'):
            for func_tree in funcs_list_tree.children:
                if hasattr(func_tree, 'data') and func_tree.data == 'func':
                    self.func(func_tree)
        
        # Rellenar el GOTO main con el índice actual
        if self.sdt.main_goto_index is not None:
            self.sdt.fill_quad(self.sdt.main_goto_index, self.sdt.get_quad_counter())
        
        main_body_tree = tree.children[6]
        self._visit_body(main_body_tree)
        
        # Generar cuádruplo END al final del programa
        self.sdt.gen_quad('END', None, None, None)
    
    def func(self, tree):
        # Índices actualizados: func_type está en [0], ID en [1]
        func_name = tree.children[1].value
        params_tree = tree.children[3]
        vars_list_tree = tree.children[6]
        body_tree = tree.children[7]
        
        self.sdt.current_function = func_name
        func_info = self.sdt.func_dir.get_function(func_name)
        
        # Registrar el inicio de la función (quad_start)
        if func_info:
            func_info.set_quad_start(self.sdt.get_quad_counter())
        
        # Entrar a función (resetear contadores locales y temporales)
        self.sdt.memory_map.enter_function() #PN5 :entrar a scope local de la funcion
        self.sdt.var_table.enter_scope(func_name)
        
        params = self._extract_params(params_tree)
        for param_name, param_type in params:
            try:
                # Asignar dirección virtual para parámetro
                address = self.sdt.memory_map.assign_local(param_type)
                self.sdt.var_table.add_parameter(param_name, param_type, address=address)
            except Exception as e:
                self.sdt.add_error(str(e))
        
        self._process_vars_list(vars_list_tree) #PN6 :procesar variables locales de la funcion
        
        if func_info:
            for var_name, var_info in self.sdt.var_table.get_current_scope_vars().items():
                if var_info.kind == 'var':
                    try:
                        func_info.add_local_var(var_name, var_info.type)
                    except:
                        pass
        
        self._visit_body(body_tree)
        
        # Guardar recursos usados por la función antes de salir
        if func_info:
            resources = self.sdt.memory_map.get_function_resources()
            func_info.set_resources(
                local_int=resources['local_int'],
                local_float=resources['local_float'],
                temp_int=resources['temp_int'],
                temp_float=resources['temp_float']
            )
        
        # Generar ENDFUNC al final de la función
        self.sdt.gen_quad('ENDFUNC', None, None, None)
        
        self.sdt.var_table.exit_scope()
        self.sdt.memory_map.exit_function()
        self.sdt.current_function = None
    
    def _visit_body(self, tree):
        if tree is None or not hasattr(tree, 'data') or tree.data != 'body':
            return
        
        statement_plus_tree = tree.children[1]
        
        if statement_plus_tree and hasattr(statement_plus_tree, 'children'):
            for statement_tree in statement_plus_tree.children:
                if hasattr(statement_tree, 'data'):
                    if statement_tree.data == 'statement' and len(statement_tree.children) > 0:
                        actual_statement = statement_tree.children[0]
                        if hasattr(actual_statement, 'data'):
                            self._dispatch_statement(actual_statement)
                    else:
                        self._dispatch_statement(statement_tree)
    
    def _dispatch_statement(self, tree):
        """Despacha el procesamiento de un estatuto según su tipo."""
        if not hasattr(tree, 'data'):
            return
        
        if tree.data == 'assign':
            self._validate_assign(tree)
        elif tree.data == 'f_call':
            self._validate_f_call(tree)
        elif tree.data == 'condition':
            self._visit_condition(tree)
        elif tree.data == 'cycle':
            self._visit_cycle(tree)
        elif tree.data == 'print_stmt':
            self._visit_print_stmt(tree)
        elif tree.data == 'return_stmt':
            self._visit_return_stmt(tree)
    
    def _visit_condition(self, tree):
        if_condition_tree = tree.children[0]
        
        cond_tree = if_condition_tree.children[2]
        self._eval_expresion(cond_tree)
        result_addr, result_type = self._build_quads(cond_tree)
        
        gotof_generated = False #PN9: gotof generado
        if result_addr is not None and result_type is not None:
            # GOTOF usa dirección virtual del resultado de la condición
            gotof_idx = self.sdt.gen_quad('GOTOF', result_addr, None, None)
            self.sdt.jump_stack.append(gotof_idx)
            gotof_generated = True
        
        then_body_tree = if_condition_tree.children[4]
        self._visit_body(then_body_tree)
        
        else_opt_tree = if_condition_tree.children[5]
        has_else = else_opt_tree and hasattr(else_opt_tree, 'children') and len(else_opt_tree.children) >= 2
        
        if has_else: #PN10: else generado
            goto_idx = self.sdt.gen_quad('GOTO', None, None, None)
            if len(self.sdt.jump_stack) > 0:
                false_jump = self.sdt.jump_stack.pop()
                self.sdt.fill_quad(false_jump, self.sdt.get_quad_counter())
            
            else_body_tree = else_opt_tree.children[1]
            self._visit_body(else_body_tree)
            
            self.sdt.fill_quad(goto_idx, self.sdt.get_quad_counter()) #PN11: rellenar cuádruplo de goto, despues del else
        else:
            if gotof_generated and len(self.sdt.jump_stack) > 0: #PN12: rellenar cuádruplo de gotof sin else
                false_jump = self.sdt.jump_stack.pop()
                self.sdt.fill_quad(false_jump, self.sdt.get_quad_counter())
    
    def _visit_cycle(self, tree):
        loop_start = self.sdt.get_quad_counter() #PN13: inicio del ciclo
        
        cond_tree = tree.children[2]
        self._eval_expresion(cond_tree)
        result_addr, result_type = self._build_quads(cond_tree)
        
        if result_addr is not None and result_type is not None: #PN14: gotof generado
            # GOTOF usa dirección virtual del resultado de la condición
            gotof_idx = self.sdt.gen_quad('GOTOF', result_addr, None, None)
            self.sdt.jump_stack.append(gotof_idx)
        
        cuerpo_tree = tree.children[5]
        if cuerpo_tree and hasattr(cuerpo_tree, 'data') and cuerpo_tree.data == 'cuerpo':
            body_tree = cuerpo_tree.children[0]
            self._visit_body(body_tree)
        
        #GOTO usa dirección de cuádruplo (índice)
        self.sdt.gen_quad('GOTO', None, None, loop_start) #PN15: goto generado al inicio del ciclo
        
        if len(self.sdt.jump_stack) > 0: #PN16: rellenar cuádruplo de goto, despues del ciclo
            exit_jump = self.sdt.jump_stack.pop()
            self.sdt.fill_quad(exit_jump, self.sdt.get_quad_counter())
    
    def _visit_print_stmt(self, tree):
        print_args_tree = tree.children[2]
        
        if not print_args_tree or not hasattr(print_args_tree, 'children'):
            return
        
        for child in print_args_tree.children:
            if isinstance(child, Token):
                if child.type == 'STRING':
                    #strings se pasan directamente, solo quitamos las comillas
                    str_value = child.value[1:-1] if child.value.startswith('"') else child.value
                    self.sdt.gen_quad('PRINT', str_value, None, None)
                continue
            if hasattr(child, 'data') and child.data in ['expresion', 'expr_cmp_opt']:
                self._eval_expresion(child)
                result_addr, result_type = self._build_quads(child)
                if result_addr is not None and result_type is not None:
                    self.sdt.gen_quad('PRINT', result_addr, None, None)
    
    def _visit_return_stmt(self, tree):
        """
        Procesa un estatuto return: return(expresion);
        
        Genera cuádruplo: (RETURN, expr_addr, None, return_addr)
        """
        # Verificar que estamos dentro de una función
        if self.sdt.current_function is None:
            self.sdt.add_error("return fuera de una función")
            return
        
        func_info = self.sdt.func_dir.get_function(self.sdt.current_function)
        if func_info is None:
            self.sdt.add_error(f"Función '{self.sdt.current_function}' no encontrada")
            return
        
        # Verificar que la función no sea void
        if func_info.return_type == 'void':
            self.sdt.add_error(f"Función void '{self.sdt.current_function}' no puede retornar un valor")
            return
        
        # Evaluar la expresión de retorno
        expr_tree = tree.children[2]  # return ( expresion ) ;
        expr_type = self._eval_expresion(expr_tree)
        
        # Verificar compatibilidad de tipos
        if expr_type and not can_assign(func_info.return_type, expr_type):
            self.sdt.add_error(
                f"Tipo de retorno incompatible en '{self.sdt.current_function}': "
                f"se esperaba {func_info.return_type}, se obtuvo {expr_type}"
            )
            return
        
        # Generar cuádruplos para la expresión
        result_addr, result_type = self._build_quads(expr_tree)
        
        if result_addr is not None:
            # Generar cuádruplo RETURN
            self.sdt.gen_quad('RETURN', result_addr, None, func_info.return_address)

    def _validate_assign(self, tree):
        var_name = tree.children[0].value # nombre de variable
        expr_tree = tree.children[2] # expresion
        
        var_type = self.sdt.var_table.get_variable_type(var_name)
        if var_type is None:
            self.sdt.add_error(f"Variable '{var_name}' no declarada")
            return
        
        var_address = self.sdt.var_table.get_variable_address(var_name)
        if var_address is None:
            self.sdt.add_error(f"Variable '{var_name}' no tiene dirección asignada")
            return
        
        expr_type = self._eval_expresion(expr_tree)
        if expr_type is None:
            return
        
        if expr_type and not can_assign(var_type, expr_type): #PN 7: verificar compatibilidad de tipos
            self.sdt.add_error(f"No se puede asignar {expr_type} a {var_type} en variable '{var_name}'")
            return
        
        result_addr, result_type = self._build_quads(expr_tree)
        if result_addr is not None and result_type is not None: #PN *: generar cuadruplo de asignacion
            # Usar direcciones virtuales en el cuádruplo
            self.sdt.gen_quad('=', result_addr, None, var_address)

    def _validate_f_call(self, tree):
        """
        Valida y genera cuádruplos para llamada a función.
        
        Genera:
            (ERA, func_name, None, None)         - Activar registro de activación
            (PARAM, arg_addr, None, param_num)   - Por cada argumento
            (GOSUB, func_name, None, quad_start) - Saltar a función
        """
        func_name = tree.children[0].value
        args_tree = tree.children[2]
        
        if not self.sdt.func_dir.function_exists(func_name):
            self.sdt.add_error(f"Función '{func_name}' no declarada")
            return None
        
        func_info = self.sdt.func_dir.get_function(func_name)
        expected_params = func_info.params
        
        arg_types = self._eval_exp_plus(args_tree)
        
        if len(arg_types) != len(expected_params):
            self.sdt.add_error(f"Función '{func_name}' espera {len(expected_params)} argumentos, pero recibió {len(arg_types)}")
            return None
        
        # Validar tipos de argumentos
        for i, (arg_type, (param_name, param_type)) in enumerate(zip(arg_types, expected_params)):
            if arg_type and not can_assign(param_type, arg_type):
                self.sdt.add_error(f"Argumento {i+1} de '{func_name}': se esperaba {param_type}, se obtuvo {arg_type}")
                return None
        
        # Generar cuádruplo ERA (Expansion of Activation Record)
        self.sdt.gen_quad('ERA', func_name, None, None)
        
        # Generar cuádruplos PARAM para cada argumento
        arg_addrs = self._get_arg_addresses(args_tree)
        for i, arg_addr in enumerate(arg_addrs):
            if arg_addr is not None:
                self.sdt.gen_quad('PARAM', arg_addr, None, i)
        
        # Generar cuádruplo GOSUB
        self.sdt.gen_quad('GOSUB', func_name, None, func_info.quad_start)
        
        # Si la función retorna valor, asignarlo a un temporal
        if func_info.return_type != 'void' and func_info.return_address is not None:
            temp_addr = self.sdt.new_temp(func_info.return_type)
            self.sdt.gen_quad('=', func_info.return_address, None, temp_addr)
            return temp_addr, func_info.return_type
        
        return None
    
    def _get_arg_addresses(self, tree):
        """
        Obtiene las direcciones virtuales de los argumentos de una llamada.
        Genera los cuádruplos necesarios para evaluar cada expresión.
        """
        if tree is None:
            return []
        
        if not hasattr(tree, 'data') or tree.data != 'exp_plus':
            return []
        
        if not hasattr(tree, 'children') or len(tree.children) == 0:
            return []
        
        addresses = []
        for child in tree.children:
            if hasattr(child, 'data') and child.data in ['expresion', 'expr_cmp_opt']:
                result_addr, result_type = self._build_quads(child)
                addresses.append(result_addr)
        
        return addresses
    
    def _build_quads(self, tree):
        builder = _ExpressionQuadBuilder(self.sdt)
        return builder.build(tree)


    def _eval_expresion(self, tree):
        if tree is None:
            return None
        
        if hasattr(tree, 'data'):
            if tree.data == 'expr_cmp_opt':
                exp1 = tree.children[0]
                tipo1 = self._eval_exp(exp1)
                
                if len(tree.children) > 1:
                    comparador = tree.children[1]
                    exp2 = tree.children[2]
                    tipo2 = self._eval_exp(exp2)
                    
                    if tipo1 and tipo2:
                        op_type = comparador.children[0].type
                        result = check_binary_op(tipo1, tipo2, op_type)
                        if result is None:
                            self.sdt.add_error(f"Operación inválida: {tipo1} {op_type} {tipo2}")
                        return result
                
                return tipo1
        
        return self._eval_exp(tree)
    
    def _eval_exp(self, tree):
        if tree is None:
            return None
        
        if hasattr(tree, 'data') and tree.data == 'expr_addsub':
            tipo_resultado = self._eval_term(tree.children[0])
            
            i = 1
            while i + 1 < len(tree.children):
                signo = tree.children[i]
                term = tree.children[i + 1]
                
                tipo_term = self._eval_term(term)
                if tipo_resultado and tipo_term:
                    op_type = signo.children[0].type
                    tipo_resultado = check_binary_op(tipo_resultado, tipo_term, op_type)
                    if tipo_resultado is None:
                        self.sdt.add_error(f"Operación inválida: {op_type} entre tipos incompatibles")
                
                i += 2
            
            return tipo_resultado
        
        return self._eval_term(tree)
    
    def _eval_term(self, tree):
        if tree is None:
            return None
        
        if hasattr(tree, 'data') and tree.data == 'expr_muldiv':
            tipo_resultado = self._eval_factor(tree.children[0])
            
            i = 1
            while i + 1 < len(tree.children):
                operador = tree.children[i]
                factor = tree.children[i + 1]
                
                tipo_factor = self._eval_factor(factor)
                if tipo_resultado and tipo_factor:
                    op_type = operador.children[0].type
                    tipo_resultado = check_binary_op(tipo_resultado, tipo_factor, op_type)
                    if tipo_resultado is None:
                        self.sdt.add_error(f"Operación inválida: {op_type} entre tipos incompatibles")
                
                i += 2
            
            return tipo_resultado
        
        return self._eval_factor(tree)
    
    def _eval_factor(self, tree):
        if tree is None:
            return None
        
        if hasattr(tree, 'data'):
            if tree.data == 'factor':
                if len(tree.children) == 3:
                    return self._eval_expresion(tree.children[1])
                elif len(tree.children) == 1:
                    return self._eval_valor(tree.children[0])
            elif tree.data == 'signed':
                signo = tree.children[0]
                valor = tree.children[1]
                
                tipo_valor = self._eval_valor(valor)
                if tipo_valor:
                    op_type = signo.children[0].type
                    result = check_unary_op(tipo_valor, op_type)
                    if result is None:
                        self.sdt.add_error(f"Operación unaria inválida: {op_type}{tipo_valor}")
                    return result
        
        return self._eval_valor(tree)
    
    def _eval_valor(self, tree):
        if tree is None:
            return None
        
        if isinstance(tree, Token):
            if tree.type == 'ID':
                var_type = self.sdt.var_table.get_variable_type(tree.value)
                if var_type is None:
                    self.sdt.add_error(f"Variable '{tree.value}' no declarada")
                return var_type
            elif tree.type == 'CTE_INT':
                return 'int'
            elif tree.type == 'CTE_FLOAT':
                return 'float'
            elif tree.type == 'STRING':
                return 'string'
        
        if hasattr(tree, 'data'):
            if tree.data == 'valor':
                return self._eval_valor(tree.children[0])
            elif tree.data == 'cte':
                return self._eval_valor(tree.children[0])
            elif tree.data == 'func_call_expr':
                return self._eval_func_call_expr(tree)
        
        return None
    
    def _eval_func_call_expr(self, tree):
        """Evalúa el tipo de retorno de una llamada a función."""
        func_name = tree.children[0].value
        args_tree = tree.children[2] if len(tree.children) > 2 else None
        
        if not self.sdt.func_dir.function_exists(func_name):
            self.sdt.add_error(f"Función '{func_name}' no declarada")
            return None
        
        func_info = self.sdt.func_dir.get_function(func_name)
        
        # Verificar argumentos
        arg_types = []
        if args_tree and hasattr(args_tree, 'data') and args_tree.data == 'exp_plus':
            for child in args_tree.children:
                if hasattr(child, 'data') and child.data in ['expresion', 'expr_cmp_opt']:
                    tipo = self._eval_expresion(child)
                    arg_types.append(tipo)
        
        expected_params = func_info.params
        
        if len(arg_types) != len(expected_params):
            self.sdt.add_error(
                f"Función '{func_name}' espera {len(expected_params)} argumentos, "
                f"pero recibió {len(arg_types)}"
            )
            return None
        
        for i, (arg_type, (param_name, param_type)) in enumerate(zip(arg_types, expected_params)):
            if arg_type and not can_assign(param_type, arg_type):
                self.sdt.add_error(
                    f"Argumento {i+1} de '{func_name}': se esperaba {param_type}, se obtuvo {arg_type}"
                )
        
        if func_info.return_type == 'void':
            self.sdt.add_error(f"Función void '{func_name}' no puede usarse como expresión")
            return None
        
        return func_info.return_type
    
    def _eval_exp_plus(self, tree):
        if tree is None:
            return []
        
        if not hasattr(tree, 'data') or tree.data != 'exp_plus':
            return []
        
        if not hasattr(tree, 'children') or len(tree.children) == 0:
            return []
        
        types = []
        for child in tree.children:
            if hasattr(child, 'data') and child.data in ['expresion', 'expr_cmp_opt']:
                tipo = self._eval_expresion(child)
                types.append(tipo)
        
        return types
    
    def _process_vars_list(self, tree):
        if tree is None or not hasattr(tree, 'children'):
            return
        
        for child in tree.children:
            if hasattr(child, 'data') and child.data == 'vars':
                self._process_vars(child)
    
    def _process_vars(self, tree):
        id_plus_tree = tree.children[1]
        type_tree = tree.children[3]
        
        ids = self._extract_ids(id_plus_tree)
        tipo = self._extract_type(type_tree)
        
        for var_name in ids:
            try:
                # Asignar dirección virtual local
                address = self.sdt.memory_map.assign_local(tipo)
                self.sdt.var_table.add_local_variable(var_name, tipo, address=address)
            except Exception as e:
                self.sdt.add_error(str(e))
        
        vars_plus_tree = tree.children[5]
        self._process_vars_plus(vars_plus_tree)
    
    def _process_vars_plus(self, tree):
        if tree is None or not hasattr(tree, 'children'):
            return
        
        i = 0
        children = tree.children
        while i + 3 < len(children):
            id_plus_tree = children[i]
            type_tree = children[i + 2]
            
            ids = self._extract_ids(id_plus_tree)
            tipo = self._extract_type(type_tree)
            
            for var_name in ids:
                try:
                    self.sdt.var_table.add_local_variable(var_name, tipo)
                except Exception as e:
                    self.sdt.add_error(str(e))
            
            i += 4
    
    def _extract_ids(self, tree):
        ids = []
        for child in tree.children:
            if isinstance(child, Token) and child.type == 'ID':
                ids.append(child.value)
        return ids
    
    def _extract_type(self, tree):
        type_token = tree.children[0]
        return type_token.type.lower().replace("kw_", "")
    
    def _extract_params(self, tree):
        params = []
        for child in tree.children:
            if hasattr(child, 'data') and child.data == 'param':
                param_name = child.children[0].value
                param_type = self._extract_type(child.children[2])
                params.append((param_name, param_type))
        return params


class _ExpressionQuadBuilder:
    def __init__(self, sdt):
        self.sdt = sdt
        self.operator_stack = sdt.operator_stack
        self.operand_stack = sdt.operand_stack
        self.type_stack = sdt.type_stack
        self.start_ops = 0
        self.start_operands = 0
        self.start_types = 0

    def build(self, tree):
        self.start_ops = len(self.operator_stack)
        self.start_operands = len(self.operand_stack)
        self.start_types = len(self.type_stack)
        self._build_expression(tree)
        self._reduce({'PLUS', 'MINUS', 'MUL', 'DIV', 'GT', 'LT', 'NEQ'})
        if len(self.operand_stack) == self.start_operands:
            return None, None
        result_addr = self.operand_stack.pop()
        result_type = self.type_stack.pop()
        while len(self.operator_stack) > self.start_ops:
            self.operator_stack.pop()
        while len(self.operand_stack) > self.start_operands:
            self.operand_stack.pop()
        while len(self.type_stack) > self.start_types:
            self.type_stack.pop()
        return result_addr, result_type

    def _build_expression(self, tree):
        if tree is None:
            return
        if hasattr(tree, 'data') and tree.data == 'expr_cmp_opt':
            self._build_exp(tree.children[0])
            if len(tree.children) > 1:
                op_type = self._get_token_type(tree.children[1])
                self._push_operator(op_type)
                self._build_exp(tree.children[2])
                self._reduce({'GT', 'LT', 'NEQ'})
            return
        self._build_exp(tree)

    def _build_exp(self, tree):
        if tree is None:
            return
        if hasattr(tree, 'data') and tree.data == 'expr_addsub':
            self._build_term(tree.children[0])
            i = 1
            while i + 1 < len(tree.children):
                op_type = self._get_token_type(tree.children[i])
                self._push_operator(op_type) #PN17 :push operador a la pila de operadores
                self._build_term(tree.children[i + 1])
                self._reduce({'PLUS', 'MINUS'}) #PN18 :reducir la pila de operadores
                i += 2
            return
        self._build_term(tree)

    def _build_term(self, tree):
        if tree is None:
            return
        if hasattr(tree, 'data') and tree.data == 'expr_muldiv':
            self._build_factor(tree.children[0])
            i = 1
            while i + 1 < len(tree.children):
                op_type = self._get_token_type(tree.children[i])
                self._push_operator(op_type)
                self._build_factor(tree.children[i + 1])
                self._reduce({'MUL', 'DIV'})
                i += 2
            return
        self._build_factor(tree)

    def _build_factor(self, tree):
        if tree is None:
            return
        if hasattr(tree, 'data'):
            if tree.data == 'factor':
                if len(tree.children) == 3:
                    self._build_expression(tree.children[1])
                    return
                self._build_factor(tree.children[0])
                return
            if tree.data == 'signed':
                self._build_signed(tree)
                return
        self._build_valor(tree)

    def _build_signed(self, tree):
        if tree is None or len(tree.children) < 2:
            return
        op_type = self._get_token_type(tree.children[0])
        self._build_valor(tree.children[1])
        self._generate_unary(op_type)

    def _build_valor(self, tree):
        if tree is None:
            return
        if isinstance(tree, Token):
            self._push_token(tree)
            return
        if hasattr(tree, 'data') and tree.children:
            if tree.data in ('valor', 'cte'):
                self._build_valor(tree.children[0])
                return
            if tree.data in ('expresion', 'expr_cmp_opt'):
                self._build_expression(tree)
                return
            if tree.data == 'func_call_expr':
                self._build_func_call_expr(tree)
                return
    
    def _build_func_call_expr(self, tree):
        """
        Construye cuádruplos para llamada a función como expresión.
        Genera ERA, PARAM, GOSUB y pone el resultado en la pila.
        """
        func_name = tree.children[0].value
        args_tree = tree.children[2] if len(tree.children) > 2 else None
        
        if not self.sdt.func_dir.function_exists(func_name):
            self.sdt.add_error(f"Función '{func_name}' no declarada")
            self._push_operand(None, None)
            return
        
        func_info = self.sdt.func_dir.get_function(func_name)
        expected_params = func_info.params
        
        # Obtener direcciones de argumentos
        arg_addrs = []
        if args_tree and hasattr(args_tree, 'data') and args_tree.data == 'exp_plus':
            for child in args_tree.children:
                if hasattr(child, 'data') and child.data in ['expresion', 'expr_cmp_opt']:
                    # Construir cuádruplos para cada argumento
                    builder = _ExpressionQuadBuilder(self.sdt)
                    addr, tipo = builder.build(child)
                    arg_addrs.append(addr)
        
        # Verificar número de argumentos
        if len(arg_addrs) != len(expected_params):
            self.sdt.add_error(
                f"Función '{func_name}' espera {len(expected_params)} argumentos, "
                f"pero recibió {len(arg_addrs)}"
            )
            self._push_operand(None, None)
            return
        
        # Generar cuádruplo ERA
        self.sdt.gen_quad('ERA', func_name, None, None)
        
        # Generar cuádruplos PARAM
        for i, arg_addr in enumerate(arg_addrs):
            if arg_addr is not None:
                self.sdt.gen_quad('PARAM', arg_addr, None, i)
        
        # Generar cuádruplo GOSUB
        self.sdt.gen_quad('GOSUB', func_name, None, func_info.quad_start)
        
        # Si la función retorna valor, crear temporal con el resultado
        if func_info.return_type != 'void' and func_info.return_address is not None:
            temp_addr = self.sdt.new_temp(func_info.return_type)
            self.sdt.gen_quad('=', func_info.return_address, None, temp_addr)
            self._push_operand(temp_addr, func_info.return_type)
        else:
            # Función void usada como expresión - error
            if func_info.return_type == 'void':
                self.sdt.add_error(f"Función void '{func_name}' no puede usarse como expresión")
            self._push_operand(None, None)

    def _push_token(self, token):
        if token.type == 'ID':
            var_type = self.sdt.var_table.get_variable_type(token.value)
            var_address = self.sdt.var_table.get_variable_address(token.value)
            if var_address is None:
                self.sdt.add_error(f"Variable '{token.value}' no tiene dirección asignada")
                self._push_operand(None, None)
            else:
                self._push_operand(var_address, var_type) #PN19 :push direccion virtual a la pila de operandos
        elif token.type == 'CTE_INT':
            # Agregar constante a tabla y usar su dirección
            const_addr = self.sdt.constant_table.add_int_constant(token.value)
            self._push_operand(const_addr, 'int') #PN19 :push direccion virtual a la pila de operandos
        elif token.type == 'CTE_FLOAT':
            # Agregar constante a tabla y usar su dirección
            const_addr = self.sdt.constant_table.add_float_constant(token.value)
            self._push_operand(const_addr, 'float') #PN19 :push direccion virtual a la pila de operandos

    def _push_operand(self, address, tipo):
        """
        Push de operando a la pila.
        
        Args:
            address: Dirección virtual (int) o None
            tipo: Tipo del operando ('int', 'float', etc.)
        """
        self.operand_stack.append(address)
        self.type_stack.append(tipo)

    def _pop_operand(self):
        """
        Pop de operando de la pila.
        
        Returns:
            tuple: (dirección_virtual, tipo) o (None, None) si está vacía
        """
        if not self.operand_stack:
            return (None, None)
        address = self.operand_stack.pop()
        tipo = self.type_stack.pop()
        return address, tipo

    def _push_operator(self, op_type): #PN17 :push operador a la pila de operadores
        if op_type:
            self.operator_stack.append(op_type)

    def _reduce(self, allowed_ops): #PN18 :reducir la pila de operadores
        while len(self.operator_stack) > self.start_ops and self.operator_stack[-1] in allowed_ops:
            if len(self.operand_stack) - self.start_operands < 2:
                break
            op = self.operator_stack.pop()
            right = self._pop_operand()
            left = self._pop_operand()
            self._apply_operator(op, left, right)

    def _apply_operator(self, op, left, right):
        left_addr, left_type = left
        right_addr, right_type = right
        if left_addr is None or right_addr is None:
            return
        if left_type is None or right_type is None:
            self._push_operand(None, None)
            return
        result_type = check_binary_op(left_type, right_type, op) #PN20 :verificar tipo de resultado de la operacion binaria en cubo semantico
        if result_type is None:
            self.sdt.add_error(f"Operación inválida: {left_type} {op} {right_type}")
            self._push_operand(None, None)
            return
        # Generar temporal con dirección virtual 
        temp_addr = self.sdt.new_temp(result_type) #PN21 :generar temporal con direccion virtual
        self.sdt.gen_quad(op, left_addr, right_addr, temp_addr)
        self._push_operand(temp_addr, result_type)

    def _generate_unary(self, op_type):
        operand_addr, tipo = self._pop_operand()
        if operand_addr is None:
            return
        if tipo is None:
            self._push_operand(operand_addr, None)
            return
        result_type = check_unary_op(tipo, op_type)
        if result_type is None:
            self.sdt.add_error(f"Operación unaria inválida: {op_type}")
            self._push_operand(operand_addr, None)
            return
        # Generar temporal con dirección virtual
        temp_addr = self.sdt.new_temp(result_type)
        self.sdt.gen_quad(op_type, operand_addr, None, temp_addr)
        self._push_operand(temp_addr, result_type)

    def _get_token_type(self, node):
        if node is None:
            return None
        if isinstance(node, Token):
            return node.type
        if hasattr(node, 'children') and node.children:
            return self._get_token_type(node.children[0])
        return None
