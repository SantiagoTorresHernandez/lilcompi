"""
Generador de Archivo .obj para el Compilador Patito

Genera un archivo .obj que contiene:
- Cuádruplos del programa
- Tabla de constantes
- Directorio de funciones (sin tabla de variables)
"""

import json


class ObjGenerator:
    """
    Genera archivos .obj a partir del resultado de compilación.
    
    El archivo .obj es un JSON con la estructura:
    {
        "program_name": "nombre_programa",
        "quadruples": [[op, arg1, arg2, result], ...],
        "constants": {addr: value, ...},
        "functions": {
            "func_name": {
                "return_type": "void|int|float",
                "quad_start": int,
                "return_address": int|null,
                "params": [{"name": "x", "type": "int"}, ...],
                "resources": {"local_int": int, "local_float": int, ...}
            }
        }
    }
    """
    
    @staticmethod
    def generate(sdt, output_path):
        """
        Genera el archivo .obj a partir del SDT compilado.
        
        Args:
            sdt: Instancia de PatitoSDT después de compilar
            output_path: Ruta del archivo .obj a generar
        """
        obj_data = sdt.to_obj()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(obj_data, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    @staticmethod
    def load(input_path):
        """
        Carga un archivo .obj.
        
        Args:
            input_path: Ruta del archivo .obj a cargar
        
        Returns:
            dict: Datos del programa compilado
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            obj_data = json.load(f)
        
        # Convertir claves de constantes de string a int
        if 'constants' in obj_data:
            constants = {}
            for addr_str, value in obj_data['constants'].items():
                constants[int(addr_str)] = value
            obj_data['constants'] = constants
        
        # Convertir cuádruplos a tuplas
        if 'quadruples' in obj_data:
            obj_data['quadruples'] = [
                tuple(quad) for quad in obj_data['quadruples']
            ]
        
        return obj_data


def compile_to_obj(source_code, output_path):
    """
    Función de conveniencia para compilar código fuente a .obj.
    
    Args:
        source_code: Código fuente Patito
        output_path: Ruta del archivo .obj a generar
    
    Returns:
        tuple: (sdt, output_path) o (None, errors) si hay errores
    """
    from .patito_parser import parse_and_validate
    
    sdt = parse_and_validate(source_code)
    
    if sdt.has_errors():
        return None, sdt.errors
    
    ObjGenerator.generate(sdt, output_path)
    return sdt, output_path

