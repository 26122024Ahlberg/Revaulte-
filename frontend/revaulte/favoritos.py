# Favoritos do Cliente (Change favoritos). As requisições saem do servidor do Reflex; o token
# da conta só vai no cabeçalho. O backend devolve apenas ids; os dados dos veículos vêm do
# catálogo público (GET /vehicles), que nunca inclui Rascunho.
import dataclasses

import reflex as rx

from .auth import NOME_COOKIE, ROTA_ENTRAR, ROTA_FAVORITOS, AuthState, chamar_xano
from .config import catalog_api_url, favoritos_api_url
from .state import CartaoVeiculo, IMAGEM_PROVISORIA, _id_da_rota, ler_id_veiculo, preparar_cartao

ERRO_GENERICO_FAVORITO = "Não foi possível concluir agora. Verifique sua conexão e tente novamente."
ERRO_INDISPONIVEL = "Este veículo não está disponível para favoritar."
ERRO_MUITAS_TENTATIVAS = "Muitas tentativas em pouco tempo. Aguarde alguns segundos e tente novamente."
ERRO_RESTRITO_FAVORITO = "Sua conta não tem permissão para usar favoritos."


# ---------------------------------------------------------------------------
# Funções puras.
# ---------------------------------------------------------------------------


def preparar_ids(corpo: object) -> list[int]:
    """Ids favoritados, na ordem recebida (mais recentes primeiro). Itens malformados e
    repetidos são descartados; resposta que não seja lista gera ValueError."""
    if not isinstance(corpo, list):
        raise ValueError("Resposta inesperada de favoritos")
    ids: list[int] = []
    for item in corpo:
        valor = item.get("vehicle_id") if isinstance(item, dict) else None
        if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0 or valor in ids:
            continue
        ids.append(valor)
    return ids


def selecionar_cartoes(ids: list[int], veiculos: object) -> list[CartaoVeiculo]:
    """Cartões dos favoritos presentes no catálogo público, na ordem de `ids`.
    Favorito que não está no catálogo (Rascunho, removido) não aparece."""
    if not isinstance(veiculos, list):
        raise ValueError("Resposta inesperada do catálogo")
    por_id: dict[int, CartaoVeiculo] = {}
    for veiculo in veiculos:
        if not isinstance(veiculo, dict):
            continue
        try:
            cartao = preparar_cartao(veiculo)
        except ValueError:
            continue
        por_id[cartao.id] = cartao
    return [por_id[i] for i in ids if i in por_id]


def mensagem_erro_favorito(status: int) -> str:
    """Texto exibido para uma resposta diferente de 200; nunca o texto cru do backend."""
    if status == 404:
        return ERRO_INDISPONIVEL
    if status == 403:
        return ERRO_RESTRITO_FAVORITO
    if status == 429:
        return ERRO_MUITAS_TENTATIVAS
    return ERRO_GENERICO_FAVORITO


def _sessao_expirada(auth, rota: str) -> list:
    auth._encerrar()
    return [rx.remove_cookie(NOME_COOKIE), rx.redirect(f"{ROTA_ENTRAR}?proximo={rota}")]


async def _consultar_favoritos(token: str) -> tuple[int, object]:
    return await chamar_xano("GET", f"{favoritos_api_url()}/favoritos", token)


# ---------------------------------------------------------------------------
# Estado.
# ---------------------------------------------------------------------------


class FavoritosState(rx.State):
    """Favoritos da conta: botão da página do veículo e página /favoritos."""

    # Página /favoritos: "carregando", "lista", "vazio", "restrito" ou "erro".
    situacao: str = "carregando"
    cartoes: list[CartaoVeiculo] = []
    mensagem_erro: str = ""
    # Botão da página do veículo.
    veiculo_id: int = 0
    favorito_atual: bool = False
    ocupado: bool = False
    erro_botao: str = ""

    @rx.event
    def limpar(self):
        """Apaga tudo o que veio da conta (saída da conta)."""
        self.situacao = "carregando"
        self.cartoes = []
        self.mensagem_erro = ""
        self.veiculo_id = 0
        self.favorito_atual = False
        self.ocupado = False
        self.erro_botao = ""

    # -- Página do veículo -------------------------------------------------

    @rx.event
    async def verificar_veiculo(self):
        """on_load de /veiculo/<id>: com sessão, descobre se o veículo já é favorito."""
        self.favorito_atual = False
        self.ocupado = False
        self.erro_botao = ""
        self.veiculo_id = ler_id_veiculo(_id_da_rota(self.router.page.params, self.router.page.raw_path)) or 0
        auth = await self.get_state(AuthState)
        if not auth.token or self.veiculo_id == 0:
            return
        veiculo = self.veiculo_id
        status, corpo = await _consultar_favoritos(auth.token)
        if status != 200 or self.veiculo_id != veiculo:
            return  # o botão continua utilizável; o erro aparece ao acioná-lo
        try:
            self.favorito_atual = veiculo in preparar_ids(corpo)
        except ValueError:
            pass

    @rx.event
    async def alternar(self):
        """Favorita ou remove o veículo aberto; visitante vai ao login e volta à mesma página."""
        veiculo = self.veiculo_id
        if veiculo == 0 or self.ocupado:
            return
        rota = f"/veiculo/{veiculo}"
        auth = await self.get_state(AuthState)
        if not auth.token:
            yield rx.redirect(f"{ROTA_ENTRAR}?proximo={rota}")
            return
        self.ocupado = True
        self.erro_botao = ""
        yield
        metodo = "DELETE" if self.favorito_atual else "POST"
        status, _ = await chamar_xano(metodo, f"{favoritos_api_url()}/favoritos/{veiculo}", auth.token)
        self.ocupado = False
        if self.veiculo_id != veiculo:
            return
        if status == 401:
            yield _sessao_expirada(auth, rota)
            return
        if status != 200:
            self.erro_botao = mensagem_erro_favorito(status)
            return
        self.favorito_atual = metodo == "POST"

    # -- Página /favoritos -------------------------------------------------

    @rx.event
    async def abrir(self):
        """on_load de /favoritos e ação de "Tentar novamente"."""
        self.situacao = "carregando"
        self.cartoes = []
        self.mensagem_erro = ""
        yield
        auth = await self.get_state(AuthState)
        redirecionar = await auth._exigir(ROTA_FAVORITOS, None)
        if redirecionar is not None:
            yield redirecionar
            return
        if auth.situacao_protegida != "ok":
            self.situacao = "erro"
            self.mensagem_erro = ERRO_GENERICO_FAVORITO
            return
        status, corpo = await _consultar_favoritos(auth.token)
        if status == 401:
            yield _sessao_expirada(auth, ROTA_FAVORITOS)
            return
        if status == 403:
            self.situacao = "restrito"
            return
        if status != 200:
            self.situacao = "erro"
            self.mensagem_erro = mensagem_erro_favorito(status)
            return
        try:
            ids = preparar_ids(corpo)
        except ValueError as erro:
            print(f"Falha ao carregar favoritos: {erro}")
            self.situacao = "erro"
            self.mensagem_erro = ERRO_GENERICO_FAVORITO
            return
        if not ids:
            self.situacao = "vazio"
            return
        status, veiculos = await chamar_xano("GET", f"{catalog_api_url()}/vehicles")
        try:
            if status != 200:
                raise ValueError(f"status {status}")
            self.cartoes = selecionar_cartoes(ids, veiculos)
        except ValueError as erro:
            print(f"Falha ao carregar o catálogo dos favoritos: {erro}")
            self.situacao = "erro"
            self.mensagem_erro = mensagem_erro_favorito(status) if status in (429,) else ERRO_GENERICO_FAVORITO
            return
        self.situacao = "lista" if self.cartoes else "vazio"

    @rx.event
    async def remover(self, id_veiculo: int):
        """Remove um favorito da lista; em falha, a lista continua como estava e o erro é mostrado."""
        if isinstance(id_veiculo, bool) or not isinstance(id_veiculo, int):
            return
        auth = await self.get_state(AuthState)
        status, _ = await chamar_xano("DELETE", f"{favoritos_api_url()}/favoritos/{id_veiculo}", auth.token)
        if status == 401:
            yield _sessao_expirada(auth, ROTA_FAVORITOS)
            return
        if status != 200:
            self.mensagem_erro = mensagem_erro_favorito(status)
            return
        self.mensagem_erro = ""
        self.cartoes = [c for c in self.cartoes if c.id != id_veiculo]
        if not self.cartoes:
            self.situacao = "vazio"

    @rx.event
    def usar_imagem_provisoria(self, id_veiculo: int, capa: str):
        """Troca a capa que falhou ao carregar pela imagem provisória (mesma regra do catálogo)."""
        cartoes = [
            dataclasses.replace(c, capa=IMAGEM_PROVISORIA) if c.id == id_veiculo and c.capa == capa else c
            for c in self.cartoes
        ]
        if cartoes != self.cartoes:
            self.cartoes = cartoes
