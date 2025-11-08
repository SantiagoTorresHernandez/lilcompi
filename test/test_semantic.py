"""
Tests para el analizador semántico de Patito.
"""

import pytest
from pathlib import Path
from patito.patito_parser import parse_text
from patito.semantic_analyzer import SemanticAnalyzer


def analyze_program(source_code):
    """Helper para parsear y analizar un programa."""
    ast = parse_text(source_code)
    analyzer = SemanticAnalyzer()
    success = analyzer.analyze(ast)
    return success, analyzer.errors


def test_programa_correcto():
    """Prueba un programa semánticamente correcto."""
    src = """
    programa Test;
    var x, y: int;
    var z: float;
    
    main {
        x = 5;
        y = 10;
        z = 3.14;
        x = x + y;
    }
    end
    """
    success, errors = analyze_program(src)
    assert success, f"Debería pasar sin errores: {errors}"


def test_variable_no_declarada():
    """Detecta uso de variable no declarada."""
    src = """
    programa Test;
    var x: int;
    
    main {
        x = 5;
        y = 10;
    }
    end
    """
    success, errors = analyze_program(src)
    assert not success
    assert any("no declarada" in err for err in errors)


def test_asignacion_tipo_incompatible():
    """Detecta asignación de float a int."""
    src = """
    programa Test;
    var x: int;
    var y: float;
    
    main {
        y = 3.14;
        x = y;
    }
    end
    """
    success, errors = analyze_program(src)
    assert not success
    assert any("asignar" in err.lower() for err in errors)


def test_promocion_int_a_float():
    """Permite asignar int a float (promoción implícita)."""
    src = """
    programa Test;
    var x: int;
    var y: float;
    
    main {
        x = 5;
        y = x;
    }
    end
    """
    success, errors = analyze_program(src)
    assert success, f"Promoción int->float debería ser válida: {errors}"


def test_operaciones_aritmeticas():
    """Verifica operaciones aritméticas válidas."""
    src = """
    programa Test;
    var a, b, c: int;
    var x, y: float;
    
    main {
        a = 5;
        b = 10;
        c = a + b * 2 - 3;
        
        x = 3.14;
        y = x / 2.0;
    }
    end
    """
    success, errors = analyze_program(src)
    assert success, f"Operaciones aritméticas deberían ser válidas: {errors}"


def test_funcion_no_declarada():
    """Detecta llamada a función no declarada."""
    src = """
    programa Test;
    
    main {
        calcular(5, 10);
    }
    end
    """
    success, errors = analyze_program(src)
    assert not success
    assert any("no declarada" in err for err in errors)


def test_parametros_incorrectos():
    """Detecta número incorrecto de parámetros en llamada."""
    src = """
    programa Test;
    
    void sumar(a: int, b: int) [
        { print(a + b); }
    ];
    
    main {
        sumar(5);
    }
    end
    """
    success, errors = analyze_program(src)
    assert not success
    assert any("espera" in err.lower() or "argumentos" in err.lower() for err in errors)


def test_tipo_parametro_incorrecto():
    """Detecta tipo incorrecto en parámetro de función."""
    src = """
    programa Test;
    var x: float;
    
    void procesar(n: int) [
        { print(n); }
    ];
    
    main {
        x = 3.14;
        procesar(x);
    }
    end
    """
    success, errors = analyze_program(src)
    assert not success
    assert any("argumento" in err.lower() for err in errors)


def test_variables_locales_en_funcion():
    """Verifica que las variables locales funcionan correctamente."""
    src = """
    programa Test;
    var global: int;
    
    void func(x: int) [
        var local: int;
        {
            local = x + 1;
            print(local);
        }
    ];
    
    main {
        global = 10;
        func(global);
    }
    end
    """
    success, errors = analyze_program(src)
    assert success, f"Variables locales deberían funcionar: {errors}"


def test_comparaciones():
    """Verifica operadores de comparación."""
    src = """
    programa Test;
    var a, b: int;
    var x: float;
    
    main {
        a = 5;
        b = 10;
        
        if (a < b) {
            print("a es menor");
        };
        
        if (a > 0) {
            print("a es positivo");
        };
        
        x = 3.14;
        if (x != 0.0) {
            print("x es diferente de cero");
        };
    }
    end
    """
    success, errors = analyze_program(src)
    assert success, f"Comparaciones deberían ser válidas: {errors}"


def test_expresiones_mixtas():
    """Verifica expresiones con int y float mezclados."""
    src = """
    programa Test;
    var i: int;
    var f: float;
    
    main {
        i = 5;
        f = 3.14;
        
        f = i + f;
        f = f * 2.0 + i;
    }
    end
    """
    success, errors = analyze_program(src)
    assert success, f"Expresiones mixtas deberían ser válidas: {errors}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

