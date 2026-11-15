from flask import Flask

from infrastructure.sqlite_repository import (
    SQLiteDiscoRepository
)
from application.use_cases import DiscoService
from presentation.routes import crear_rutas


def create_app():
    app = Flask(__name__)

    # Infraestructura
    repositorio = SQLiteDiscoRepository()

    # Aplicacion
    servicio = DiscoService(repositorio)

    # Presentacion
    app.register_blueprint(
        crear_rutas(servicio)
    )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
