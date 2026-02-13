from pathlib import Path

def main():
    ruta_carpeta = Path(__file__).parent
    archivo_salida = ruta_carpeta / f"{ruta_carpeta.name}.txt"

    # Verificar si el archivo ya existe
    if archivo_salida.exists():
        print(f"¡El archivo '{archivo_salida.name}' ya existe!")
        opcion = input("¿Borrar y crear uno nuevo? (s/n): ").strip().lower()
        if opcion == "s":
            archivo_salida.unlink()  # Borra el archivo existente
            print("Creando nueva lista...\n")
        else:
            print("Operación cancelada.")
            input("Presiona Enter para cerrar...")
            return  # Sale del script

    total_carpetas = 0
    total_archivos = 0

    print("Generando lista de carpetas y archivos...\n")

    with open(archivo_salida, "w", encoding="utf-8") as f:
        # Bloque de carpetas
        f.write(f"Carpetas:")
        print("Carpetas:\n")
        for elemento in ruta_carpeta.iterdir():
            if elemento.is_dir():
                linea = f"- {elemento.name}\n"
                f.write(linea) 
                print(linea, end="")
                total_carpetas += 1

        # Separación de bloques
        f.write("\n")
        print()

        # Bloque de archivos
        f.write(f"Archivos:")
        print("Archivos:\n")
        for elemento in ruta_carpeta.iterdir():
            if elemento.is_file():
                if elemento.suffix.lower() not in [".py", ".txt"]:
                    linea = f"- {elemento.name}\n"
                    f.write(linea)
                    print(linea, end="")
                    total_archivos += 1

        # Resumen final
        resumen = f"\nTotal de carpetas: {total_carpetas}\nTotal de archivos: {total_archivos}\n"
        print(resumen)

    print("¡LISTO!\n")
    input("Presiona Enter para cerrar...")

if __name__ == "__main__":
    main()