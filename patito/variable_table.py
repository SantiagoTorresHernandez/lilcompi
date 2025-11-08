class VariableInfo:
    def __init__(self, name, var_type, scope, kind='var'):
        self.name = name
        self.type = var_type
        self.scope = scope
        self.kind = kind
    
    def __repr__(self):
        return f"{self.name}: {self.type} ({self.kind})"


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
    
    def add_variable(self, name, var_type, kind='var'):
        current_scope = self.scope_stack[-1]
        scope_name = self.current_scope_name()
        
        if name in current_scope:
            raise Exception(f"Error: Variable '{name}' ya está declarada en {scope_name}")
        
        var_info = VariableInfo(name, var_type, scope_name, kind)
        current_scope[name] = var_info
    
    def add_global_variable(self, name, var_type):
        self.add_variable(name, var_type, kind='var')
    
    def add_local_variable(self, name, var_type):
        self.add_variable(name, var_type, kind='var')
    
    def add_parameter(self, name, var_type):
        self.add_variable(name, var_type, kind='param')
    
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
    
    def get_all_global_vars(self):
        return dict(self.global_vars)
    
    def get_current_scope_vars(self):
        return dict(self.scope_stack[-1])
    
    def count_global_vars(self):
        return len(self.global_vars)
    
    def count_local_vars(self):
        if self.is_global_scope():
            return 0
        return len(self.scope_stack[-1])
    
    def __repr__(self):
        result = ["=== TABLA DE VARIABLES ===\n"]
        
        for i, scope in enumerate(self.scope_stack):
            scope_name = self.scope_names[i]
            
            if i == 0:
                result.append(f"SCOPE GLOBAL:")
            else:
                result.append(f"\nSCOPE LOCAL: {scope_name}")
            
            if not scope:
                result.append("  (vacio)")
            else:
                params = [(n, v) for n, v in scope.items() if v.kind == 'param']
                vars_list = [(n, v) for n, v in scope.items() if v.kind == 'var']
                
                if params:
                    result.append("  Parámetros:")
                    for name, var_info in params:
                        result.append(f"    - {name}: {var_info.type}")
                
                if vars_list:
                    result.append("  Variables:")
                    for name, var_info in vars_list:
                        result.append(f"    - {name}: {var_info.type}")
        
        result.append(f"\nTotal variables globales: {self.count_global_vars()}")
        
        return "\n".join(result)

