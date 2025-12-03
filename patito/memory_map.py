"""
Sistema de Direcciones Virtuales para el Compilador Patito

Asigna direcciones de memoria virtuales a variables, temporales y constantes
según su tipo y scope (global, local, temporal, constante).
"""


class MemoryMap:
    
    def __init__(self):
        #bases de direcciones
        self.global_int_base = 1000
        self.global_float_base = 2000
        self.local_int_base = 3000
        self.local_float_base = 4000
        self.temp_int_base = 5000
        self.temp_float_base = 6000
        self.cte_int_base = 7000
        self.cte_float_base = 8000
        
        self.global_int_counter = 0
        self.global_float_counter = 0
        self.local_int_counter = 0
        self.local_float_counter = 0
        self.temp_int_counter = 0
        self.temp_float_counter = 0
        self.cte_int_counter = 0
        self.cte_float_counter = 0
        
        # Stack para manejar múltiples funciones (scopes locales)
        self.local_counters_stack = []
    
    def assign_global_int(self): #asignar direccion virtual para variable global int
        if self.global_int_counter >= 1000:
            raise Exception("Memoria global int agotada")
        addr = self.global_int_base + self.global_int_counter
        self.global_int_counter += 1
        return addr
    
    def assign_global_float(self): #asignar direccion virtual para variable global float
        if self.global_float_counter >= 1000:
            raise Exception("Memoria global float agotada")
        addr = self.global_float_base + self.global_float_counter
        self.global_float_counter += 1
        return addr
    
    def assign_local_int(self): #asignar direccion virtual para variable local int
        if self.local_int_counter >= 1000:
            raise Exception("Memoria local int agotada")
        addr = self.local_int_base + self.local_int_counter
        self.local_int_counter += 1
        return addr
    
    def assign_local_float(self): #asignar direccion virtual para variable local float
        if self.local_float_counter >= 1000:
            raise Exception("Memoria local float agotada")
        addr = self.local_float_base + self.local_float_counter
        self.local_float_counter += 1
        return addr
    
    def assign_temp_int(self): #asignar direccion virtual para temporal int
        if self.temp_int_counter >= 1000:
            raise Exception("Memoria temporal int agotada")
        addr = self.temp_int_base + self.temp_int_counter
        self.temp_int_counter += 1
        return addr
    
    def assign_temp_float(self): #asignar direccion virtual para temporal float
        if self.temp_float_counter >= 1000:
            raise Exception("Memoria temporal float agotada")
        addr = self.temp_float_base + self.temp_float_counter
        self.temp_float_counter += 1
        return addr
    
    def assign_constant_int(self): #asignar direccion virtual para constante int
        if self.cte_int_counter >= 1000:
            raise Exception("Memoria constante int agotada")
        addr = self.cte_int_base + self.cte_int_counter
        self.cte_int_counter += 1
        return addr
    
    def assign_constant_float(self): #asignar direccion virtual para constante float    
        if self.cte_float_counter >= 1000:
            raise Exception("Memoria constante float agotada")
        addr = self.cte_float_base + self.cte_float_counter
        self.cte_float_counter += 1
        return addr
    
    def assign_global(self, var_type): #asignar direccion virtual para variable global según tipo
        if var_type == 'int':
            return self.assign_global_int()
        elif var_type == 'float':
            return self.assign_global_float()
        else:
            raise Exception(f"Tipo no soportado para variable global: {var_type}")
    
    def assign_local(self, var_type): #asignar direccion virtual para variable local según tipo
        if var_type == 'int':
            return self.assign_local_int()
        elif var_type == 'float':
            return self.assign_local_float()
        else:
            raise Exception(f"Tipo no soportado para variable local: {var_type}")
    
    def assign_temp(self, var_type): #asignar direccion virtual para temporal según tipo
        if var_type == 'int':
            return self.assign_temp_int()
        elif var_type == 'float':
            return self.assign_temp_float()
        else:
            raise Exception(f"Tipo no soportado para temporal: {var_type}")
    
    def enter_function(self): #entrar a una función (guardar estado de contadores locales y temporales)
        state = {
            'local_int_counter': self.local_int_counter,
            'local_float_counter': self.local_float_counter,
            'temp_int_counter': self.temp_int_counter,
            'temp_float_counter': self.temp_float_counter
        }
        self.local_counters_stack.append(state)
        # Resetear contadores locales y temporales para la nueva función
        self.local_int_counter = 0
        self.local_float_counter = 0
        self.temp_int_counter = 0
        self.temp_float_counter = 0
    
    def exit_function(self): #salir de una función (restaurar estado de contadores locales y temporales)
        if self.local_counters_stack:
            state = self.local_counters_stack.pop()
            self.local_int_counter = state['local_int_counter']
            self.local_float_counter = state['local_float_counter']
            self.temp_int_counter = state['temp_int_counter']
            self.temp_float_counter = state['temp_float_counter']
    
    def get_function_resources(self): #obtener recursos usados por la función actual
        return {
            'local_int': self.local_int_counter,
            'local_float': self.local_float_counter,
            'temp_int': self.temp_int_counter,
            'temp_float': self.temp_float_counter
        }
    
    def get_memory_summary(self): #obtener resumen del uso de memoria
        return {
            'global_int': (self.global_int_base, self.global_int_base + self.global_int_counter - 1) if self.global_int_counter > 0 else None,
            'global_float': (self.global_float_base, self.global_float_base + self.global_float_counter - 1) if self.global_float_counter > 0 else None,
            'local_int': (self.local_int_base, self.local_int_base + self.local_int_counter - 1) if self.local_int_counter > 0 else None,
            'local_float': (self.local_float_base, self.local_float_base + self.local_float_counter - 1) if self.local_float_counter > 0 else None,
            'temp_int': (self.temp_int_base, self.temp_int_base + self.temp_int_counter - 1) if self.temp_int_counter > 0 else None,
            'temp_float': (self.temp_float_base, self.temp_float_base + self.temp_float_counter - 1) if self.temp_float_counter > 0 else None,
        }
    
    def get_segment_bases(self): #obtener bases de cada segmento de memoria para la VM
        return {
            'global_int': self.global_int_base,
            'global_float': self.global_float_base,
            'local_int': self.local_int_base,
            'local_float': self.local_float_base,
            'temp_int': self.temp_int_base,
            'temp_float': self.temp_float_base,
            'cte_int': self.cte_int_base,
            'cte_float': self.cte_float_base
        }
    
    @staticmethod
    def get_segment(address): #determinar a qué segmento pertenece una dirección
        if 1000 <= address < 3000:
            return 'global'
        elif 3000 <= address < 5000:
            return 'local'
        elif 5000 <= address < 7000:
            return 'temp'
        elif 7000 <= address < 9000:
            return 'constant'
        else:
            raise ValueError(f"Dirección {address} fuera de rango válido")
    
    @staticmethod
    def get_type_from_address(address): #determinar el tipo de dato según la dirección  
        #direcciones pares son int, impares son float en cada segmento
        if address < 1000 or address >= 9000:
            raise ValueError(f"Dirección {address} fuera de rango válido")
        
        #global int: 1000-1999, global float: 2000-2999
        #local int: 3000-3999, local float: 4000-4999
        #temp int: 5000-5999, temp float: 6000-6999
        #cte int: 7000-7999, cte float: 8000-8999
        segment_offset = address % 2000
        if segment_offset < 1000:
            return 'int'
        else:
            return 'float'

