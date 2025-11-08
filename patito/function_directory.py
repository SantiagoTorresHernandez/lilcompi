class FunctionInfo:
    def __init__(self, name, return_type='void'):
        self.name = name
        self.return_type = return_type
        self.params = []
        self.local_vars = {}
    
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


class FunctionDirectory:
    def __init__(self):
        self.functions = {}
    
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

