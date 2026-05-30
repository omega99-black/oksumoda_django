import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS productos (
    id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    foto VARCHAR(500),
    estado VARCHAR(20) DEFAULT 'activo',
    precio DECIMAL(12,2) NOT NULL,
    cantidad_stock INTEGER DEFAULT 0,
    categoria VARCHAR(100),
    subcategoria VARCHAR(100),
    colores VARCHAR(200),
    tallas VARCHAR(200),
    precioAnterior DECIMAL(12,2),
    esNuevo BOOLEAN DEFAULT 0
)
""")

conn.commit()
conn.close()
print('Tabla creada exitosamente')
