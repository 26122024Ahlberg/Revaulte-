import reflex as rx

from .components import (
    ROTA_CATALOGO_ANTIGA,
    ROTA_ESTOQUE,
    ROTA_HOME,
    ROTA_MODIFICADOS,
    ROTA_USADOS,
    ROTA_VEICULO,
    pagina_admin,
    pagina_anunciar,
    pagina_cadastro,
    pagina_conta,
    pagina_entrar,
    pagina_estoque,
    pagina_ficha_anuncio,
    pagina_inicial,
    pagina_meus_anuncios,
    pagina_nao_encontrada,
    pagina_veiculo,
)
from .anuncios import ROTA_FICHA_ANUNCIO, AnunciarState, FichaAnuncioState, MeusAnunciosState
from .auth import (
    ROTA_ADMIN,
    ROTA_ANUNCIAR,
    ROTA_CADASTRO,
    ROTA_CONTA,
    ROTA_ENTRAR,
    ROTA_MEUS_ANUNCIOS,
    AuthState,
)
from .state import CarrosselState, CatalogState, DetalheState, MenuState

FONTES_GOOGLE = (
    "https://fonts.googleapis.com/css2?family=League+Gothic"
    "&family=Poppins:wght@300;400;500;600;700&display=swap"
)


def estoque() -> rx.Component:
    return pagina_estoque(ROTA_ESTOQUE, "Estoque", "Não há veículos no catálogo no momento.")


def usados() -> rx.Component:
    return pagina_estoque(ROTA_USADOS, "Usados", "Não há veículos usados no momento.")


def modificados() -> rx.Component:
    return pagina_estoque(
        ROTA_MODIFICADOS, "Modificados", "Não há veículos modificados no momento."
    )


# Menu "Minha conta" (tarefa 3.4): as páginas públicas chamam AuthState.verificar_sessao,
# que só consulta auth/me quando há token e a sessão ainda não foi conferida nesta conexão.
app = rx.App(
    # Identidade visual da Revaulte, portada de frontend-html/css/styles.css.
    stylesheets=[FONTES_GOOGLE, "/styles.css"],
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
    ],
    html_lang="pt-BR",
)
# Páginas de estoque: mesma estrutura, com recorte fixo aplicado no estado.
for componente, rota, titulo, recorte in (
    (estoque, ROTA_ESTOQUE, "Estoque | Revaulte", "todos"),
    (usados, ROTA_USADOS, "Usados | Revaulte", "usados"),
    (modificados, ROTA_MODIFICADOS, "Modificados | Revaulte", "modificados"),
):
    app.add_page(
        componente,
        route=rota,
        title=titulo,
        on_load=[MenuState.fechar_menu, AuthState.verificar_sessao, CatalogState.abrir_pagina(recorte)],
    )

# Página inicial: os destaques usam o recorte "destaques" do catálogo.
app.add_page(
    pagina_inicial,
    route=ROTA_HOME,
    title="Revaulte | Clássicos, esportivos e preparados",
    description="Carros antigos, clássicos, esportivos e modificados/preparados.",
    on_load=[
        MenuState.fechar_menu,
        AuthState.verificar_sessao,
        CarrosselState.reiniciar,
        CatalogState.abrir_pagina("destaques"),
    ],
)

# Página individual do veículo; o identificador é validado no DetalheState.
app.add_page(
    pagina_veiculo,
    route=ROTA_VEICULO,
    title="Veículo | Revaulte",
    on_load=[MenuState.fechar_menu, AuthState.verificar_sessao, DetalheState.abrir],
)

# Login (Change contas-acesso). abrir_formulario limpa a mensagem, guarda o destino seguro
# (?proximo=) e leva quem já está autenticado direto para ele.
app.add_page(
    pagina_entrar,
    route=ROTA_ENTRAR,
    title="Entrar | Revaulte",
    on_load=[MenuState.fechar_menu, AuthState.abrir_formulario],
)

# Cadastro de Cliente (Change contas-acesso): mesmo on_load do login.
app.add_page(
    pagina_cadastro,
    route=ROTA_CADASTRO,
    title="Criar conta | Revaulte",
    on_load=[MenuState.fechar_menu, AuthState.abrir_formulario],
)

# Minha conta (Change contas-acesso): exigir_login confere o token no backend a cada abertura
# e leva o visitante a /entrar?proximo=/conta.
app.add_page(
    pagina_conta,
    route=ROTA_CONTA,
    title="Minha conta | Revaulte",
    on_load=[MenuState.fechar_menu, AuthState.exigir_login],
)

# Painel administrativo (Change contas-acesso): exigir_admin confere token e perfil no backend;
# visitante vai a /entrar?proximo=/admin e Cliente vê "Acesso restrito".
app.add_page(
    pagina_admin,
    route=ROTA_ADMIN,
    title="Painel administrativo | Revaulte",
    on_load=[MenuState.fechar_menu, AuthState.exigir_admin],
)

# Anúncios dos Clientes (Change anuncios-cliente). abrir confere a sessão no backend (auth/me)
# a cada abertura e leva o visitante a /entrar?proximo=<rota>; só então consulta GET /anuncios.
app.add_page(
    pagina_anunciar,
    route=ROTA_ANUNCIAR,
    title="Anunciar veículo | Revaulte",
    on_load=[MenuState.fechar_menu, AnunciarState.abrir],
)

app.add_page(
    pagina_meus_anuncios,
    route=ROTA_MEUS_ANUNCIOS,
    title="Meus anúncios | Revaulte",
    on_load=[MenuState.fechar_menu, MeusAnunciosState.abrir],
)

# Ficha privada: o identificador é validado no FichaAnuncioState; inválido não consulta o backend.
app.add_page(
    pagina_ficha_anuncio,
    route=ROTA_FICHA_ANUNCIO,
    title="Meu anúncio | Revaulte",
    on_load=[MenuState.fechar_menu, FichaAnuncioState.abrir],
)

# Endereço antigo do catálogo, mantido para não quebrar links.
app.add_page(
    rx.fragment,
    route=ROTA_CATALOGO_ANTIGA,
    title="Estoque | Revaulte",
    on_load=rx.redirect(ROTA_ESTOQUE, replace=True),
)

app.add_page(
    pagina_nao_encontrada,
    route="404",
    title="Página não encontrada | Revaulte",
    on_load=[MenuState.fechar_menu, AuthState.verificar_sessao],
)
