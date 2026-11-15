from abc import ABC, abstractmethod
from .entities import Disco


class DiscoRepository(ABC):

    @abstractmethod
    def listar(self) -> list[Disco]:
        pass

    @abstractmethod
    def obtener_por_id(self, disco_id: int) -> Disco | None:
        pass

    @abstractmethod
    def crear(self, disco: Disco) -> Disco:
        pass
