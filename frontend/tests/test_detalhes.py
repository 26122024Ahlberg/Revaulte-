# Testes da página individual do veículo (Change detalhes-veiculo).
# Execução, dentro de frontend/: python -m unittest discover -s tests -v
import asyncio
import re
import unittest
from types import SimpleNamespace
from unittest import mock

import httpx

from revaulte import state
from revaulte.components import cartao_veiculo, grade_cartoes, pagina_veiculo, regiao_detalhe
from revaulte.revaulte import app
from revaulte.state import (
    IMAGEM_PROVISORIA,
    CatalogState,
    DetalheState,
    DetalheVeiculo,
    GrupoModificacoes,
    _id_da_rota,
    agrupar_modificacoes,
    buscar_veiculo,
    ler_id_veiculo,
    preparar_detalhe,
)


def codigo(componente) -> str:
    return re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), str(componente))


def veiculo(**extra) -> dict:
    base = {
        "id": 7, "brand": "Ford", "model": "Maverick", "version": "GT V8", "year": 1975,
        "condition": "used", "mileage": 98000, "price": 189900, "is_modified": True,
        "status": "available", "cover_image_url": "https://exemplo.com/maverick.jpg",
    }
    base.update(extra)
    return base


def cliente_falso(responder):
    """Substitui httpx.AsyncClient por um cliente com MockTransport."""
    original = httpx.AsyncClient

    def fabrica(*args, **kwargs):
        kwargs["transport"] = httpx.MockTransport(responder)
        return original(*args, **kwargs)

    return mock.patch.object(state.httpx, "AsyncClient", side_effect=fabrica)


def buscar(id_veiculo, responder):
    with cliente_falso(responder):
        return asyncio.run(buscar_veiculo(id_veiculo))


class TestIdentificador(unittest.TestCase):
    def test_ids_validos(self):
        self.assertEqual(ler_id_veiculo("1"), 1)
        self.assertEqual(ler_id_veiculo(" 42 "), 42)

    def test_ids_invalidos(self):
        for texto in ("", "0", "-1", "abc", "1.5", "+3", "١", "9" * 13, None, 5):
            with self.subTest(texto=texto):
                self.assertIsNone(ler_id_veiculo(texto))

    def test_id_da_rota(self):
        self.assertEqual(_id_da_rota({"veiculo_id": "3"}, "/veiculo/9"), "3")
        self.assertEqual(_id_da_rota({}, "/veiculo/9/"), "9")
        self.assertEqual(_id_da_rota({}, "/estoque"), "")


class TestPreparacao(unittest.TestCase):
    def test_campos_formatados(self):
        d = preparar_detalhe(veiculo())
        self.assertEqual((d.marca, d.modelo, d.versao), ("Ford", "Maverick", "GT V8"))
        self.assertEqual(d.titulo, "Ford Maverick GT V8")
        self.assertEqual((d.ano, d.quilometragem, d.condicao), ("1975", "98.000 km", "Usado"))
        self.assertEqual(d.preco, "R$ 189.900,00")
        self.assertTrue(d.modificado)
        self.assertFalse(d.vendido)

    def test_sem_versao_e_sem_capa(self):
        d = preparar_detalhe(veiculo(version=None, cover_image_url=None))
        self.assertEqual(d.versao, "")
        self.assertEqual(d.capa, IMAGEM_PROVISORIA)


class TestDadosTecnicos(unittest.TestCase):
    def test_campos_cadastrados(self):
        d = preparar_detalhe(veiculo(
            color="  Vermelho ", engine="V8  302", transmission="Manual de 4 marchas",
            description="  Primeiro parágrafo.\n\n\n\nSegundo   parágrafo.  ",
        ))
        self.assertEqual((d.cor, d.motorizacao, d.cambio), ("Vermelho", "V8 302", "Manual de 4 marchas"))
        self.assertEqual(d.descricao, "Primeiro parágrafo.\n\nSegundo parágrafo.")

    def test_dados_parciais_e_ausentes_ficam_vazios(self):
        # O Xano devolve "" para campo não preenchido; nada é inventado.
        d = preparar_detalhe(veiculo(color="Prata", engine="", transmission=None))
        self.assertEqual((d.cor, d.motorizacao, d.cambio, d.descricao), ("Prata", "", "", ""))
        self.assertEqual(d.modificacoes, [])

    def test_agrupamento_por_area(self):
        grupos = agrupar_modificacoes([
            {"area": "suspension", "description": "Coilover"},
            {"area": "engine", "description": "Comando bravo"},
            {"area": "suspension", "description": "Barra estabilizadora"},
            {"area": "inexistente", "description": "Item sem área conhecida"},
            {"area": "brakes", "description": "   "},
        ])
        self.assertEqual(grupos, [
            GrupoModificacoes("Preparação do motor", ["Comando bravo"]),
            GrupoModificacoes("Suspensão", ["Coilover", "Barra estabilizadora"]),
            GrupoModificacoes("Outras modificações", ["Item sem área conhecida"]),
        ])

    def test_modificacoes_ausentes_ou_invalidas(self):
        self.assertEqual(agrupar_modificacoes(None), [])
        self.assertEqual(agrupar_modificacoes([]), [])
        for invalido in ("texto", {"area": "engine"}, [1]):
            with self.subTest(invalido=invalido):
                with self.assertRaises(ValueError):
                    agrupar_modificacoes(invalido)


def detalhe(**extra) -> dict:
    """Resposta de GET /vehicles/{id}: dados de catálogo, técnicos e modificações."""
    base = veiculo(color="", engine="", transmission="", description="", modifications=[])
    base.update(extra)
    return base


class TestBusca(unittest.TestCase):
    def test_consulta_o_endpoint_de_detalhe(self):
        pedidos = []

        def responder(requisicao):
            pedidos.append(requisicao.url.path)
            return httpx.Response(200, json=detalhe(
                engine="V8 302", modifications=[{"area": "engine", "description": "Carburador quadrijet"}],
            ))

        situacao, d = buscar(7, responder)
        self.assertEqual(situacao, "encontrado")
        self.assertTrue(pedidos[0].endswith("/vehicles/7"))
        self.assertEqual(len(pedidos), 1)
        self.assertEqual(d.motorizacao, "V8 302")
        self.assertEqual(d.modificacoes, [GrupoModificacoes("Preparação do motor", ["Carburador quadrijet"])])

    def test_vendido(self):
        situacao, d = buscar(7, lambda r: httpx.Response(200, json=detalhe(status="sold")))
        self.assertEqual(situacao, "encontrado")
        self.assertTrue(d.vendido)

    def test_404_e_nao_encontrado(self):
        # Rascunho e inexistente chegam do Xano como o mesmo 404.
        resposta = {"code": "ERROR_CODE_NOT_FOUND", "message": "Vehicle not found"}
        situacao, d = buscar(99, lambda r: httpx.Response(404, json=resposta))
        self.assertEqual((situacao, d), ("nao_encontrado", None))

    def test_falha_http(self):
        for status in (400, 429, 500):
            with self.subTest(status=status):
                self.assertEqual(buscar(7, lambda r: httpx.Response(status))[0], "erro")

    def test_tempo_esgotado(self):
        def responder(requisicao):
            raise httpx.ReadTimeout("tempo esgotado", request=requisicao)

        self.assertEqual(buscar(7, responder)[0], "erro")

    def test_resposta_invalida(self):
        self.assertEqual(buscar(7, lambda r: httpx.Response(200, json=[detalhe()]))[0], "erro")
        self.assertEqual(buscar(7, lambda r: httpx.Response(200, text="<html>"))[0], "erro")

    def test_outro_veiculo_na_resposta(self):
        self.assertEqual(buscar(7, lambda r: httpx.Response(200, json=detalhe(id=8)))[0], "erro")
        self.assertEqual(buscar(1, lambda r: httpx.Response(200, json=detalhe(id=True)))[0], "erro")

    def test_registro_do_veiculo_invalido(self):
        situacao, _ = buscar(7, lambda r: httpx.Response(200, json=detalhe(condition="x")))
        self.assertEqual(situacao, "erro")
        situacao, _ = buscar(7, lambda r: httpx.Response(200, json=detalhe(modifications="x")))
        self.assertEqual(situacao, "erro")


class TestEstado(unittest.TestCase):
    def estado(self, params, caminho):
        e = SimpleNamespace(
            situacao="", veiculo=DetalheVeiculo(id=1), id_pedido=None,
            router=SimpleNamespace(page=SimpleNamespace(params=params, raw_path=caminho)),
        )
        resultado = DetalheState.event_handlers["abrir"].fn(e)
        return e, resultado

    def test_abrir_id_invalido(self):
        e, resultado = self.estado({"veiculo_id": "abc"}, "/veiculo/abc")
        self.assertEqual(e.situacao, "nao_encontrado")
        self.assertIsNone(resultado)
        self.assertEqual(e.veiculo, DetalheVeiculo())

    def test_abrir_id_valido(self):
        e, resultado = self.estado({"veiculo_id": "2"}, "/veiculo/2")
        self.assertEqual((e.situacao, e.id_pedido), ("carregando", 2))
        self.assertIsNotNone(resultado)

    def test_imagem_provisoria(self):
        e = SimpleNamespace(veiculo=DetalheVeiculo(capa="https://x/y.jpg"))
        DetalheState.event_handlers["usar_imagem_provisoria"].fn(e, "https://outra/z.jpg")
        self.assertEqual(e.veiculo.capa, "https://x/y.jpg")
        DetalheState.event_handlers["usar_imagem_provisoria"].fn(e, "https://x/y.jpg")
        self.assertEqual(e.veiculo.capa, IMAGEM_PROVISORIA)


class TestComponentes(unittest.TestCase):
    def test_modificacoes_somente_para_veiculo_modificado(self):
        gerado = codigo(pagina_veiculo())
        # A seção de modificações depende do selo "modificado" do veículo.
        self.assertIn(
            '["modificado"]?(jsx(Fragment,{},jsx("section",{className:"detail-panel detail-mods"}', gerado
        )
        self.assertIn('className:"mod-area"', gerado)


    def test_rota_registrada(self):
        self.assertIn("veiculo/[veiculo_id]", app._unevaluated_pages)

    def test_cartao_e_link_para_o_veiculo(self):
        gerado = codigo(grade_cartoes(CatalogState.cartoes_exibidos))
        self.assertIn('to:("/veiculo/"+', gerado)
        self.assertIn('className:"card-link"', gerado)

    def test_pagina(self):
        gerado = codigo(pagina_veiculo())
        for texto in (
            "← Voltar ao estoque", "Veículo não encontrado", "Tentar novamente",
            "Anunciado por", "Conversar no WhatsApp", "Contato não disponível", "Marca", "Modelo", "Versão", "Ano", "Quilometragem",
            "Condição", "Os detalhes das modificações não foram informados",
            "indisponível para negociação", "Modificado", "Vendido",
            "Configuração original", "Cor", "Motorização", "Câmbio", "Não informado",
            "Descrição", "Descrição não informada.", "Modificações e preparação",
        ):
            with self.subTest(texto=texto):
                self.assertIn(texto, gerado)
        self.assertEqual(gerado.count('jsx("h1"'), 2)  # veículo ou "não encontrado", nunca juntos

    def test_sem_contato_nem_promessas(self):
        textos = " ".join(re.findall(r'"([^"]*)"', codigo(regiao_detalhe()))).lower()
        # O WhatsApp agora existe (contato-vendedor), mas só pelo link montado no estado:
        # nenhum número fixo no código da página.
        self.assertNotRegex(codigo(regiao_detalhe()), r"wa\.me/[0-9]")
        for termo in ("telefone", "e-mail", "@", "legalizad", "homologad", "regularizad"):
            with self.subTest(termo=termo):
                self.assertNotIn(termo, textos)


if __name__ == "__main__":
    unittest.main()
