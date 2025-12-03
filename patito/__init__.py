"""Patito - A compiler for the Patito language using Syntax Directed Translation."""

from .patito_parser import parse_and_validate, parse_text
from .patito_sdt import PatitoSDT
from .function_directory import FunctionDirectory, FunctionInfo
from .variable_table import VariableTable, VariableInfo
from .semantic_cube import check_binary_op, check_unary_op, can_assign
from .memory_map import MemoryMap
from .constant_table import ConstantTable
from .obj_generator import ObjGenerator, compile_to_obj
from .virtual_machine import VirtualMachine, run_program, run_from_source

__all__ = [
    # Parser y SDT
    "parse_and_validate",
    "parse_text",  # deprecated, usar parse_and_validate
    "PatitoSDT",
    # Tablas y directorios
    "FunctionDirectory",
    "FunctionInfo",
    "VariableTable",
    "VariableInfo",
    # Semántica
    "check_binary_op",
    "check_unary_op",
    "can_assign",
    # Memoria
    "MemoryMap",
    "ConstantTable",
    # Generación de .obj
    "ObjGenerator",
    "compile_to_obj",
    # Máquina Virtual
    "VirtualMachine",
    "run_program",
    "run_from_source",
]
