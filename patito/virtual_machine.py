"""
Máquina Virtual para el Compilador Patito

Ejecuta programas compilados (.obj) utilizando:
- Memoria de ejecución con diccionarios (dirección -> valor)
- Stack de activación para funciones y recursión
- Soporte completo para expresiones, control de flujo y funciones
"""

from typing import Dict, Any, List, Optional, Tuple


class ActivationRecord:
    """
    Registro de activación para llamadas a funciones.
    
    Almacena el contexto de una función:
    - Memoria local (parámetros y variables locales)
    - Memoria temporal
    - Dirección de retorno (IP a donde volver)
    """
    
    def __init__(self, return_address: int):
        self.local_memory: Dict[int, Any] = {}  # Memoria local de la función
        self.temp_memory: Dict[int, Any] = {}   # Temporales de la función
        self.return_address = return_address     # IP para retornar
    
    def __repr__(self):
        return f"AR(ret={self.return_address}, locals={len(self.local_memory)}, temps={len(self.temp_memory)})"


class ExecutionMemory:
    """
    Gestiona la memoria de ejecución de la máquina virtual.
    
    Utiliza diccionarios (dirección -> valor) para cada segmento:
    - global_memory: Variables globales (1000-2999)
    - local_stack: Stack de memorias locales para recursión
    - temp_memory: Temporales del contexto actual
    - constant_memory: Constantes (solo lectura)
    
    Rangos de direcciones:
    - Global int:    1000-1999
    - Global float:  2000-2999
    - Local int:     3000-3999
    - Local float:   4000-4999
    - Temp int:      5000-5999
    - Temp float:    6000-6999
    - Const int:     7000-7999
    - Const float:   8000-8999
    """
    
    def __init__(self):
        self.global_memory: Dict[int, Any] = {}
        self.constant_memory: Dict[int, Any] = {}
        
        # Stack de registros de activación
        self.call_stack: List[ActivationRecord] = []
        
        # Memoria local y temporal del contexto actual (main inicialmente)
        self.current_local: Dict[int, Any] = {}
        self.current_temp: Dict[int, Any] = {}
    
    def load_constants(self, constants: Dict[int, Any]):
        """Carga las constantes desde el archivo .obj"""
        self.constant_memory = dict(constants)
    
    def get_segment(self, address: int) -> str:
        """Determina el segmento de una dirección."""
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
    
    def get_value(self, address: int) -> Any:
        """
        Obtiene el valor de una dirección de memoria.
        
        Args:
            address: Dirección virtual
        
        Returns:
            Valor almacenado en esa dirección
        """
        segment = self.get_segment(address)
        
        if segment == 'global':
            return self.global_memory.get(address, 0)
        elif segment == 'local':
            return self.current_local.get(address, 0)
        elif segment == 'temp':
            return self.current_temp.get(address, 0)
        elif segment == 'constant':
            if address not in self.constant_memory:
                raise ValueError(f"Constante {address} no encontrada")
            return self.constant_memory[address]
        
        raise ValueError(f"Segmento desconocido para dirección {address}")
    
    def set_value(self, address: int, value: Any):
        """
        Almacena un valor en una dirección de memoria.
        
        Args:
            address: Dirección virtual
            value: Valor a almacenar
        """
        segment = self.get_segment(address)
        
        if segment == 'global':
            self.global_memory[address] = value
        elif segment == 'local':
            self.current_local[address] = value
        elif segment == 'temp':
            self.current_temp[address] = value
        elif segment == 'constant':
            raise ValueError(f"No se puede escribir en memoria de constantes: {address}")
        else:
            raise ValueError(f"Segmento desconocido para dirección {address}")
    
    def push_activation_record(self, return_address: int):
        """
        Crea un nuevo registro de activación al llamar a una función.
        Guarda el contexto actual y crea uno nuevo.
        """
        # Guardar contexto actual
        ar = ActivationRecord(return_address)
        ar.local_memory = self.current_local
        ar.temp_memory = self.current_temp
        self.call_stack.append(ar)
        
        # Crear nuevo contexto vacío
        self.current_local = {}
        self.current_temp = {}
    
    def pop_activation_record(self) -> int:
        """
        Restaura el contexto anterior al retornar de una función.
        
        Returns:
            int: Dirección de retorno (siguiente IP)
        """
        if not self.call_stack:
            raise RuntimeError("Stack de llamadas vacío")
        
        ar = self.call_stack.pop()
        self.current_local = ar.local_memory
        self.current_temp = ar.temp_memory
        return ar.return_address


class VirtualMachine:
    """
    Máquina Virtual para ejecutar programas Patito compilados.
    
    Soporta:
    - Operaciones aritméticas: +, -, *, /
    - Operaciones relacionales: <, >, !=
    - Asignación
    - Control de flujo: GOTO, GOTOF
    - Funciones: ERA, PARAM, GOSUB, RETURN, ENDFUNC
    - I/O: PRINT
    """
    
    def __init__(self, obj_data: dict):
        """
        Inicializa la VM con datos de un archivo .obj.
        
        Args:
            obj_data: Diccionario con quadruples, constants, functions
        """
        self.quadruples = obj_data['quadruples']
        self.functions = obj_data.get('functions', {})
        self.program_name = obj_data.get('program_name', 'Unknown')
        
        # Inicializar memoria
        self.memory = ExecutionMemory()
        self.memory.load_constants(obj_data.get('constants', {}))
        
        # Instruction Pointer
        self.ip = 0
        
        # Stack de parámetros pendientes para llamada actual
        self.param_stack: List[Any] = []
        
        # Función que se está llamando actualmente (para ERA)
        self.current_call: Optional[str] = None
        
        # Flag para terminar ejecución
        self.running = True
        
        # Output buffer para testing
        self.output_buffer: List[str] = []
    
    def execute(self) -> List[str]:
        """
        Ejecuta el programa completo.
        
        Returns:
            List[str]: Salida del programa (prints)
        """
        self.ip = 0
        self.running = True
        self.output_buffer = []
        
        while self.running and self.ip < len(self.quadruples):
            quad = self.quadruples[self.ip]
            op, arg1, arg2, result = quad
            
            # Despachar operación
            self.ip = self._dispatch(op, arg1, arg2, result)
        
        return self.output_buffer
    
    def _dispatch(self, op: str, arg1: Any, arg2: Any, result: Any) -> int:
        """
        Despacha una operación y retorna el siguiente IP.
        """
        next_ip = self.ip + 1
        
        # Operaciones aritméticas
        if op == 'PLUS':
            val1 = self.memory.get_value(arg1)
            val2 = self.memory.get_value(arg2)
            self.memory.set_value(result, val1 + val2)
        
        elif op == 'MINUS':
            val1 = self.memory.get_value(arg1)
            val2 = self.memory.get_value(arg2)
            self.memory.set_value(result, val1 - val2)
        
        elif op == 'MUL':
            val1 = self.memory.get_value(arg1)
            val2 = self.memory.get_value(arg2)
            self.memory.set_value(result, val1 * val2)
        
        elif op == 'DIV':
            val1 = self.memory.get_value(arg1)
            val2 = self.memory.get_value(arg2)
            if val2 == 0:
                raise RuntimeError("División por cero")
            # Mantener tipo: si ambos son int, resultado es int
            if isinstance(val1, int) and isinstance(val2, int):
                self.memory.set_value(result, val1 // val2)
            else:
                self.memory.set_value(result, val1 / val2)
        
        # Operaciones relacionales
        elif op == 'GT':
            val1 = self.memory.get_value(arg1)
            val2 = self.memory.get_value(arg2)
            self.memory.set_value(result, 1 if val1 > val2 else 0)
        
        elif op == 'LT':
            val1 = self.memory.get_value(arg1)
            val2 = self.memory.get_value(arg2)
            self.memory.set_value(result, 1 if val1 < val2 else 0)
        
        elif op == 'NEQ':
            val1 = self.memory.get_value(arg1)
            val2 = self.memory.get_value(arg2)
            self.memory.set_value(result, 1 if val1 != val2 else 0)
        
        # Asignación
        elif op == '=':
            val = self.memory.get_value(arg1)
            self.memory.set_value(result, val)
        
        # Control de flujo
        elif op == 'GOTO':
            next_ip = result
        
        elif op == 'GOTOF':
            val = self.memory.get_value(arg1)
            if val == 0 or val is False:
                next_ip = result
        
        # I/O
        elif op == 'PRINT':
            if isinstance(arg1, str):
                # Es un string literal
                output = arg1
            else:
                # Es una dirección de memoria
                output = str(self.memory.get_value(arg1))
            
            print(output, end='')
            self.output_buffer.append(output)
        
        # Funciones
        elif op == 'ERA':
            # Expansion of Activation Record
            # arg1 = nombre de la función
            self.current_call = arg1
            self.param_stack = []
        
        elif op == 'PARAM':
            # arg1 = dirección del argumento
            # result = número de parámetro
            val = self.memory.get_value(arg1)
            self.param_stack.append((result, val))
        
        elif op == 'GOSUB':
            # arg1 = nombre de la función
            # result = quad_start de la función
            func_name = arg1
            func_start = result
            
            # Guardar contexto y crear nuevo registro de activación
            self.memory.push_activation_record(self.ip + 1)
            
            # Asignar parámetros a memoria local
            if func_name in self.functions:
                func_info = self.functions[func_name]
                params = func_info.get('params', [])
                
                # Ordenar parámetros por índice
                self.param_stack.sort(key=lambda x: x[0])
                
                # Base de memoria local para parámetros
                local_int_base = 3000
                local_float_base = 4000
                int_offset = 0
                float_offset = 0
                
                for i, (param_idx, value) in enumerate(self.param_stack):
                    if i < len(params):
                        param_type = params[i].get('type', 'int')
                        if param_type == 'int':
                            addr = local_int_base + int_offset
                            int_offset += 1
                        else:
                            addr = local_float_base + float_offset
                            float_offset += 1
                        self.memory.set_value(addr, value)
            
            self.param_stack = []
            self.current_call = None
            
            # Saltar al inicio de la función
            next_ip = func_start
        
        elif op == 'RETURN':
            # arg1 = dirección del valor a retornar
            # result = dirección global donde guardar el retorno
            val = self.memory.get_value(arg1)
            
            # Restaurar contexto anterior
            return_addr = self.memory.pop_activation_record()
            
            # Guardar valor de retorno en variable global
            if result is not None:
                self.memory.set_value(result, val)
            
            next_ip = return_addr
        
        elif op == 'ENDFUNC':
            # Fin de función void (sin RETURN explícito)
            return_addr = self.memory.pop_activation_record()
            next_ip = return_addr
        
        elif op == 'END':
            # Fin del programa
            self.running = False
        
        else:
            raise RuntimeError(f"Operación desconocida: {op}")
        
        return next_ip
    
    def get_memory_snapshot(self) -> dict:
        """
        Obtiene un snapshot del estado actual de la memoria.
        Útil para debugging.
        """
        return {
            'global': dict(self.memory.global_memory),
            'local': dict(self.memory.current_local),
            'temp': dict(self.memory.current_temp),
            'constants': dict(self.memory.constant_memory),
            'call_stack_depth': len(self.memory.call_stack)
        }


def run_program(obj_path: str) -> List[str]:
    """
    Función de conveniencia para ejecutar un programa .obj.
    
    Args:
        obj_path: Ruta al archivo .obj
    
    Returns:
        List[str]: Salida del programa
    """
    from .obj_generator import ObjGenerator
    
    obj_data = ObjGenerator.load(obj_path)
    vm = VirtualMachine(obj_data)
    return vm.execute()


def run_from_source(source_code: str) -> Tuple[List[str], Optional[List[str]]]:
    """
    Compila y ejecuta código fuente Patito directamente.
    
    Args:
        source_code: Código fuente Patito
    
    Returns:
        Tuple[output, errors]: Salida del programa y errores (si hay)
    """
    from .patito_parser import parse_and_validate
    
    sdt = parse_and_validate(source_code)
    
    if sdt.has_errors():
        return [], sdt.errors
    
    obj_data = sdt.to_obj()
    vm = VirtualMachine(obj_data)
    output = vm.execute()
    
    return output, None

