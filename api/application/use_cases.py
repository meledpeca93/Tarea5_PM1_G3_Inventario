from domain.entities import Disco
from domain.repositories import DiscoRepository


class DiscoService:

    def __init__(self, repository: DiscoRepository):
        self.repository = repository

    def listar_discos(self) -> list[Disco]:
        return self.repository.listar()

    def obtener_disco(self, disco_id: int) -> Disco | None:
        if disco_id <= 0:
            raise ValueError("El ID debe ser positivo")

        return self.repository.obtener_por_id(disco_id)

    def registrar_disco(
        self,
        marca: str,
        modelo: str,
        tipo: str,
        capacidad_gb: int,
        interfaz: str,
        precio_usd: float
    ) -> Disco:

        disco = Disco(
            id=None,
            marca=marca,
            modelo=modelo,
            tipo=tipo.upper(),
            capacidad_gb=capacidad_gb,
            interfaz=interfaz,
            precio_usd=precio_usd
        )

        return self.repository.crear(disco)
