"""
Tabla de Constantes para el Compilador Patito

Almacena constantes únicas y les asigna direcciones virtuales.
Evita duplicación de constantes en memoria.
"""

class ConstantTable:
    
    def __init__(self, memory_map):
        self.memory_map = memory_map
        # {valor: dirección_virtual}
        self.constants = {}
        # {dirección_virtual: valor} para lookup inverso
        self.addr_to_value = {}
    
    def add_int_constant(self, value):
        #normalizar a int
        if isinstance(value, str):
            try:
                int_value = int(value)
            except ValueError:
                raise Exception(f"Valor no es un entero válido: {value}")
        else:
            int_value = int(value)
        
        #ya existe, retornar su dirección
        if int_value in self.constants:
            return self.constants[int_value]
        
        #asignar nueva dirección desde espacio de constantes
        addr = self.memory_map.assign_constant_int()
        
        self.constants[int_value] = addr
        self.addr_to_value[addr] = int_value
        return addr
    
    def add_float_constant(self, value):
        #normalizar a float
        if isinstance(value, str):
            try:
                float_value = float(value)
            except ValueError:
                raise Exception(f"Valor no es un flotante válido: {value}")
        else:
            float_value = float(value)
        
        #ya existe, retornar su dirección
        if float_value in self.constants:
            return self.constants[float_value]
        
        #asignar nueva dirección desde espacio de constantes
        addr = self.memory_map.assign_constant_float()
        
        self.constants[float_value] = addr
        self.addr_to_value[addr] = float_value
        return addr
    
    
    def get_constant_value(self, addr):
        return self.addr_to_value.get(addr)
    
    def get_constant_address(self, value):
        return self.constants.get(value)
    
    def get_all_constants(self):
        return dict(self.constants)

