# Testes do simulador de financiamento (Change simulador-financiamento).
# Execução, dentro de frontend/: python -m unittest discover -s tests -v
import re
import unittest
from decimal import Decimal
from types import SimpleNamespace

from revaulte.components import AVISO_SIMULACAO, conteudo_detalhe, secao_simulador
from revaulte.state import (
    OPCOES_PARCELAS,
    DetalheState,
    calcular_financiamento,
    entrada_inicial,
    ler_valor_br,
    preparar_detalhe,
    simular,
)


def codigo(componente) -> str:
    return re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), str(componente))


class TestCalculo(unittest.TestCase):
    def test_cenario_com_juros_da_spec(self):
        r = simular("100000.00", "20.000,00", 48, "1,5")
        self.assertEqual(r.erro, "")
        self.assertEqual(r.financiado, "R$ 80.000,00")
        self.assertEqual(r.parcela, "R$ 2.350,00")
        self.assertEqual(r.total, "R$ 132.800,00")
        self.assertEqual(r.juros, "R$ 32.800,00")

    def test_cenario_taxa_zero_da_spec(self):
        r = simular("100000.00", "40.000,00", 60, "0")
        self.assertEqual((r.parcela, r.juros), ("R$ 1.000,00", "R$ 0,00"))

    def test_total_fecha_com_a_parcela_arredondada(self):
        r = calcular_financiamento(Decimal("118900"), Decimal("23780"), 36, Decimal("1.99"))
        self.assertEqual(r["total"], Decimal("23780") + r["parcela"] * 36)
        self.assertEqual(r["juros"], r["total"] - Decimal("118900"))

    def test_entrada_zero(self):
        self.assertEqual(simular("100000.00", "0", 12, "0").parcela, "R$ 8.333,33")

    def test_mudar_o_prazo_recalcula(self):
        self.assertNotEqual(
            simular("100000.00", "20.000", 48, "1,5").parcela,
            simular("100000.00", "20.000", 24, "1,5").parcela,
        )


class TestValidacao(unittest.TestCase):
    def erro(self, entrada="20.000", taxa="1,5", parcelas=48):
        return simular("100000.00", entrada, parcelas, taxa).erro

    def test_entrada_invalida(self):
        self.assertIn("menor que o valor do veículo", self.erro(entrada="100.000,00"))
        self.assertIn("menor que o valor do veículo", self.erro(entrada="150000"))
        self.assertIn("negativa", self.erro(entrada="-1"))
        self.assertIn("Informe a entrada", self.erro(entrada="abc"))
        self.assertIn("Informe a entrada", self.erro(entrada=""))
        self.assertIn("duas casas", self.erro(entrada="10,555"))

    def test_taxa_invalida(self):
        for taxa in ("abc", "12", "5,01", "-1", "1,555", ""):
            with self.subTest(taxa=taxa):
                self.assertIn("entre 0% e 5%", self.erro(taxa=taxa))
        self.assertEqual(self.erro(taxa="5"), "")

    def test_prazo_invalido(self):
        self.assertIn("prazo", self.erro(parcelas=30))

    def test_erro_nao_traz_resultado(self):
        r = simular("100000.00", "abc", 48, "1,5")
        self.assertEqual((r.parcela, r.total, r.juros), ("", "", ""))


class TestLeitura(unittest.TestCase):
    def test_formato_brasileiro(self):
        casos = {
            "20.000,50": "20000.50", "20.000": "20000", "1,5": "1.5", "1.5": "1.5",
            "R$ 1.234.567,89": "1234567.89", " 300 ": "300", "1,50%": "1.50",
        }
        for texto, esperado in casos.items():
            with self.subTest(texto=texto):
                self.assertEqual(ler_valor_br(texto), Decimal(esperado))

    def test_textos_invalidos(self):
        for texto in ("abc", "", "1,2,3", "1..2", "--1", None):
            with self.subTest(texto=texto):
                self.assertIsNone(ler_valor_br(texto))


class TestEstado(unittest.TestCase):
    def test_valores_iniciais(self):
        self.assertEqual(entrada_inicial("189900.00"), "37.980,00")
        d = preparar_detalhe({
            "id": 1, "brand": "Chevrolet", "model": "Opala", "year": 1978, "condition": "used",
            "mileage": 72000, "price": 118900, "status": "available",
        })
        self.assertEqual(d.preco_numero, "118900.00")

    def test_prazo_so_aceita_opcoes(self):
        e = SimpleNamespace(parcelas=48)
        fn = DetalheState.event_handlers["definir_parcelas"].fn
        fn(e, 24)
        self.assertEqual(e.parcelas, 24)
        for invalido in (30, "12", None, 0):
            fn(e, invalido)
            self.assertEqual(e.parcelas, 24)
        self.assertEqual(OPCOES_PARCELAS, (12, 24, 36, 48, 60))


class TestComponentes(unittest.TestCase):
    def test_secao(self):
        gerado = codigo(secao_simulador())
        for texto in ("Simular financiamento", "Valor do veículo", "Entrada", "Prazo",
                      "Taxa de juros ilustrativa", "Total pago", "Total de juros", AVISO_SIMULACAO):
            with self.subTest(texto=texto):
                self.assertIn(texto, gerado)
        for n in OPCOES_PARCELAS:
            self.assertIn(f'"aria-label":"{n} parcelas"', gerado)
        self.assertIn('htmlFor:"sim-entrada"', gerado)
        self.assertIn('id:"sim-entrada"', gerado)

    def test_simulador_so_para_disponivel(self):
        gerado = codigo(conteudo_detalhe())
        self.assertIn('(!(reflex___state____state__revaulte___state____detalhe_state.veiculo_rx_state_?.["vendido"])', gerado)

    def test_sem_oferta_nem_contratacao(self):
        textos = " ".join(re.findall(r'"([^"]*)"', codigo(secao_simulador()))).lower()
        for termo in ("contrat", "aprovad", "oferta", "banco", "solicitar", "garant"):
            with self.subTest(termo=termo):
                # "contratação" e "aprovação" só aparecem dentro do aviso, negadas.
                self.assertNotIn(termo, textos.replace(AVISO_SIMULACAO.lower(), ""))


if __name__ == "__main__":
    unittest.main()
