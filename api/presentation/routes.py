import os
import socket
from dataclasses import asdict
from datetime import datetime, timezone

from flask import Blueprint, jsonify, render_template_string, request

from application.use_cases import DiscoService


def crear_rutas(servicio: DiscoService):
    api = Blueprint("api", __name__)

    @api.get("/api/estado")
    def estado():
        datos = {
            "aplicacion": os.getenv(
                "APP_NOMBRE", "g3-discos-api"
            ),
            "estado": "ok",
            "hostname": socket.gethostname(),
            "fecha_hora": datetime.now(
                timezone.utc
            ).isoformat(),
            "grupo": 3,
            "componente": "Almacenamiento"
        }

        if "text/html" in request.headers.get("Accept", ""):
            return render_template_string("""
                <!doctype html>
                <html lang="es">
                <head>
                  <meta charset="utf-8">
                  <meta name="viewport" content="width=device-width, initial-scale=1">
                  <meta name="theme-color" content="#101827">
                  <title>Estado de la API · {{ datos.aplicacion }}</title>
                  <style>
                    * { box-sizing: border-box; }
                    body {
                      min-height: 100vh; margin: 0; padding: 32px 18px;
                      display: grid; place-items: center;
                      color: #e8eef8; font: 16px/1.5 system-ui, sans-serif;
                      background: radial-gradient(ellipse at 50% 0, #1d3654, #101827 62%);
                    }
                    main {
                      width: min(100%, 720px); padding: clamp(24px, 6vw, 48px);
                      border: 1px solid #29384d; border-radius: 24px;
                      background: #172235; box-shadow: 0 24px 80px #050a1280;
                    }
                    .eyebrow { color: #9aacc4; font-size: .78rem; letter-spacing: .16em; }
                    h1 { margin: 8px 0 20px; font-size: clamp(2rem, 7vw, 3.2rem); }
                    .status {
                      display: inline-flex; align-items: center; gap: 10px;
                      padding: 9px 14px; border: 1px solid #176a50;
                      border-radius: 999px; color: #8af0c1; background: #12392f;
                      font-weight: 700;
                    }
                    .dot { width: 10px; height: 10px; border-radius: 50%; background: #45dfa2; box-shadow: 0 0 14px #45dfa2; }
                    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 12px; margin-top: 30px; }
                    .item { padding: 16px; border: 1px solid #2b3a50; border-radius: 14px; background: #1c2a3e; }
                    .label { display: block; margin-bottom: 5px; color: #9aacc4; font-size: .82rem; }
                    .value { overflow-wrap: anywhere; font-weight: 650; }
                    footer { margin-top: 26px; color: #9aacc4; font-size: .85rem; }
                    code { color: #9ed5ff; }
                  </style>
                </head>
                <body>
                  <main>
                    <div class="eyebrow">GRUPO {{ datos.grupo }} · {{ datos.componente }}</div>
                    <h1>Estado del servicio</h1>
                    <div class="status"><span class="dot"></span> API en línea</div>
                    <section class="grid" aria-label="Detalles del servicio">
                      <div class="item"><span class="label">Aplicación</span><span class="value">{{ datos.aplicacion }}</span></div>
                      <div class="item"><span class="label">Estado</span><span class="value">{{ datos.estado }}</span></div>
                      <div class="item"><span class="label">Contenedor</span><span class="value">{{ datos.hostname }}</span></div>
                      <div class="item"><span class="label">Comprobado (UTC)</span><span class="value">{{ datos.fecha_hora }}</span></div>
                    </section>
                    <footer>La API respondió correctamente a <code>GET /api/estado</code>.</footer>
                  </main>
                </body>
                </html>
            """, datos=datos)

        return jsonify(datos), 200

    @api.get("/api/discos")
    def listar_discos():
        discos = servicio.listar_discos()
        registros = [
            asdict(disco) for disco in discos
        ]

        if "text/html" in request.headers.get("Accept", ""):
            return render_template_string("""
                <!doctype html>
                <html lang="es">
                <head>
                  <meta charset="utf-8">
                  <meta name="viewport" content="width=device-width, initial-scale=1">
                  <meta name="theme-color" content="#111827">
                  <title>Inventario de discos · Grupo 3</title>
                  <style>
                    * { box-sizing: border-box; }
                    body {
                      margin: 0; min-height: 100vh; padding: 40px 20px;
                      color: #e5e7eb; font: 15px/1.5 system-ui, sans-serif;
                      background: #111827;
                    }
                    main {
                      width: min(100%, 1050px); margin: 0 auto; padding: 30px;
                      border: 1px solid #374151; border-radius: 18px;
                      background: #1f2937;
                    }
                    a { color: #93c5fd; }
                    .top { display: flex; justify-content: space-between; gap: 20px; }
                    .eyebrow { color: #9ca3af; font-size: .8rem; letter-spacing: .12em; }
                    h1 { margin: 6px 0; font-size: clamp(1.7rem, 5vw, 2.5rem); }
                    .summary { color: #9ca3af; }
                    .table-wrap { overflow-x: auto; margin-top: 24px; }
                    table { width: 100%; border-collapse: collapse; text-align: left; }
                    th, td { padding: 13px 12px; border-bottom: 1px solid #374151; }
                    th { color: #9ca3af; font-size: .75rem; letter-spacing: .06em; }
                    tbody tr:hover { background: #273449; }
                    .badge {
                      display: inline-block; padding: 3px 9px; border-radius: 999px;
                      color: #bfdbfe; background: #1e3a5f; font-size: .8rem;
                    }
                    .price { text-align: right; white-space: nowrap; }
                    @media (max-width: 600px) {
                      body { padding: 16px 10px; }
                      main { padding: 18px 12px; }
                      th, td { padding: 10px 8px; }
                    }
                  </style>
                </head>
                <body>
                  <main>
                    <div class="top">
                      <div>
                        <div class="eyebrow">GRUPO 3 · ALMACENAMIENTO</div>
                        <h1>Inventario de discos</h1>
                        <div class="summary">{{ registros|length }} dispositivos registrados · Vista de consulta API</div>
                      </div>
                      <a href="/">Volver a StorageLab</a>
                    </div>
                    <div class="table-wrap">
                      <table>
                        <thead>
                          <tr>
                            <th>ID</th><th>MARCA</th><th>MODELO</th><th>TIPO</th>
                            <th>CAPACIDAD</th><th>INTERFAZ</th><th class="price">PRECIO</th>
                          </tr>
                        </thead>
                        <tbody>
                          {% for disco in registros %}
                          <tr>
                            <td>{{ disco.id }}</td>
                            <td>{{ disco.marca }}</td>
                            <td>{{ disco.modelo }}</td>
                            <td><span class="badge">{{ disco.tipo }}</span></td>
                            <td>{{ disco.capacidad_gb }} GB</td>
                            <td>{{ disco.interfaz }}</td>
                            <td class="price">${{ "%.2f"|format(disco.precio_usd) }}</td>
                          </tr>
                          {% else %}
                          <tr><td colspan="7">El inventario está vacío.</td></tr>
                          {% endfor %}
                        </tbody>
                      </table>
                    </div>
                  </main>
                </body>
                </html>
            """, registros=registros), 200

        return jsonify({
            "total": len(registros),
            "discos": registros
        }), 200

    @api.get("/api/discos/<int:disco_id>")
    def obtener_disco(disco_id):
        try:
            disco = servicio.obtener_disco(disco_id)
        except ValueError as error:
            return jsonify({
                "error": str(error)
            }), 400

        if disco is None:
            return jsonify({
                "error": "Disco no encontrado"
            }), 404

        return jsonify(asdict(disco)), 200

    @api.post("/api/discos")
    def registrar_disco():
        datos = request.get_json(silent=True)

        if not isinstance(datos, dict):
            return jsonify({
                "error": "Se requiere un objeto JSON"
            }), 400

        campos = [
            "marca", "modelo", "tipo",
            "capacidad_gb", "interfaz", "precio_usd"
        ]

        faltantes = [
            campo for campo in campos
            if campo not in datos
        ]

        if faltantes:
            return jsonify({
                "error": "Faltan campos obligatorios",
                "campos": faltantes
            }), 400

        try:
            for campo in [
                "marca", "modelo", "tipo", "interfaz"
            ]:
                if not isinstance(datos[campo], str):
                    raise ValueError(
                        f"{campo} debe ser texto"
                    )

            if type(datos["capacidad_gb"]) is not int:
                raise ValueError(
                    "capacidad_gb debe ser un entero"
                )

            if type(datos["precio_usd"]) not in (
                int, float
            ):
                raise ValueError(
                    "precio_usd debe ser numerico"
                )

            disco = servicio.registrar_disco(
                marca=datos["marca"].strip(),
                modelo=datos["modelo"].strip(),
                tipo=datos["tipo"].strip(),
                capacidad_gb=datos["capacidad_gb"],
                interfaz=datos["interfaz"].strip(),
                precio_usd=datos["precio_usd"]
            )

        except ValueError as error:
            return jsonify({
                "error": str(error)
            }), 400

        return jsonify({
            "mensaje": "Disco registrado correctamente",
            "disco": asdict(disco)
        }), 201

    return api
