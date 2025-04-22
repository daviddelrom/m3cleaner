import sys
import re
import sqlite3
from collections import defaultdict

DB_FILE = "preferencias_canales.db"

def crear_bd():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS canales (
                            tvg_id TEXT PRIMARY KEY,
                            nombre TEXT,
                            url TEXT,
                            activo INTEGER
                        )''')

def guardar_preferencia(canal):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''INSERT OR REPLACE INTO canales (tvg_id, nombre, url, activo)
                        VALUES (?, ?, ?, ?)''',
                     (canal['tvg-id'], canal['nombre'], canal['url'], int(canal['activo'])))

def cargar_preferencia(tvg_id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute('SELECT nombre, url, activo FROM canales WHERE tvg_id = ?', (tvg_id,))
        fila = cursor.fetchone()
        if fila:
            return {
                'nombre': fila[0],
                'url': fila[1],
                'activo': bool(fila[2])
            }
        return None

def cargar_m3u(ruta_archivo):
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        contenido = f.read().splitlines()

    canales = []
    i = 0
    while i < len(contenido):
        if contenido[i].startswith("#EXTINF"):
            linea_info = contenido[i]
            url = contenido[i + 1] if i + 1 < len(contenido) else ''
            tvg_id = re.search(r'tvg-id="([^"]+)"', linea_info)
            nombre = linea_info.split(",")[-1].strip()
            tvg_id = tvg_id.group(1) if tvg_id else nombre

            canal = {
                'tvg-id': tvg_id,
                'nombre': nombre,
                'linea_info': linea_info,
                'url': url,
                'activo': True
            }

            # Cargar preferencias guardadas
            preferencia = cargar_preferencia(tvg_id)
            if preferencia and preferencia['url'] == url:
                canal['activo'] = preferencia['activo']
            canales.append(canal)
            i += 2
        else:
            i += 1
    return canales

def agrupar_por_tvg_id(canales):
    agrupado = defaultdict(list)
    for canal in canales:
        agrupado[canal['tvg-id']].append(canal)
    return agrupado

def activar_desactivar_todo(agrupado, activar=True):
    for canales in agrupado.values():
        for c in canales:
            c['activo'] = activar

def menu_principal():
    print("\nMenú:")
    print("1. Activar/desactivar canales individuales")
    print("2. Activar todos los canales")
    print("3. Desactivar todos los canales")
    print("4. Cambiar fuente de canal (solo activados)")
    print("5. Generar archivo m3u filtrado")
    print("q. Salir")

def activar_desactivar(agrupado):
    ids = list(agrupado.keys())
    while True:
        print("\nLista de canales:")
        for i, id_canal in enumerate(ids):
            activo = any(c['activo'] for c in agrupado[id_canal])
            estado = "-Activado-" if activo else "-Desactivado-"
            print(f"{i+1}. {id_canal} {estado}")
        entrada = input("Selecciona canal a activar/desactivar (q para salir): ")
        if entrada.lower() == 'q':
            break
        if entrada.isdigit() and 1 <= int(entrada) <= len(ids):
            idx = int(entrada) - 1
            grupo = agrupado[ids[idx]]
            nuevo_estado = not any(c['activo'] for c in grupo)
            for c in grupo:
                c['activo'] = nuevo_estado
        else:
            print("Entrada inválida.")

def cambiar_fuente(agrupado):
    ids = [k for k in agrupado if any(c['activo'] for c in agrupado[k])]
    if not ids:
        print("No hay canales activados.")
        return
    while True:
        print("\nSelecciona canal para cambiar fuente (solo activados):")
        for i, id_canal in enumerate(ids):
            activo = [c for c in agrupado[id_canal] if c['activo']]
            activo_str = activo[0]['nombre'] if activo else "Desactivado"
            print(f"{i+1}. {id_canal} (Fuente actual: {activo_str})")
        entrada = input("Selecciona canal (q para salir): ")
        if entrada.lower() == 'q':
            break
        if entrada.isdigit() and 1 <= int(entrada) <= len(ids):
            idx = int(entrada) - 1
            opciones = agrupado[ids[idx]]
            print(f"Opciones para {ids[idx]}:")
            for j, c in enumerate(opciones):
                print(f"{j+1}. {c['nombre']}")
            eleccion = input("Elige variante: ")
            if eleccion.isdigit() and 1 <= int(eleccion) <= len(opciones):
                for c in opciones:
                    c['activo'] = False
                opciones[int(eleccion)-1]['activo'] = True
            else:
                print("Entrada inválida.")
        else:
            print("Entrada inválida.")

def generar_m3u(agrupado, nombre_archivo="filtrado.m3u"):
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for canales in agrupado.values():
            for c in canales:
                if c['activo']:
                    f.write(f"{c['linea_info']}\n{c['url']}\n")
                    guardar_preferencia(c)
    print(f"\n✅ Archivo generado: {nombre_archivo}")

def main():
    if len(sys.argv) < 2:
        print("Uso: python m3u_filter.py archivo.m3u")
        sys.exit(1)

    crear_bd()

    ruta = sys.argv[1]
    canales = cargar_m3u(ruta)
    agrupado = agrupar_por_tvg_id(canales)

    while True:
        menu_principal()
        opcion = input("Selecciona una opción: ")
        if opcion == '1':
            activar_desactivar(agrupado)
        elif opcion == '2':
            activar_desactivar_todo(agrupado, activar=True)
        elif opcion == '3':
            activar_desactivar_todo(agrupado, activar=False)
        elif opcion == '4':
            cambiar_fuente(agrupado)
        elif opcion == '5':
            generar_m3u(agrupado)
        elif opcion.lower() == 'q':
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    main()

