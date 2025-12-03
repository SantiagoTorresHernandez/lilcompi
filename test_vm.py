"""
Test de la Máquina Virtual Patito

Prueba la ejecución completa de programas compilados.
"""

from patito import parse_and_validate, VirtualMachine, run_from_source


def test_and_show(name, source_code):
    """Ejecuta un programa y muestra los resultados."""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print('='*60)
    print("\nCódigo fuente:")
    print("-"*40)
    print(source_code.strip())
    print("-"*40)
    
    # Compilar
    sdt = parse_and_validate(source_code)
    
    if sdt.has_errors():
        print(f"\n❌ Errores de compilación:")
        for err in sdt.errors:
            print(f"   {err}")
        return False
    
    print(f"\n✓ Compilado ({len(sdt.quadruples)} cuádruplos)")
    
    # Mostrar cuádruplos
    print("\nCuádruplos generados:")
    for i, quad in enumerate(sdt.quadruples):
        op, a1, a2, r = quad
        a1_str = str(a1) if a1 is not None else "-"
        a2_str = str(a2) if a2 is not None else "-"
        r_str = str(r) if r is not None else "-"
        print(f"  {i:03}: {op:10} {a1_str:15} {a2_str:15} {r_str}")
    
    # Ejecutar
    print("\n" + "-"*40)
    print("Ejecutando en VM...")
    print("-"*40)
    print("Salida:")
    
    obj_data = sdt.to_obj()
    vm = VirtualMachine(obj_data)
    
    try:
        output = vm.execute()
        print()  # Nueva línea después de salida
        print("-"*40)
        print("✓ Ejecución exitosa")
        
        # Mostrar estado de memoria
        snapshot = vm.get_memory_snapshot()
        if snapshot['global']:
            print(f"\nMemoria global: {snapshot['global']}")
        
        return True
    except Exception as e:
        print(f"\n❌ Error de ejecución: {e}")
        return False


# ============================================================
# TESTS
# ============================================================

# Test 1: Expresiones aritméticas básicas
test1 = """
programa Test1;
var x, y, z: int;

main {
    x = 10;
    y = 20;
    z = x + y * 2;
    print("z = ", z);
}
end
"""

# Test 2: Ciclo while
test2 = """
programa Test2;
var i, suma: int;

main {
    i = 1;
    suma = 0;
    while (i < 6) do {
        suma = suma + i;
        i = i + 1;
    };
    print("Suma 1-5 = ", suma);
}
end
"""

# Test 3: If-else
test3 = """
programa Test3;
var edad: int;

main {
    edad = 20;
    if (edad > 17) {
        print("Mayor de edad");
    } else {
        print("Menor de edad");
    };
}
end
"""

# Test 4: Función void con parámetros
test4 = """
programa Test4;
var a, b: int;

void mostrar(x: int, y: int) [
    var suma: int;
    {
        suma = x + y;
        print("Suma: ", suma);
    }
];

main {
    a = 5;
    b = 7;
    mostrar(a, b);
    print(" Fin");
}
end
"""

# Test 5: Función con valor de retorno
test5 = """
programa Test5;
var resultado: int;

int sumar(a: int, b: int) [
    var temp: int;
    {
        temp = a + b;
        return(temp);
    }
];

main {
    resultado = sumar(10, 25);
    print("10 + 25 = ", resultado);
}
end
"""

# Test 6: Función recursiva (factorial)
test6 = """
programa TestFactorial;
var n, fact: int;

int factorial(x: int) [
    var res: int;
    {
        if (x < 2) {
            return(1);
        } else {
            res = x * factorial(x - 1);
            return(res);
        };
    }
];

main {
    n = 5;
    fact = factorial(n);
    print("5! = ", fact);
}
end
"""

# Test 7: Múltiples funciones
test7 = """
programa TestMulti;
var x: int;

int doble(n: int) [
    {
        return(n * 2);
    }
];

int triple(n: int) [
    {
        return(n * 3);
    }
];

main {
    x = 5;
    print("Doble de 5: ", doble(x));
    print(" Triple de 5: ", triple(x));
}
end
"""

# ============================================================
# EJECUTAR TODOS LOS TESTS
# ============================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  PRUEBAS DE LA MÁQUINA VIRTUAL PATITO")
    print("="*60)
    
    tests = [
        ("Expresiones Aritméticas", test1),
        ("Ciclo While", test2),
        ("If-Else", test3),
        ("Función Void", test4),
        ("Función con Retorno", test5),
        ("Función Recursiva (Factorial)", test6),
        ("Múltiples Funciones", test7),
    ]
    
    results = []
    for name, code in tests:
        result = test_and_show(name, code)
        results.append((name, result))
    
    # Resumen
    print("\n\n" + "="*60)
    print("  RESUMEN DE PRUEBAS")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\nResultado: {passed}/{total} pruebas pasaron")
    print("="*60)

