import pytest

from facturacion import calcular_total


def test_total_sin_descuento():
    """Una factura de 100 € sin descuento cuesta 121 € con IVA."""
    assert calcular_total(100) == 121.0


def test_total_con_descuento():
    """El descuento se aplica antes del IVA."""
    assert calcular_total(100, 0.10) == 108.9


def test_descuento_del_50_permitido():
    """El 50 % es el descuento máximo y está permitido."""
    assert calcular_total(100, 0.5) == 60.5


# Regla de negocio: el descuento máximo es el 50 % (aprobado por Finanzas).
def test_descuento_superior_al_50_no_permitido():
    """Ningún descuento puede superar el 50 %."""
    with pytest.raises(ValueError):
        calcular_total(100, 0.6)


def test_descuento_negativo_no_permitido():
    """Un descuento negativo es un error."""
    with pytest.raises(ValueError):
        calcular_total(100, -0.1)


def test_base_negativa_no_permitida():
    """Una base imponible negativa es un error."""
    with pytest.raises(ValueError):
        calcular_total(-1)
