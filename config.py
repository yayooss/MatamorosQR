import sqlite3
import os

# --- ASEGURAMOS QUE LA BD EXISTA EN ESTE PROYECTO ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "matamoros.db")

# --- CONEXION DB ---
def conexion():
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    return conn, cur

# --- TABLAS ---
def crear_tablas():
    conn, cur = conexion()

    try:
        # --- TABLA AREA ---
        cur.execute("""
            CREATE TABLE IF NOT EXISTS area (
                id_area TEXT PRIMARY KEY,
                nom_area TEXT NOT NULL
                )
            """)

        # --- TABLA ACTIVOS ---
        cur.execute("""
            CREATE TABLE IF NOT EXISTS activos (
                id_activos INTEGER PRIMARY KEY AUTOINCREMENT,
                id_area TEXT,
                activo TEXT NOT NULL,
                UNIQUE(id_area, activo),
                FOREIGN KEY(id_area) REFERENCES area(id_area)
                )
            """)

        conn.commit()
    except Exception as e:
        print(f'Error: {e}')
    finally:
        conn.close()

# --- INSERT ACTIVOS ---
def insertar_activos(id_area, activo):
    conn, cur = conexion()

    try:
        # --- ASEGURAMOS QUE EXISTA EL ID AREA ---
        obtener_area(id_area)

        cur.execute("""
            INSERT INTO activos (id_area, activo) VALUES (?, ?)
        """, (id_area, activo))

        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f'Error: {e}')
        return False
    finally:
        conn.close()

# --- OBTENER AREA ---
def obtener_area(id_area):
    conn, cur = conexion()

    try:
        # --- VERIFICAMOS SI EXISTE AREA ---
        cur.execute("SELECT id_area FROM area WHERE id_area = ?", (id_area,))
        r = cur.fetchone()

        # --- SI EXISTE, RETORNAMOS ID ---
        if r:
            return id_area

        # --- SI NO EXISTE, LA INSERTAMOS ---
        cur.execute("SELECT COUNT(*) FROM area")
        count = cur.fetchone()[0] + 1

        # --- GENERAMOS NOMBRE AUTOMATICO ---
        nombre = f'Insert #{count}'

        cur.execute("""
            INSERT INTO area (id_area, nom_area) VALUES (?, ?)
        """, (id_area, nombre))
        conn.commit()
        return id_area
    except Exception as e:
        print(f'Error: {e}')
    finally:
        conn.close()
