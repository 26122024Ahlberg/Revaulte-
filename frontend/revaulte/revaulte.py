import reflex as rx

from .components import (
    ROTA_CATALOGO_ANTIGA,
    ROTA_ESTOQUE,
    ROTA_HOME,
    ROTA_MODIFICADOS,
    ROTA_USADOS,
    ROTA_VEICULO,
    pagina_estoque,
    pagina_inicial,
    pagina_nao_encontrada,
    pagina_veiculo,
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
        on_load=[MenuState.fechar_menu, CatalogState.abrir_pagina(recorte)],
    )

# Página inicial: os destaques usam o recorte "destaques" do catálogo.
app.add_page(
    pagina_inicial,
    route=ROTA_HOME,
    title="Revaulte | Clássicos, esportivos e preparados",
    description="Carros antigos, clássicos, esportivos e modificados/preparados.",
    on_load=[MenuState.fechar_menu, CarrosselState.reiniciar, CatalogState.abrir_pagina("destaques")],
)

# Página individual do veículo; o identificador é validado no DetalheState.
app.add_page(
    pagina_veiculo,
    route=ROTA_VEICULO,
    title="Veículo | Revaulte",
    on_load=[MenuState.fechar_menu, DetalheState.abrir],
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
    on_load=MenuState.fechar_menu,
)
