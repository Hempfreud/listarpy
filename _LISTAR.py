from pathlib import Path
import os
import stat
import sys
import ctypes

EXTENSIONES_VALIDAS = {".nsp", ".chd", ".7z", ".pkg", ".cia"}

CARPETAS_EXCLUIDAS = {
    "$recycle.bin",
    "system volume information",
}


def obtener_etiqueta_disco(ruta):
    if os.name != "nt":
        return "root"

    try:
        drive = Path(ruta).anchor
        volume_name = ctypes.create_unicode_buffer(1024)
        filesystem_name = ctypes.create_unicode_buffer(1024)

        ctypes.windll.kernel32.GetVolumeInformationW(
            ctypes.c_wchar_p(drive),
            volume_name,
            ctypes.sizeof(volume_name),
            None,
            None,
            None,
            filesystem_name,
            ctypes.sizeof(filesystem_name),
        )

        etiqueta = volume_name.value.strip()
        return etiqueta if etiqueta else drive.replace(":\\", "")

    except Exception:
        return "root"


def es_oculto_path(path_obj):
    # Unix ocultos
    if path_obj.name.startswith("."):
        return True

    # Windows ocultos
    if os.name == "nt":
        try:
            attrs = os.stat(path_obj, follow_symlinks=False).st_file_attributes
            return bool(attrs & stat.FILE_ATTRIBUTE_HIDDEN)
        except Exception:
            return False

    return False


def es_carpeta_excluida(nombre):
    nombre = nombre.lower()

    if nombre in CARPETAS_EXCLUIDAS:
        return True

    if nombre.startswith("found."):
        return True

    return False


def barra_progreso(actual, total, ancho=30):
    porcentaje = actual / total if total else 1
    bloques = int(ancho * porcentaje)
    barra = "#" * bloques + "-" * (ancho - bloques)
    print(f"\r[{barra}] {porcentaje*100:6.2f}% ", end="")
    sys.stdout.flush()


def escanear_directorio(ruta):
    total_archivos = 0
    total_bytes = 0
    procesados = 0

    print("\nCalculando tamaño total...\n")

    for root, dirs, files in os.walk(ruta):

        # Filtrar carpetas excluidas y ocultas
        dirs[:] = [
            d for d in dirs
            if not es_carpeta_excluida(d)
            and not es_oculto_path(Path(root) / d)
        ]

        for file in files:
            ruta_archivo = Path(root) / file

            if es_oculto_path(ruta_archivo):
                continue

            try:
                stat_info = os.stat(ruta_archivo, follow_symlinks=False)
                total_bytes += stat_info.st_size
                total_archivos += 1
                procesados += 1
                print(f"\rArchivos procesados: {procesados}", end="")
            except (PermissionError, OSError):
                continue

    print()
    return total_archivos, total_bytes


def main():
    print("〜Estás usando el *maravilloso* script LISTAR de Hempfreud〜\n")

    ruta_carpeta = Path(__file__).parent

    if ruta_carpeta.name:
        nombre_base = ruta_carpeta.name
    else:
        nombre_base = obtener_etiqueta_disco(ruta_carpeta)

    archivo_salida = ruta_carpeta / f"{nombre_base}.txt"

    if archivo_salida.exists():
        print(f"ERROR: ¡El archivo '{archivo_salida.name}' ya existe!\n")
        opcion = input("¿Borrar y crear uno nuevo? (s/n): ").strip().lower()
        if opcion == "s":
            archivo_salida.unlink()
        else:
            print("Operación cancelada.")
            input("Presiona Enter para cerrar...")
            return

    print("Generando lista de carpetas y archivos...\n")

    carpetas = []
    archivos = []

    for elemento in ruta_carpeta.iterdir():

        if elemento.is_symlink():
            continue

        if es_oculto_path(elemento):
            continue

        if elemento.is_dir() and es_carpeta_excluida(elemento.name):
            continue

        if elemento.is_dir():
            carpetas.append(elemento.name)

        elif (
            elemento.is_file()
            and elemento != archivo_salida
            and elemento.suffix.lower() in EXTENSIONES_VALIDAS
        ):
            archivos.append(elemento.name)

    carpetas.sort(key=str.lower)
    archivos.sort(key=str.lower)

    total_archivos, tamano_total_bytes = escanear_directorio(str(ruta_carpeta))
    tamano_total_gb = tamano_total_bytes / (1024 ** 3)

    with open(archivo_salida, "w", encoding="utf-8") as f:

        f.write("Carpetas:\n\n")
        print("\nCarpetas:\n")

        if carpetas:
            for nombre in carpetas:
                linea = f"- {nombre}\n"
                f.write(linea)
                print(linea, end="")
        else:
            mensaje = "- No hay carpetas.\n"
            f.write(mensaje)
            print(mensaje, end="")

        f.write("\n")
        print()

        f.write("Archivos:\n\n")
        print("Archivos:\n")

        if archivos:
            for nombre in archivos:
                linea = f"- {nombre}\n"
                f.write(linea)
                print(linea, end="")
        else:
            mensaje = "- No hay archivos.\n"
            f.write(mensaje)
            print(mensaje, end="")

        resumen = (
            f"\nTotal de archivos reales: {total_archivos}\n"
            f"Archivos listados (ext válidas): {len(archivos)}\n\n"
            "TAMAÑO TOTAL:\n"
            f"{tamano_total_gb:.2f} GB\n"
        )

        f.write(resumen)
        print(resumen)

    print("¡LISTO!\n")
    input("Presiona Enter para cerrar...")


if __name__ == "__main__":
    main()
