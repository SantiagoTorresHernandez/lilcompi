class VariableInfo:
    def __init__(self, name, var_type, scope, kind='var', address=None):
        self.name = name
        self.type = var_type
        self.scope = scope
        self.kind = kind
        self.address = address  # Dirección virtual asignada
    
    def __repr__(self):
        addr_str = f"@{self.address}" if self.address is not None else ""
        return f"{self.name}: {self.type} {addr_str}"


class VariableTable:
    def __init__(self):
        self.scope_stack = [{}]
        self.scope_names = ['global']
        self.global_vars = self.scope_stack[0]
    
    def enter_scope(self, scope_name):
        self.scope_stack.append({})
        self.scope_names.append(scope_name)
    
    def exit_scope(self):
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
            self.scope_names.pop()
    
    def current_scope_name(self):
        return self.scope_names[-1]
    
    def is_global_scope(self):
        return len(self.scope_stack) == 1
    
    def add_variable(self, name, var_type, kind='var', address=None):
        current_scope = self.scope_stack[-1]
        scope_name = self.current_scope_name()
        
        if name in current_scope:
            raise Exception(f"Error: Variable '{name}' ya está declarada en {scope_name}")
        
        var_info = VariableInfo(name, var_type, scope_name, kind, address)
        current_scope[name] = var_info
    
    def add_global_variable(self, name, var_type, address=None):
        self.add_variable(name, var_type, kind='var', address=address)
    
    def add_local_variable(self, name, var_type, address=None):
        self.add_variable(name, var_type, kind='var', address=address)
    
    def add_parameter(self, name, var_type, address=None):
        self.add_variable(name, var_type, kind='param', address=address)
    
    def get_variable_address(self, name):
        """Obtiene la dirección virtual de una variable"""
        var_info = self.lookup_variable(name)
        return var_info.address if var_info else None
    
    def set_variable_address(self, name, address):
        """Asigna una dirección virtual a una variable"""
        var_info = self.lookup_variable(name)
        if var_info:
            var_info.address = address
        else:
            raise Exception(f"Variable '{name}' no encontrada")
    
    def lookup_variable(self, name):
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        return None
    
    def variable_exists(self, name):
        return self.lookup_variable(name) is not None
    
    def get_variable_type(self, name):
        var_info = self.lookup_variable(name)
        return var_info.type if var_info else None
    
    def get_variable_scope(self, name):
        var_info = self.lookup_variable(name)
        return var_info.scope if var_info else None
    
    def is_global_variable(self, name):
        return name in self.global_vars
    
    def get_current_scope_vars(self):
        return dict(self.scope_stack[-1])

