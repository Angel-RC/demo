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


# Descuento que corresponde a cada tipo de cliente.
DESCUENTOS_POR_TIPO = {
    "normal": 0.0,
    "fiel": 0.10,
    "premium": 0.25,
}


def total_cliente(base: float, tipo_cliente: str) -> float:
    """Devuelve el total de la factura con el descuento de su tipo de cliente."""
    return calcular_total(base, DESCUENTOS_POR_TIPO[tipo_cliente])
