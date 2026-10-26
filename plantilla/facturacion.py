"""Cálculo del total de una factura."""

IVA = 0.21
DESCUENTO_MAXIMO = 0.5


def calcular_total(base: float, descuento: float = 0.0) -> float:
    """Devuelve el total con IVA tras aplicar el descuento (0.10 = 10 %)."""
    if base < 0:
        raise ValueError("La base imponible no puede ser negativa.")
    if descuento < 0:
        raise ValueError("El descuento no puede ser negativo.")
    if descuento > DESCUENTO_MAXIMO:
        raise ValueError(f"El descuento no puede superar el {DESCUENTO_MAXIMO:.0%}.")
    return round(base * (1 - descuento) * (1 + IVA), 2)
