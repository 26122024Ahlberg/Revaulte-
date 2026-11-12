# Testes da pesquisa e dos filtros do estoque (Change pesquisa-filtros-catalogo).
# Execução, dentro de frontend/: python -m unittest discover -s tests -v
import re
import unittest
from types import SimpleNamespace

from revaulte.components import (
    FILTROS_POR_PAGINA,
    ROTA_ESTOQUE,
    ROTA_MODIFICADOS,
    ROTA_USADOS,
    barra_filtros,
    pagina_estoque,
    pagina_inicial,
    regiao_estoque,
)
from revaulte.state import CartaoVeiculo, CatalogState, aplicar_recorte, filtrar_cartoes, normalizar_texto


def codigo(componente) -> str:
    return re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), str(componente))


def cartao(id, titulo, usado=True, modificado=False, vendido=False) -> CartaoVeiculo:
    return CartaoVeiculo(
        id=id, titulo=titulo, ano="2000", quilometragem="1 km", condicao="Usado" if usado else "Novo",
        preco="R$ 1,00", usado=usado, modificado=modificado, vendido=vendido, capa="/placeholder.svg",
    )


ESTOQUE = [
    cartao(1, "Chevrolet Opala SS"),
    cartao(2, "Ford Maverick GT V8", modificado=True),
    cartao(3, "Volkswagen Gol GTI Turbo", modificado=True),
    cartao(4, "Citroën C4 Lounge", usado=False),
    cartao(5, "Volkswagen Gol Copa", vendido=True),
    cartao(6, "Porsche 911 Turbo", usado=False, modificado=True),
]


def ids(cartoes):
    return [c.id for c in cartoes]


class TestFiltragem(unittest.TestCase):
    def test_pesquisa_por_modelo(self):
        self.assertEqual(ids(filtrar_cartoes(ESTOQUE, "opala", "todos", "todos")), [1])

    def test_pesquisa_sem_acento_e_maiusculas(self):
        self.assertEqual(ids(filtrar_cartoes(ESTOQUE, "CITROEN", "todos", "todos")), [4])
        self.assertEqual(ids(filtrar_cartoes(ESTOQUE, "citroën c4", "todos", "todos")), [4])

    def test_pesquisa_por_versao_e_marca(self):
        self.assertEqual(ids(filtrar_cartoes(ESTOQUE, "turbo", "todos", "todos")), [3, 6])
        self.assertEqual(ids(filtrar_cartoes(ESTOQUE, "volkswagen", "todos", "todos")), [3, 5])

    def test_pesquisa_vazia(self):
        for busca in ("", "   "):
            self.assertEqual(ids(filtrar_cartoes(ESTOQUE, busca, "todos", "todos")), [1, 2, 3, 4, 5, 6])

    def test_filtros_combinados(self):
        self.assertEqual(ids(filtrar_cartoes(ESTOQUE, "", "usado", "modificados")), [2, 3])
        self.assertEqual(ids(filtrar_cartoes(ESTOQUE, "", "novo", "originais")), [4])
        self.assertEqual(ids(filtrar_cartoes(ESTOQUE, "turbo", "novo", "todos")), [6])

    def test_pesquisa_com_recorte(self):
        modificados = aplicar_recorte(ESTOQUE, "modificados")
        self.assertEqual(ids(filtrar_cartoes(modificados, "gol", "todos", "todos")), [3])

    def test_vendido_continua_filtravel(self):
        resultado = filtrar_cartoes(ESTOQUE, "copa", "usado", "originais")
        self.assertEqual(ids(resultado), [5])
        self.assertTrue(resultado[0].vendido)

    def test_nenhum_resultado(self):
        self.assertEqual(filtrar_cartoes(ESTOQUE, "ferrari", "todos", "todos"), [])

    def test_normalizacao(self):
        self.assertEqual(normalizar_texto("  Citroën   C4 "), "citroen c4")
        self.assertEqual(normalizar_texto(None), "")


class TestEstado(unittest.TestCase):
    def estado(self):
        return SimpleNamespace(
            recorte="todos", situacao="lista", cartoes=list(ESTOQUE),
            busca="gol", filtro_condicao="usado", filtro_modificacao="modificados",
        )

    def test_abrir_pagina_reinicia_os_filtros(self):
        e = self.estado()
        CatalogState.event_handlers["abrir_pagina"].fn(e, "usados")
        self.assertEqual((e.busca, e.filtro_condicao, e.filtro_modificacao), ("", "todos", "todos"))

    def test_limpar_filtros(self):
        e = self.estado()
        CatalogState.event_handlers["limpar_filtros"].fn(e)
        self.assertEqual((e.busca, e.filtro_condicao, e.filtro_modificacao), ("", "todos", "todos"))

    def test_valores_invalidos_voltam_a_todos(self):
        e = self.estado()
        CatalogState.event_handlers["definir_condicao"].fn(e, "seminovo")
        CatalogState.event_handlers["definir_modificacao"].fn(e, None)
        self.assertEqual((e.filtro_condicao, e.filtro_modificacao), ("todos", "todos"))
        CatalogState.event_handlers["definir_condicao"].fn(e, "novo")
        self.assertEqual(e.filtro_condicao, "novo")


class TestComponentes(unittest.TestCase):
    def test_filtros_por_pagina(self):
        self.assertEqual(FILTROS_POR_PAGINA[ROTA_ESTOQUE], ("condicao", "modificacao"))
        self.assertEqual(FILTROS_POR_PAGINA[ROTA_USADOS], ("modificacao",))
        self.assertEqual(FILTROS_POR_PAGINA[ROTA_MODIFICADOS], ("condicao",))

    def test_controles_rotulados(self):
        gerado = codigo(barra_filtros(("condicao", "modificacao")))
        for id_campo in ("busca-estoque", "filtro-condicao", "filtro-modificacao"):
            with self.subTest(id_campo=id_campo):
                self.assertIn(f'htmlFor:"{id_campo}"', gerado)
                self.assertIn(f'id:"{id_campo}"', gerado)
        self.assertIn('role:"search"', gerado)
        self.assertIn("DebounceInput", gerado)

    def test_usados_sem_filtro_de_condicao(self):
        gerado = codigo(pagina_estoque(ROTA_USADOS, "Usados", "vazio"))
        self.assertIn('id:"filtro-modificacao"', gerado)
        self.assertNotIn('id:"filtro-condicao"', gerado)
        gerado = codigo(pagina_estoque(ROTA_MODIFICADOS, "Modificados", "vazio"))
        self.assertIn('id:"filtro-condicao"', gerado)
        self.assertNotIn('id:"filtro-modificacao"', gerado)

    def test_nenhum_resultado_distinto_do_vazio(self):
        gerado = codigo(regiao_estoque("Não há veículos no catálogo no momento."))
        self.assertIn("Nenhum veículo corresponde aos critérios de pesquisa.", gerado)
        self.assertIn("Não há veículos no catálogo no momento.", gerado)
        self.assertIn("Limpar filtros", gerado)

    def test_home_sem_barra_de_filtros(self):
        self.assertNotIn("busca-estoque", codigo(pagina_inicial()))


if __name__ == "__main__":
    unittest.main()
