from dataclasses import dataclass


@dataclass(frozen=True)
class Disco:
    id: int | None
    marca: str
    modelo: str
    tipo: str
    capacidad_gb: int
    interfaz: str
    precio_usd: float

    def __post_init__(self):
        if not self.marca.strip():
            raise ValueError("La marca es obligatoria")

        if not self.modelo.strip():
            raise ValueError("El modelo es obligatorio")

        if self.tipo.upper() not in ("SSD", "HDD"):
            raise ValueError("El tipo debe ser SSD o HDD")

        if type(self.capacidad_gb) is not int or self.capacidad_gb <= 0:
            raise ValueError("La capacidad debe ser un entero positivo")

        if not self.interfaz.strip():
            raise ValueError("La interfaz es obligatoria")

        if isinstance(self.precio_usd, bool) or not isinstance(
            self.precio_usd, (int, float)
        ):
            raise ValueError("El precio debe ser numerico")

        if not (0 <= self.precio_usd < float("inf")):
            raise ValueError("El precio debe ser positivo o cero")
