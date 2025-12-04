from patito.patito_parser import parse_and_validate

def show_quadruples(prog, title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)
    print("\nCódigo fuente:")
    print("-" * 70)
    print(prog)
    print("-" * 70)
    
    sdt = parse_and_validate(prog)
    
    if sdt.errors:
        print("\nErrores encontrados:")
        for err in sdt.errors:
            print(f"  - {err}")
    else:
        print("\nSin errores semánticos")
    
    print(f"\nCuádruplos generados ({len(sdt.quadruples)}):")
    print("-" * 70)
    for i, quad in enumerate(sdt.quadruples):
        op, arg1, arg2, result = quad
        print(f"{i:3d}: {op:10s} {str(arg1):15s} {str(arg2):15s} {str(result):15s}")
    print()

prog1 = """
programa Ejemplo1;
var x, y, z: int;

main {
    x = 10;
    y = 20;
    z = (x + y) * 2 - 5;
    print("Resultado:", z);
}
end
"""

prog2 = """
programa Ejemplo2;
var n, suma: int;

main {
    n = 1;
    suma = 0;
    while (n < 6) do {
        suma = suma + n;
        n = n + 1;
    };
    print("Suma:", suma);
}
end
"""

prog3 = """
programa Ejemplo3;
var edad: int;

main {
    edad = 18;
    if (edad > 17) {
        print("Mayor de edad");
    } else {
        print("Menor de edad");
    };
}
end
"""

prog4 = """
programa Ejemplo4;
var a, b: int;

main {
    a = 5;
    if (a > 0) {
        b = a * 2;
        print("Positivo");
    };
    print("Fin");
}
end
"""

prog5 = """
programa Ejemplo5;
var x, y: int;
var resultado: float;

void calcular(a: int, b: int) [
    var temp: int;
    {
        temp = a + b;
        print("Suma:", temp);
    }
];

main {
    x = 10;
    y = 20;
    calcular(x, y);
    resultado = 3.14;
}
end
"""

prog6 = """
programa Ejemplo6;
var i, j: int;

main {
    i = 0;
    while (i < 3) do {
        j = 0;
        while (j < 2) do {
            print("i:", i, "j:", j);
            j = j + 1;
        };
        i = i + 1;
    };
}
end
"""

show_quadruples(prog1, "Expresiones Aritméticas")
show_quadruples(prog2, "Ciclo While con Acumulador")
show_quadruples(prog3, "If-Else Completo")
show_quadruples(prog4, "If Sin Else")
show_quadruples(prog5, "Función con Parámetros")
show_quadruples(prog6, "Ciclos While Anidados")

print("\n" + "=" * 70)
print("  RESUMEN")
print("=" * 70)
print("\nSe han generado cuádruplos correctamente para:")
print("  ✓ Expresiones aritméticas y relacionales")
print("  ✓ Asignaciones")
print("  ✓ Estatutos de impresión (print)")
print("  ✓ Estatutos condicionales (if-else)")
print("  ✓ Ciclos (while)")
print("  ✓ Llamadas a funciones")
print("\nOperadores de control de flujo generados:")
print("  - GOTO: Salto incondicional")
print("  - GOTOF: Salto condicional (si falso)")
print()

