import os
import sqlite3
from pathlib import Path

from domain.entities import Disco
from domain.repositories import DiscoRepository


class SQLiteDiscoRepository(DiscoRepository):

    def __init__(self, db_path=None):
        self.db_path = db_path or os.getenv(
            "DB_PATH", "/datos/inventario.db"
        )

        Path(self.db_path).parent.mkdir(
            parents=True, exist_ok=True
        )

        self.inicializar_base()

    def conectar(self):
        conexion = sqlite3.connect(
            self.db_path,
            timeout=10
        )
        conexion.row_factory = sqlite3.Row
        conexion.execute("PRAGMA busy_timeout = 10000")
        return conexion

    def inicializar_base(self):
        with self.conectar() as conexion:
            conexion.execute("""
                CREATE TABLE IF NOT EXISTS discos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    marca TEXT NOT NULL,
                    modelo TEXT NOT NULL,
                    tipo TEXT NOT NULL
                        CHECK(tipo IN ('SSD', 'HDD')),
                    capacidad_gb INTEGER NOT NULL
                        CHECK(capacidad_gb > 0),
                    interfaz TEXT NOT NULL,
                    precio_usd REAL NOT NULL
                        CHECK(precio_usd >= 0)
                )
            """)

            cantidad = conexion.execute(
                "SELECT COUNT(*) FROM discos"
            ).fetchone()[0]

            if cantidad == 0:
                self.insertar_datos_iniciales(conexion)

    def insertar_datos_iniciales(self, conexion):
        discos = [
            ("Samsung", "970 EVO Plus", "SSD",
             500, "NVMe", 89.99),

            ("Western Digital", "WD Blue", "HDD",
             1000, "SATA III", 49.99),

            ("Kingston", "A400", "SSD",
             480, "SATA III", 35.99),

            ("Seagate", "BarraCuda", "HDD",
             2000, "SATA III", 64.99),

            ("Crucial", "MX500", "SSD",
             1000, "SATA III", 79.99)
        ]

        conexion.executemany("""
            INSERT INTO discos (
                marca, modelo, tipo, capacidad_gb,
                interfaz, precio_usd
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, discos)

    @staticmethod
    def convertir_a_entidad(fila):
        if fila is None:
            return None

        return Disco(
            id=fila["id"],
            marca=fila["marca"],
            modelo=fila["modelo"],
            tipo=fila["tipo"],
            capacidad_gb=fila["capacidad_gb"],
            interfaz=fila["interfaz"],
            precio_usd=fila["precio_usd"]
        )

    def listar(self):
        with self.conectar() as conexion:
            filas = conexion.execute(
                "SELECT * FROM discos ORDER BY id"
            ).fetchall()

        return [
            self.convertir_a_entidad(fila)
            for fila in filas
        ]

    def obtener_por_id(self, disco_id):
        with self.conectar() as conexion:
            fila = conexion.execute(
                "SELECT * FROM discos WHERE id = ?",
                (disco_id,)
            ).fetchone()

        return self.convertir_a_entidad(fila)

    def crear(self, disco):
        with self.conectar() as conexion:
            cursor = conexion.execute("""
                INSERT INTO discos (
                    marca, modelo, tipo, capacidad_gb,
                    interfaz, precio_usd
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                disco.marca,
                disco.modelo,
                disco.tipo,
                disco.capacidad_gb,
                disco.interfaz,
                disco.precio_usd
            ))

            nuevo_id = cursor.lastrowid

        return self.obtener_por_id(nuevo_id)
