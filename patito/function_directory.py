class FunctionInfo:
    """
    Información de una función en el directorio de funciones.
    
    Atributos:
        name: Nombre de la función
        return_type: Tipo de retorno ('void', 'int', 'float')
        params: Lista de parámetros [(nombre, tipo), ...]
        local_vars: Variables locales {nombre: tipo}
        quad_start: Índice del primer cuádruplo de la función
        return_address: Dirección virtual de variable global para valor de retorno
        resources: Conteo de recursos usados por la función
    """
    def __init__(self, name, return_type='void'):
        self.name = name
        self.return_type = return_type
        self.params = []
        self.local_vars = {}
        # Nuevos campos para cuádruplos y VM
        self.quad_start = None  # Índice del primer cuádruplo
        self.return_address = None  # Dirección de variable global para retorno
        self.resources = {
            'local_int': 0,
            'local_float': 0,
            'temp_int': 0,
            'temp_float': 0,
            'params_int': 0,
            'params_float': 0
        }
    
    def add_param(self, param_name, param_type):
        for existing_name, _ in self.params:
            if existing_name == param_name:
                raise Exception(f"Error: Parámetro '{param_name}' duplicado en función '{self.name}'")
        
        self.params.append((param_name, param_type))
    
    def add_local_var(self, var_name, var_type):
        if var_name in self.local_vars:
            raise Exception(f"Error: Variable local '{var_name}' ya declarada en función '{self.name}'")
        
        for param_name, _ in self.params:
            if param_name == var_name:
                raise Exception(f"Error: Variable '{var_name}' ya existe como parámetro en función '{self.name}'")
        
        self.local_vars[var_name] = var_type
    
    def set_quad_start(self, quad_index):
        """Establece el índice del primer cuádruplo de la función."""
        self.quad_start = quad_index
    
    def set_return_address(self, address):
        """Establece la dirección de la variable global para valor de retorno."""
        self.return_address = address
    
    def set_resources(self, local_int=0, local_float=0, temp_int=0, temp_float=0):
        """Establece el conteo de recursos usados por la función."""
        self.resources = {
            'local_int': local_int,
            'local_float': local_float,
            'temp_int': temp_int,
            'temp_float': temp_float,
            'params_int': sum(1 for _, t in self.params if t == 'int'),
            'params_float': sum(1 for _, t in self.params if t == 'float')
        }
    
    def to_dict(self):
        """Exporta la información de la función para el archivo .obj."""
        return {
            'name': self.name,
            'return_type': self.return_type,
            'quad_start': self.quad_start,
            'return_address': self.return_address,
            'params': [{'name': name, 'type': ptype} for name, ptype in self.params],
            'resources': self.resources
        }


class FunctionDirectory:
    def __init__(self):
        self.functions = {}
        self.program_name = None
    
    def set_program(self, name):
        self.program_name = name
        if name not in self.functions:
            self.functions[name] = FunctionInfo(name, return_type='void')
        return self.functions[name]
    
    def add_function(self, name, return_type='void'):
        if name in self.functions:
            raise Exception(f"Error: Función '{name}' ya está declarada")
        
        func_info = FunctionInfo(name, return_type)
        self.functions[name] = func_info
        return func_info
    
    def function_exists(self, name):
        return name in self.functions
    
    def get_function(self, name):
        return self.functions.get(name, None)
    
    def get_function_params(self, name):
        func = self.get_function(name)
        return func.params if func else None
    
    def validate_call(self, func_name, arg_types):
        func = self.get_function(func_name)
        
        if func is None:
            return False, f"Función '{func_name}' no declarada"
        
        expected_params = func.params
        
        if len(arg_types) != len(expected_params):
            return False, f"Función '{func_name}' espera {len(expected_params)} argumentos, pero recibió {len(arg_types)}"
        
        return True, None
    
    def get_all_functions(self):
        return list(self.functions.keys())
    
    def to_dict(self):
        """
        Exporta el directorio de funciones para el archivo .obj.
        No incluye la tabla de variables (solo metadatos de funciones).
        """
        result = {}
        for name, func_info in self.functions.items():
            # No incluir el programa principal como función
            if name != self.program_name:
                result[name] = func_info.to_dict()
        return result

