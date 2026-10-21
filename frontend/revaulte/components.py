# Componentes da interface: topo e menu, rodapé, cartão, selos e mensagens de estado.
import reflex as rx

from .state import (
    IMAGEM_PROVISORIA,
    CarrosselState,
    CartaoVeiculo,
    CatalogState,
    DetalheState,
    MenuState,
)

# Rotas públicas do site.
ROTA_HOME = "/"
ROTA_ESTOQUE = "/estoque"
ROTA_USADOS = "/usados"
ROTA_MODIFICADOS = "/modificados"
ROTA_CATALOGO_ANTIGA = "/catalogo"  # mantida como redirecionamento para ROTA_ESTOQUE
ROTA_VEICULO = "/veiculo/[veiculo_id]"  # página individual do veículo


def endereco_veiculo(id_veiculo) -> str:
    """Endereço da página de um veículo; aceita int ou Var do Reflex."""
    return f"/veiculo/{id_veiculo}"

# Itens do menu principal, na ordem exibida. Só páginas que existem.
ITENS_MENU = (
    ("Home", ROTA_HOME),
    ("Estoque", ROTA_ESTOQUE),
    ("Usados", ROTA_USADOS),
    ("Modificados", ROTA_MODIFICADOS),
)


# Itens da conta: ainda não implementados, exibidos só como "Em breve" e sem link.
ITENS_CONTA = (
    "Meu perfil",
    "Anunciar veículo",
    "Meus anúncios",
    "Favoritos",
    "Entrar / Cadastrar",
)


def item_navegacao(rotulo: str, rota: str, atual: str) -> rx.Component:
    ativo = rota == atual
    return rx.el.li(
        rx.el.a(
            rotulo,
            href=rota,
            class_name="current" if ativo else "",
            custom_attrs={"aria-current": "page"} if ativo else {},
            on_click=MenuState.fechar_menu,
        ),
    )


def lista_navegacao(atual: str) -> rx.Component:
    return rx.el.ul(*(item_navegacao(rotulo, rota, atual) for rotulo, rota in ITENS_MENU))


def item_em_breve(rotulo: str) -> rx.Component:
    """Funcionalidade ainda não implementada: texto desabilitado, sem link nem evento."""
    return rx.el.li(
        rx.el.span(
            rx.el.span(rotulo),
            rx.el.span("Em breve", class_name="soon-tag"),
            class_name="menu-item-disabled",
            custom_attrs={"aria-disabled": "true"},
        ),
    )


def painel_menu(atual: str) -> rx.Component:
    """Painel do botão ☰: "Navegação" (só em telas estreitas, via CSS) e "Minha conta"."""
    return rx.el.div(
        rx.el.section(
            rx.el.h2("Navegação", class_name="menu-panel-title"),
            rx.el.nav(lista_navegacao(atual), custom_attrs={"aria-label": "Navegação principal"}),
            class_name="menu-panel-section menu-panel-nav",
        ),
        rx.el.section(
            rx.el.h2("Minha conta", class_name="menu-panel-title"),
            rx.el.ul(*(item_em_breve(rotulo) for rotulo in ITENS_CONTA)),
            class_name="menu-panel-section",
        ),
        id="menu-painel",
        class_name="menu-panel",
    )


def topo(atual: str) -> rx.Component:
    """Cabeçalho com a marca, a navegação principal e o botão ☰ do painel de menu.

    `atual` é a rota da página exibida. Acima de 760 px a navegação fica no cabeçalho;
    até 760 px ela passa para dentro do painel (ver styles.css).
    """
    return rx.el.header(
        rx.el.a("Revaulte", href=ROTA_HOME, class_name="logo", on_click=MenuState.fechar_menu),
        rx.el.nav(
            lista_navegacao(atual),
            class_name="main-nav",
            custom_attrs={"aria-label": "Navegação principal"},
        ),
        rx.el.button(
            rx.el.span(
                rx.cond(MenuState.menu_aberto, "✕", "☰"),
                class_name="menu-toggle-icon",
                custom_attrs={"aria-hidden": "true"},
            ),
            type="button",
            class_name="menu-toggle",
            on_click=MenuState.alternar_menu,
            custom_attrs={
                "aria-controls": "menu-painel",
                "aria-expanded": rx.cond(MenuState.menu_aberto, "true", "false"),
                "aria-label": rx.cond(MenuState.menu_aberto, "Fechar menu", "Abrir menu"),
            },
        ),
        rx.cond(
            MenuState.menu_aberto,
            rx.fragment(
                # Camada transparente atrás do painel: clicar fora fecha o menu.
                rx.el.div(class_name="menu-backdrop", on_click=MenuState.fechar_menu),
                painel_menu(atual),
            ),
        ),
        class_name="topbar",
    )


def rodape() -> rx.Component:
    return rx.el.footer(
        rx.el.p("Revaulte — veículos novos e usados, originais e modificados."),
        class_name="footer",
    )


def pagina(atual: str, *conteudo: rx.Component) -> rx.Component:
    """Estrutura comum das páginas: topo, conteúdo principal e rodapé."""
    return rx.el.div(topo(atual), *conteudo, rodape(), class_name="page")


class ImagemCapa(rx.el.Img):
    """Elemento de imagem com o gatilho on_error, que rx.el.img não oferece no Reflex 0.10."""

    on_error: rx.EventHandler[rx.event.no_args_event_spec]


def capa_veiculo(src: rx.Var[str], alt: rx.Var[str], on_error: rx.event.EventType) -> rx.Component:
    """Capa do cartão; a imagem provisória substitui a capa ausente ou que falhou ao carregar.

    `src` já vem preparado por `endereco_capa`; `on_error` deve trocar o `src` daquele
    cartão para `IMAGEM_PROVISORIA`.
    """
    return rx.cond(
        src == IMAGEM_PROVISORIA,
        rx.el.img(src=IMAGEM_PROVISORIA, alt=alt, loading="lazy", class_name="is-placeholder"),
        ImagemCapa.create(src=src, alt=alt, loading="lazy", on_error=on_error),
    )


def selo(texto: str, classe: str) -> rx.Component:
    return rx.el.span(texto, class_name=f"badge {classe}")


def cartao_veiculo(cartao: rx.Var[CartaoVeiculo]) -> rx.Component:
    """Cartão de um veículo: capa, selos, título, detalhes e preço.

    Os dados são exibidos como texto pelos componentes do Reflex, sem rx.html. O cartão
    inteiro é um link para a página do veículo (inclusive o vendido, cuja página informa
    a indisponibilidade).
    """
    return rx.el.a(
        rx.el.article(
            rx.el.div(
                capa_veiculo(
                    cartao.capa,
                    cartao.titulo,
                    CatalogState.usar_imagem_provisoria(cartao.id, cartao.capa),
                ),
                rx.cond(
                    cartao.vendido | cartao.modificado,
                    rx.el.div(
                        rx.cond(cartao.vendido, selo("Vendido", "badge-sold")),
                        rx.cond(cartao.modificado, selo("Modificado", "badge-modified")),
                        class_name="badges",
                    ),
                ),
                class_name="card-img",
            ),
            rx.el.div(
                rx.el.h3(cartao.titulo),
                rx.el.p(cartao.ano + " · " + cartao.quilometragem + " · " + cartao.condicao),
                rx.el.strong(cartao.preco),
                class_name="card-info",
            ),
            class_name=rx.cond(cartao.vendido, "card card-sold", "card"),
        ),
        href=endereco_veiculo(cartao.id),
        class_name="card-link",
    )


def grade_cartoes(cartoes: rx.Var[list[CartaoVeiculo]]) -> rx.Component:
    return rx.el.div(rx.foreach(cartoes, cartao_veiculo), class_name="cards")


def regiao_estoque(mensagem_vazio: str) -> rx.Component:
    """Região das páginas de estoque: exibe somente um dos estados carregando, lista,
    vazio ou erro. A lista mostra apenas o recorte da página atual."""
    vazio = rx.el.p(mensagem_vazio, class_name="state-message")
    return rx.el.div(
        rx.match(
            CatalogState.situacao,
            (
                "lista",
                rx.cond(
                    CatalogState.cartoes_exibidos.length() > 0,
                    grade_cartoes(CatalogState.cartoes_exibidos),
                    vazio,
                ),
            ),
            ("vazio", vazio),
            (
                "erro",
                rx.el.div(
                    rx.el.p(
                        "Não foi possível carregar o catálogo. Verifique sua conexão e tente novamente."
                    ),
                    rx.el.button(
                        "Tentar novamente",
                        type="button",
                        class_name="btn btn-red",
                        on_click=CatalogState.carregar_catalogo,
                    ),
                    class_name="state-message",
                ),
            ),
            rx.el.p("Carregando veículos…", class_name="state-message"),
        ),
        id="catalog-region",
        custom_attrs={"aria-live": "polite"},
    )


def pagina_estoque(atual: str, titulo: str, mensagem_vazio: str) -> rx.Component:
    """Página de estoque (/estoque, /usados ou /modificados)."""
    return pagina(
        atual,
        rx.el.main(
            rx.el.h1(titulo, class_name="section-title"),
            regiao_estoque(mensagem_vazio),
            class_name="catalog",
        ),
    )


# Pilares da proposta da Revaulte (seção da página inicial). Sem serviços ou garantias
# que não estejam definidos na documentação do projeto.
PILARES_PROPOSTA = (
    (
        "Antigos e clássicos",
        "Carros que marcaram época, para quem valoriza história, design e engenharia de outros tempos.",
    ),
    (
        "Esportivos",
        "Desempenho e presença para quem gosta de dirigir e de ser notado em cada saída.",
    ),
    (
        "Modificados e preparados",
        "Cada veículo apresenta a configuração original separada das modificações feitas depois.",
    ),
)


# Slides do carrossel da página inicial, na ordem exibida. Fotos do Pexels; origem e
# licença registradas em frontend/README.md.
SLIDES_CARROSSEL = (
    {
        "categoria": "Esportivos",
        "titulo": "Desempenho que acelera o pulso.",
        "texto": "Esportivos para quem vive a estrada com intensidade, do primeiro giro à última curva.",
        "imagem": "/hero-esportivo.jpg",
        "alt": "Carro esportivo vermelho em movimento em uma estrada à beira-mar",
    },
    {
        "categoria": "Modificados",
        "titulo": "Preparados para ir além do original.",
        "texto": "Carros modificados, com as alterações identificadas separadamente da configuração original.",
        "imagem": "/hero-modificado.jpg",
        "alt": "Sedã azul rebaixado, com rodas brancas e visual esportivo, em uma garagem",
    },
    {
        "categoria": "Clássicos",
        "titulo": "Elegância que atravessa décadas.",
        "texto": "Antigos e clássicos para quem valoriza história, design e engenharia de outros tempos.",
        "imagem": "/hero-classico.jpg",
        "alt": "Carro esportivo clássico vermelho estacionado diante de uma cerca viva",
    },
)


def slide_carrossel(posicao: int, slide: dict) -> rx.Component:
    """Um slide; só o ativo fica visível e acessível (os demais têm aria-hidden)."""
    ativo = CarrosselState.indice == posicao
    return rx.el.div(
        rx.el.img(src=slide["imagem"], alt=slide["alt"], class_name="hero-image"),
        rx.el.div(class_name="hero-shade", custom_attrs={"aria-hidden": "true"}),
        rx.el.div(
            rx.el.p(slide["categoria"], class_name="hero-kicker"),
            rx.el.h2(slide["titulo"], class_name="hero-title"),
            rx.el.p(slide["texto"], class_name="hero-text"),
            rx.el.a("Explorar estoque", href=ROTA_ESTOQUE, class_name="btn btn-red"),
            class_name="hero-content",
        ),
        class_name=rx.cond(ativo, "hero-slide is-active", "hero-slide"),
        custom_attrs={
            "role": "group",
            "aria-roledescription": "slide",
            "aria-label": f"{posicao + 1} de {len(SLIDES_CARROSSEL)}: {slide['categoria']}",
            "aria-hidden": rx.cond(ativo, "false", "true"),
        },
    )


def indicador_slide(posicao: int, slide: dict) -> rx.Component:
    ativo = CarrosselState.indice == posicao
    return rx.el.button(
        type="button",
        class_name=rx.cond(ativo, "hero-dot is-active", "hero-dot"),
        on_click=CarrosselState.ir_para(posicao),
        custom_attrs={
            "aria-label": f"Ir para o slide {posicao + 1}: {slide['categoria']}",
            "aria-current": rx.cond(ativo, "true", "false"),
        },
    )


def carrossel_inicial() -> rx.Component:
    """Banner da Home em carrossel: troca manual por setas e indicadores, sem rotação automática."""
    total = len(SLIDES_CARROSSEL)
    return rx.el.section(
        rx.el.h1("Revaulte: clássicos, esportivos e preparados", class_name="sr-only"),
        rx.el.div(
            *(slide_carrossel(i, slide) for i, slide in enumerate(SLIDES_CARROSSEL)),
            class_name="hero-slides",
            custom_attrs={"aria-live": "polite"},
        ),
        rx.el.div(
            rx.el.button(
                rx.el.span("‹", custom_attrs={"aria-hidden": "true"}),
                type="button",
                class_name="hero-arrow",
                on_click=CarrosselState.anterior,
                custom_attrs={"aria-label": "Slide anterior"},
            ),
            rx.el.span(
                rx.el.strong(
                    rx.cond(CarrosselState.indice == 0, "01", rx.cond(CarrosselState.indice == 1, "02", "03"))
                ),
                f" / {total:02d}",
                class_name="hero-counter",
                custom_attrs={"aria-hidden": "true"},
            ),
            rx.el.div(
                *(indicador_slide(i, slide) for i, slide in enumerate(SLIDES_CARROSSEL)),
                class_name="hero-dots",
            ),
            rx.el.button(
                rx.el.span("›", custom_attrs={"aria-hidden": "true"}),
                type="button",
                class_name="hero-arrow",
                on_click=CarrosselState.proximo,
                custom_attrs={"aria-label": "Próximo slide"},
            ),
            class_name="hero-controls",
        ),
        class_name="hero",
        custom_attrs={"aria-roledescription": "carrossel", "aria-label": "Destaques da Revaulte"},
    )


def secao_destaques() -> rx.Component:
    """Os 3 veículos Disponíveis mais recentes, vindos do Xano (recorte "destaques")."""
    return rx.el.section(
        rx.el.div(
            rx.el.h2("Veículos em destaque", class_name="section-title"),
            rx.el.a("Ver todo o estoque", href=ROTA_ESTOQUE, class_name="link-more"),
            class_name="section-head",
        ),
        regiao_estoque("Não há destaques no momento."),
        class_name="home-section featured reveal",
    )


def secao_proposta() -> rx.Component:
    return rx.el.section(
        rx.el.h2("A Revaulte", class_name="section-title"),
        rx.el.p(
            "A Revaulte é especializada em carros antigos, clássicos, esportivos e "
            "modificados/preparados. Não somos uma concessionária genérica: cada anúncio "
            "representa um veículo real, com suas informações apresentadas de forma direta.",
            class_name="proposal-intro",
        ),
        rx.el.div(
            *(
                rx.el.article(
                    rx.el.h3(titulo),
                    rx.el.p(texto),
                    class_name="pillar",
                )
                for titulo, texto in PILARES_PROPOSTA
            ),
            class_name="pillars",
        ),
        class_name="home-section proposal reveal",
    )


def pagina_inicial() -> rx.Component:
    return pagina(
        ROTA_HOME,
        rx.el.main(carrossel_inicial(), secao_destaques(), secao_proposta(), class_name="home"),
    )


def pagina_nao_encontrada() -> rx.Component:
    return pagina(
        "",
        rx.el.main(
            rx.el.h1("Página não encontrada", class_name="section-title"),
            rx.el.div(
                rx.el.p("O endereço acessado não existe no site da Revaulte."),
                rx.el.a("Ir para o estoque", href=ROTA_ESTOQUE, class_name="btn btn-red"),
                class_name="state-message",
            ),
            class_name="catalog",
        ),
    )


# ---------------------------------------------------------------------------
# Página individual do veículo (/veiculo/<id>), Change detalhes-veiculo etapa A.
# ---------------------------------------------------------------------------

MENSAGEM_INTERESSE = "O contato com o anunciante ainda não está disponível nesta versão do site."


def voltar_ao_estoque(classe: str = "link-back") -> rx.Component:
    return rx.el.a("← Voltar ao estoque", href=ROTA_ESTOQUE, class_name=classe)


def item_ficha(rotulo: str, valor: rx.Var[str]) -> rx.Component:
    return rx.el.div(rx.el.dt(rotulo), rx.el.dd(valor), class_name="spec-item")


def imagem_detalhe() -> rx.Component:
    veiculo = DetalheState.veiculo
    return rx.el.div(
        rx.cond(
            veiculo.capa == IMAGEM_PROVISORIA,
            rx.el.img(src=IMAGEM_PROVISORIA, alt=veiculo.titulo, class_name="is-placeholder"),
            ImagemCapa.create(
                src=veiculo.capa,
                alt=veiculo.titulo,
                on_error=DetalheState.usar_imagem_provisoria(veiculo.capa),
            ),
        ),
        rx.cond(
            veiculo.vendido | veiculo.modificado,
            rx.el.div(
                rx.cond(veiculo.vendido, selo("Vendido", "badge-sold")),
                rx.cond(veiculo.modificado, selo("Modificado", "badge-modified")),
                class_name="badges",
            ),
        ),
        class_name=rx.cond(veiculo.vendido, "detail-img is-sold", "detail-img"),
    )


def acao_negociacao() -> rx.Component:
    """Vendido: aviso de indisponibilidade. Disponível: interesse demonstrativo, sem contato."""
    return rx.cond(
        DetalheState.veiculo.vendido,
        rx.el.p(
            "Este veículo já foi vendido e está indisponível para negociação.",
            class_name="detail-notice",
        ),
        rx.el.div(
            rx.el.button(
                "Tenho interesse",
                type="button",
                class_name="btn btn-red",
                on_click=DetalheState.mostrar_interesse,
            ),
            rx.cond(
                DetalheState.interesse_aberto,
                rx.el.p(MENSAGEM_INTERESSE, class_name="detail-notice", role="status"),
            ),
            class_name="detail-actions",
        ),
    )


def conteudo_detalhe() -> rx.Component:
    veiculo = DetalheState.veiculo
    return rx.el.article(
        imagem_detalhe(),
        rx.el.div(
            rx.el.h1(veiculo.titulo, class_name="detail-title"),
            rx.el.strong(veiculo.preco, class_name="detail-price"),
            rx.el.dl(
                item_ficha("Marca", veiculo.marca),
                item_ficha("Modelo", veiculo.modelo),
                rx.cond(veiculo.versao != "", item_ficha("Versão", veiculo.versao)),
                item_ficha("Ano", veiculo.ano),
                item_ficha("Quilometragem", veiculo.quilometragem),
                item_ficha("Condição", veiculo.condicao),
                class_name="spec-list",
            ),
            rx.cond(
                veiculo.modificado,
                rx.el.section(
                    rx.el.h2("Modificações"),
                    rx.el.p(
                        "Veículo modificado/preparado. Os detalhes das modificações "
                        "não foram informados."
                    ),
                    class_name="detail-mods",
                ),
            ),
            acao_negociacao(),
            class_name="detail-info",
        ),
        class_name="detail",
    )


def regiao_detalhe() -> rx.Component:
    return rx.el.div(
        rx.match(
            DetalheState.situacao,
            ("encontrado", conteudo_detalhe()),
            (
                "nao_encontrado",
                rx.el.div(
                    rx.el.h1("Veículo não encontrado", class_name="section-title"),
                    rx.el.div(
                        rx.el.p("O veículo procurado não existe ou não está publicado."),
                        voltar_ao_estoque("btn btn-red"),
                        class_name="state-message",
                    ),
                ),
            ),
            (
                "erro",
                rx.el.div(
                    rx.el.p(
                        "Não foi possível carregar o veículo. Verifique sua conexão e tente novamente."
                    ),
                    rx.el.button(
                        "Tentar novamente",
                        type="button",
                        class_name="btn btn-red",
                        on_click=DetalheState.carregar,
                    ),
                    class_name="state-message",
                ),
            ),
            rx.el.p("Carregando veículo…", class_name="state-message"),
        ),
        id="vehicle-region",
        custom_attrs={"aria-live": "polite"},
    )


def pagina_veiculo() -> rx.Component:
    return pagina(
        "",
        rx.el.main(
            rx.el.nav(voltar_ao_estoque(), class_name="detail-back"),
            regiao_detalhe(),
            class_name="catalog vehicle-page",
        ),
    )
