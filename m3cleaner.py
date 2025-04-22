import sys
import re
import sqlite3
import urllib.request
from os.path import exists

DB_FILE = "preferencias_canales.db"

# Colores
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def crear_bd():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS channels (
                            tvg_id TEXT PRIMARY KEY,
                            activo INTEGER DEFAULT 0
                        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS sources (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            tvg_id TEXT,
                            nombre TEXT,
                            url TEXT,
                            activo INTEGER DEFAULT 0
                        )''')


def descargar_si_url(entrada):
    if entrada.startswith("http://") or entrada.startswith("https://"):
        contenido = urllib.request.urlopen(entrada).read().decode("utf-8")
        with open("descargado.m3u", "w", encoding="utf-8") as f:
            f.write(contenido)
        return "descargado.m3u"
    return entrada


def cargar_m3u(archivo):
    with open(archivo, "r", encoding="utf-8") as f:
        lineas = f.read().splitlines()

    canales = []
    i = 0
    while i < len(lineas):
        if lineas[i].startswith("#EXTINF"):
            info = lineas[i]
            url = lineas[i+1] if i+1 < len(lineas) else ""
            tvg_id_match = re.search(r'tvg-id="([^"]+)', info)
            tvg_id = tvg_id_match.group(1) if tvg_id_match else None
            nombre = info.split(",")[-1].strip()
            if tvg_id:
                canales.append((tvg_id, nombre, url))
            i += 2
        else:
            i += 1
    return canales


def limpiar_fuentes_inactivas():
    """Eliminar las fuentes que no estén marcadas como activas."""
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("DELETE FROM sources WHERE activo = 0")


def registrar_canales(canales):
    with sqlite3.connect(DB_FILE) as conn:
        # Limpiar las fuentes inactivas antes de insertar nuevas fuentes
        limpiar_fuentes_inactivas()

        for tvg_id, nombre, url in canales:
            conn.execute("INSERT OR IGNORE INTO channels (tvg_id) VALUES (?)", (tvg_id,))

            cursor = conn.execute("SELECT COUNT(*) FROM sources WHERE tvg_id = ?", (tvg_id,))
            if cursor.fetchone()[0] == 0:
                # Si la fuente no existe, se agrega
                conn.execute("INSERT INTO sources (tvg_id, nombre, url, activo) VALUES (?, ?, ?, 0)",
                             (tvg_id, nombre, url))
            else:
                # Si ya existe, respetamos la fuente activa si está presente
                conn.execute("INSERT OR IGNORE INTO sources (tvg_id, nombre, url, activo) VALUES (?, ?, ?, 0)",
                             (tvg_id, nombre, url))
                # Si la fuente estaba activa anteriormente, respetar la decisión
                # conn.execute('''UPDATE sources SET activo = 0
                #                  WHERE tvg_id = ? AND url = ?''',
                #              (tvg_id, url))

        # Eliminar fuentes duplicadas basadas en tvg_id y url
        conn.execute('''
            DELETE FROM sources WHERE id NOT IN (
                SELECT MIN(id) FROM sources GROUP BY tvg_id, url
            )
        ''')


def listar_canales():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute("SELECT tvg_id, activo FROM channels ORDER BY tvg_id")
        canales = cursor.fetchall()
        for idx, (tvg_id, activo) in enumerate(canales):
            estado = f"{GREEN}✔ Activo{RESET}" if activo else f"{RED}✖ Inactivo{RESET}"
            print(f"{idx+1}. {tvg_id} - {estado}")
        return canales


def toggle_canal(tvg_id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute("SELECT activo FROM channels WHERE tvg_id = ?", (tvg_id,))
        actual = cursor.fetchone()[0]
        nuevo = 0 if actual else 1
        conn.execute("UPDATE channels SET activo = ? WHERE tvg_id = ?", (nuevo, tvg_id))


def cambiar_estado_todos(activo):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("UPDATE channels SET activo = ?", (1 if activo else 0,))


def cambiar_fuente():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute("SELECT tvg_id FROM channels WHERE activo = 1 ORDER BY tvg_id")
        activos = [r[0] for r in cursor.fetchall()]

        if not activos:
            print(f"{YELLOW}⚠ No hay canales activos.{RESET}")
            return

        print("\nCanales activos:")
        for idx, tvg_id in enumerate(activos):
            print(f"{idx+1}. {tvg_id}")

        entrada = input("Selecciona canal por número (q para salir): ")
        if entrada.lower() == 'q':
            return

        if entrada.isdigit():
            idx = int(entrada) - 1
            if 0 <= idx < len(activos):
                tvg_id = activos[idx]
                # Mostrar URL del canal
                cursor = conn.execute("SELECT url FROM sources WHERE tvg_id = ? AND activo = 1", (tvg_id,))
                url_data = cursor.fetchone()
                url = url_data[0] if url_data else "No URL disponible"
                print(f"URL del canal {CYAN}{tvg_id}{RESET}: {url}")

                cursor = conn.execute("SELECT id, nombre, activo ,url FROM sources WHERE tvg_id = ?", (tvg_id,))
                fuentes = cursor.fetchall()
                print(f"\nFuentes para {CYAN}{tvg_id}{RESET}:")
                for i, (fid, nombre, activo, url) in enumerate(fuentes):
                    est = f"{GREEN}(actual){RESET}" if activo else ""
                    print(f"{i+1}. {nombre} {url} {est}")

                eleccion = input("Selecciona nueva fuente: ")
                if eleccion.isdigit():
                    idx_fuente = int(eleccion) - 1
                    if 0 <= idx_fuente < len(fuentes):
                        conn.execute("UPDATE sources SET activo = 0 WHERE tvg_id = ?", (tvg_id,))
                        conn.execute("UPDATE sources SET activo = 1 WHERE id = ?", (fuentes[idx_fuente][0],))
                        print(f"✅ Fuente de {tvg_id} actualizada.")


def generar_m3u(nombre="filtrado.m3u"):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute('''SELECT s.tvg_id, s.url
                                 FROM sources s
                                 JOIN channels c ON s.tvg_id = c.tvg_id
                                 WHERE s.activo = 1 AND c.activo = 1''')
        fuentes = cursor.fetchall()

        with open(nombre, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for tvg_id, url in fuentes:
                f.write(f"#EXTINF:-1 tvg-id=\"{tvg_id}\",{tvg_id}\n{url}\n")
        print(f"\n✅ Archivo generado: {YELLOW}{nombre}{RESET}")


def menu():
    while True:
        print(f"\n{CYAN}--- MENÚ ---{RESET}")
        print("1. Activar/desactivar canales individuales")
        print("2. Activar todos los canales")
        print("3. Desactivar todos los canales")
        print("4. Cambiar fuente de canal")
        print("5. Generar archivo m3u filtrado")
        print("q. Salir")
        opcion = input("Selecciona una opción: ")

        if opcion == '1':
            while True:
                canales = listar_canales()
                entrada = input("Selecciona canal por número (q para salir): ")
                if entrada.lower() == 'q':
                    break
                if entrada.isdigit():
                    idx = int(entrada) - 1
                    if 0 <= idx < len(canales):
                        toggle_canal(canales[idx][0])

        elif opcion == '2':
            cambiar_estado_todos(True)
        elif opcion == '3':
            cambiar_estado_todos(False)
        elif opcion == '4':
            cambiar_fuente()
        elif opcion == '5':
            generar_m3u()
        elif opcion.lower() == 'q':
            break
        else:
            print("❌ Opción inválida.")


def main():
    if len(sys.argv) < 2:
        print("Uso: python script.py <archivo o url>")
        sys.exit(1)

    crear_bd()
    archivo = descargar_si_url(sys.argv[1])
    canales = cargar_m3u(archivo)
    registrar_canales(canales)
    menu()


if __name__ == "__main__":
    main()

