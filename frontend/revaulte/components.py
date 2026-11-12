# Componentes da interface: topo e menu, rodapé, cartão, selos e mensagens de estado.
import reflex as rx

from .state import (
    IMAGEM_PROVISORIA,
    CarrosselState,
    CartaoVeiculo,
    CatalogState,
    DetalheState,
    GrupoModificacoes,
    MenuState,
    OPCOES_PARCELAS,
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


def indicador_carregamento(texto: str) -> rx.Component:
    """Estado de carregamento: anel animado (decorativo) e texto lido pelos leitores de tela."""
    return rx.el.p(
        rx.el.span(class_name="spinner", custom_attrs={"aria-hidden": "true"}),
        rx.el.span(texto),
        class_name="state-message is-loading",
    )


# Filtros oferecidos em cada página de estoque; o recorte fixo da página já cobre o outro.
FILTROS_POR_PAGINA = {
    ROTA_ESTOQUE: ("condicao", "modificacao"),
    ROTA_USADOS: ("modificacao",),
    ROTA_MODIFICADOS: ("condicao",),
}


def filtro_select(id_campo: str, rotulo: str, valor, ao_mudar, opcoes) -> rx.Component:
    return rx.el.div(
        rx.el.label(rotulo, html_for=id_campo),
        rx.el.select(
            *(rx.el.option(texto, value=chave) for chave, texto in opcoes),
            id=id_campo,
            value=valor,
            on_change=ao_mudar,
        ),
        class_name="filter-field",
    )


def barra_filtros(filtros: tuple[str, ...]) -> rx.Component:
    """Pesquisa por marca, modelo e versão e os filtros da página."""
    campos = [
        rx.el.div(
            rx.el.label("Pesquisar", html_for="busca-estoque"),
            rx.debounce_input(
                rx.el.input(
                    id="busca-estoque",
                    type="search",
                    placeholder="Marca, modelo ou versão",
                    auto_complete="off",
                    value=CatalogState.busca,
                    on_change=CatalogState.definir_busca,
                ),
                debounce_timeout=300,
            ),
            class_name="filter-field filter-search",
        )
    ]
    if "condicao" in filtros:
        campos.append(
            filtro_select(
                "filtro-condicao", "Condição", CatalogState.filtro_condicao,
                CatalogState.definir_condicao,
                (("todos", "Todos"), ("novo", "Novo"), ("usado", "Usado")),
            )
        )
    if "modificacao" in filtros:
        campos.append(
            filtro_select(
                "filtro-modificacao", "Modificação", CatalogState.filtro_modificacao,
                CatalogState.definir_modificacao,
                (("todos", "Todos"), ("modificados", "Modificados"), ("originais", "Originais")),
            )
        )
    return rx.el.div(
        rx.el.div(*campos, class_name="filter-fields"),
        rx.el.div(
            rx.el.p(
                CatalogState.total_exibido,
                class_name="filter-count",
                custom_attrs={"aria-live": "polite"},
            ),
            rx.cond(
                CatalogState.filtros_ativos,
                rx.el.button(
                    "Limpar filtros",
                    type="button",
                    class_name="link-clear",
                    on_click=CatalogState.limpar_filtros,
                ),
            ),
            class_name="filter-footer",
        ),
        class_name="filters",
        role="search",
        custom_attrs={"aria-label": "Pesquisar no estoque"},
    )


def sem_resultado() -> rx.Component:
    return rx.el.div(
        rx.el.p("Nenhum veículo corresponde aos critérios de pesquisa."),
        rx.el.button(
            "Limpar filtros",
            type="button",
            class_name="btn btn-red",
            on_click=CatalogState.limpar_filtros,
        ),
        class_name="state-message",
    )


def regiao_estoque(mensagem_vazio: str) -> rx.Component:
    """Região das páginas de estoque: exibe somente um dos estados carregando, lista,
    vazio ou erro. A lista mostra o recorte da página com a pesquisa e os filtros."""
    vazio = rx.el.p(mensagem_vazio, class_name="state-message")
    return rx.el.div(
        rx.match(
            CatalogState.situacao,
            (
                "lista",
                rx.cond(
                    CatalogState.cartoes_exibidos.length() > 0,
                    grade_cartoes(CatalogState.cartoes_exibidos),
                    rx.cond(CatalogState.filtros_ativos, sem_resultado(), vazio),
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
            indicador_carregamento("Carregando veículos…"),
        ),
        id="catalog-region",
        custom_attrs={"aria-live": "polite"},
    )


# Banner de cada página de estoque: fotos próprias, diferentes das da Home (Pexels,
# licença registrada em frontend/README.md). A chave define o ajuste de enquadramento
# no CSS (classe "page-banner is-<chave>").
BANNERS_ESTOQUE = {
    ROTA_ESTOQUE: (
        "/banner-estoque.jpg",
        "Todos os veículos anunciados na Revaulte: clássicos, esportivos, raros e preparados.",
        "estoque",
    ),
    ROTA_USADOS: (
        "/banner-usados.jpg",
        "Veículos com história, com ano, quilometragem e condição informados em cada anúncio.",
        "usados",
    ),
    ROTA_MODIFICADOS: (
        "/banner-modificados.jpg",
        "Carros modificados e preparados, identificados em cada anúncio.",
        "modificados",
    ),
}


def banner_interno(atual: str, titulo: str) -> rx.Component:
    """Banner horizontal das páginas de estoque; a foto é decorativa (alt vazio)."""
    imagem, texto, chave = BANNERS_ESTOQUE.get(atual, BANNERS_ESTOQUE[ROTA_ESTOQUE])
    return rx.el.section(
        rx.el.img(src=imagem, alt="", class_name="page-banner-image", custom_attrs={"aria-hidden": "true"}),
        rx.el.div(class_name="page-banner-shade", custom_attrs={"aria-hidden": "true"}),
        rx.el.div(
            rx.el.p("Marketplace Revaulte", class_name="hero-kicker"),
            rx.el.h1(titulo, class_name="page-banner-title"),
            rx.el.p(texto, class_name="page-banner-text"),
            class_name="page-banner-content",
        ),
        class_name=f"page-banner is-{chave}",
    )


def pagina_estoque(atual: str, titulo: str, mensagem_vazio: str) -> rx.Component:
    """Página de estoque (/estoque, /usados ou /modificados)."""
    return pagina(
        atual,
        rx.el.div(
            banner_interno(atual, titulo),
            rx.el.main(
                # Pesquisa e filtros só depois que a lista foi carregada com sucesso.
                rx.cond(
                    CatalogState.situacao == "lista",
                    barra_filtros(FILTROS_POR_PAGINA.get(atual, ("condicao", "modificacao"))),
                ),
                regiao_estoque(mensagem_vazio),
                class_name="catalog",
            ),
            class_name="inner-page",
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
# Página individual do veículo (/veiculo/<id>), Change detalhes-veiculo.
# ---------------------------------------------------------------------------

MENSAGEM_SEM_CONTATO = "Contato não disponível"
TEXTO_NAO_INFORMADO = "Não informado"
MENSAGEM_SEM_DESCRICAO = "Descrição não informada."
MENSAGEM_SEM_MODIFICACOES = (
    "Veículo modificado/preparado. Os detalhes das modificações não foram informados."
)


def voltar_ao_estoque(classe: str = "link-back") -> rx.Component:
    return rx.el.a("← Voltar ao estoque", href=ROTA_ESTOQUE, class_name=classe)


def item_ficha(rotulo: str, valor: rx.Var[str]) -> rx.Component:
    return rx.el.div(rx.el.dt(rotulo), rx.el.dd(valor), class_name="spec-item")


def item_tecnico(rotulo: str, valor: rx.Var[str]) -> rx.Component:
    """Item da configuração original: o valor cadastrado ou “Não informado”, discreto."""
    return rx.el.div(
        rx.el.dt(rotulo),
        rx.el.dd(
            rx.cond(valor != "", valor, rx.el.span(TEXTO_NAO_INFORMADO, class_name="value-missing"))
        ),
        class_name="spec-item",
    )


def configuracao_original() -> rx.Component:
    veiculo = DetalheState.veiculo
    return rx.el.section(
        rx.el.h2("Configuração original", class_name="detail-subtitle"),
        rx.el.dl(
            item_tecnico("Cor", veiculo.cor),
            item_tecnico("Motorização", veiculo.motorizacao),
            item_tecnico("Câmbio", veiculo.cambio),
            class_name="spec-list",
        ),
        class_name="detail-original",
    )


def secao_descricao() -> rx.Component:
    descricao = DetalheState.veiculo.descricao
    return rx.el.section(
        rx.el.h2("Descrição", class_name="detail-panel-title"),
        rx.cond(
            descricao != "",
            rx.el.p(descricao, class_name="detail-description"),
            rx.el.p(MENSAGEM_SEM_DESCRICAO, class_name="value-missing"),
        ),
        class_name="detail-panel",
    )


def grupo_modificacoes(grupo: rx.Var[GrupoModificacoes]) -> rx.Component:
    return rx.el.div(
        rx.el.h3(grupo.area, class_name="mod-area"),
        rx.el.ul(rx.foreach(grupo.itens, lambda item: rx.el.li(item)), class_name="mod-items"),
        class_name="mod-group",
    )


def secao_modificacoes() -> rx.Component:
    """Modificações cadastradas, por área; só existe para veículo indicado como modificado."""
    modificacoes = DetalheState.veiculo.modificacoes
    return rx.el.section(
        rx.el.h2("Modificações e preparação", class_name="detail-panel-title"),
        rx.cond(
            modificacoes.length() > 0,
            rx.el.div(rx.foreach(modificacoes, grupo_modificacoes), class_name="mod-groups"),
            rx.el.p(MENSAGEM_SEM_MODIFICACOES, class_name="value-missing"),
        ),
        class_name="detail-panel detail-mods",
    )


def secoes_detalhe() -> rx.Component:
    """Descrição e modificações, abaixo da ficha e separadas da configuração original."""
    return rx.el.div(
        secao_descricao(),
        rx.cond(DetalheState.veiculo.modificado, secao_modificacoes()),
        class_name=rx.cond(
            DetalheState.veiculo.modificado, "detail-sections", "detail-sections is-single"
        ),
    )


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


def bloco_anunciante() -> rx.Component:
    """Anunciante do veículo Disponível; o WhatsApp só aparece com contato autorizado e válido."""
    veiculo = DetalheState.veiculo
    return rx.el.section(
        rx.cond(
            veiculo.anunciante != "",
            rx.el.p(
                rx.el.span("Anunciado por", class_name="seller-label"),
                rx.el.strong(veiculo.anunciante, class_name="seller-name"),
                class_name="seller-id",
            ),
        ),
        rx.cond(
            veiculo.link_whatsapp != "",
            rx.el.a(
                "Conversar no WhatsApp",
                href=veiculo.link_whatsapp,
                target="_blank",
                rel="noopener noreferrer",
                class_name="btn btn-red btn-whatsapp",
            ),
            rx.el.p(MENSAGEM_SEM_CONTATO, class_name="value-missing seller-unavailable"),
        ),
        class_name="detail-actions seller-box",
        custom_attrs={"aria-label": "Contato com o anunciante"},
    )


def acao_negociacao() -> rx.Component:
    """Vendido: aviso de indisponibilidade, sem contato. Disponível: bloco do anunciante."""
    return rx.cond(
        DetalheState.veiculo.vendido,
        rx.el.p(
            "Este veículo já foi vendido e está indisponível para negociação.",
            class_name="detail-notice",
        ),
        bloco_anunciante(),
    )


AVISO_SIMULACAO = (
    "Simulação hipotética, com taxa ilustrativa. Não inclui impostos, tarifas e seguros "
    "e não representa proposta, aprovação ou contratação de crédito."
)


def campo_simulador(id_campo: str, rotulo: str, valor, ao_mudar, prefixo: str, sufixo: str = "") -> rx.Component:
    return rx.el.div(
        rx.el.label(rotulo, html_for=id_campo),
        rx.el.div(
            rx.el.span(prefixo, class_name="sim-affix", custom_attrs={"aria-hidden": "true"}) if prefixo else rx.fragment(),
            # Debounce: o valor vai ao servidor após uma pausa curta na digitação.
            rx.debounce_input(
                rx.el.input(
                    id=id_campo,
                    type="text",
                    input_mode="decimal",
                    auto_complete="off",
                    value=valor,
                    on_change=ao_mudar,
                ),
                debounce_timeout=300,
            ),
            rx.el.span(sufixo, class_name="sim-affix", custom_attrs={"aria-hidden": "true"}) if sufixo else rx.fragment(),
            class_name="sim-input",
        ),
        class_name="sim-field",
    )


def opcao_parcelas(n: int) -> rx.Component:
    ativo = DetalheState.parcelas == n
    return rx.el.button(
        f"{n}x",
        type="button",
        class_name=rx.cond(ativo, "sim-term is-active", "sim-term"),
        on_click=DetalheState.definir_parcelas(n),
        custom_attrs={"aria-pressed": rx.cond(ativo, "true", "false"), "aria-label": f"{n} parcelas"},
    )


def linha_resultado(rotulo: str, valor) -> rx.Component:
    return rx.el.div(rx.el.dt(rotulo), rx.el.dd(valor), class_name="spec-item")


def secao_simulador() -> rx.Component:
    """Simulação informativa (Tabela Price), somente para veículo Disponível."""
    sim = DetalheState.simulacao
    return rx.el.section(
        rx.el.h2("Simular financiamento", class_name="section-title"),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.span("Valor do veículo", class_name="sim-label"),
                    rx.el.strong(DetalheState.veiculo.preco, class_name="sim-price"),
                    class_name="sim-field",
                ),
                campo_simulador("sim-entrada", "Entrada", DetalheState.entrada_texto, DetalheState.definir_entrada, "R$"),
                rx.el.fieldset(
                    rx.el.legend("Prazo"),
                    rx.el.div(*(opcao_parcelas(n) for n in OPCOES_PARCELAS), class_name="sim-terms"),
                    class_name="sim-field",
                ),
                campo_simulador(
                    "sim-taxa", "Taxa de juros ilustrativa (ao mês)", DetalheState.taxa_texto,
                    DetalheState.definir_taxa, "", "%",
                ),
                class_name="sim-form",
            ),
            rx.el.div(
                rx.cond(
                    sim.erro != "",
                    rx.el.p(sim.erro, class_name="sim-error"),
                    rx.el.div(
                        rx.el.p("Parcela estimada", class_name="sim-label"),
                        rx.el.p(
                            DetalheState.parcelas.to_string() + "x de ",
                            rx.el.strong(sim.parcela),
                            class_name="sim-installment",
                        ),
                        rx.el.dl(
                            linha_resultado("Entrada", sim.entrada),
                            linha_resultado("Valor financiado", sim.financiado),
                            linha_resultado("Total pago", sim.total),
                            linha_resultado("Total de juros", sim.juros),
                            class_name="spec-list",
                        ),
                    ),
                ),
                rx.el.p(AVISO_SIMULACAO, class_name="sim-notice"),
                class_name="sim-result",
                custom_attrs={"aria-live": "polite"},
            ),
            class_name="sim-grid",
        ),
        class_name="simulator",
        custom_attrs={"aria-label": "Simulador de financiamento"},
    )


def conteudo_detalhe() -> rx.Component:
    return rx.fragment(
        ficha_detalhe(),
        secoes_detalhe(),
        rx.cond(~DetalheState.veiculo.vendido, secao_simulador()),
    )


def ficha_detalhe() -> rx.Component:
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
            configuracao_original(),
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
            indicador_carregamento("Carregando veículo…"),
        ),
        id="vehicle-region",
        custom_attrs={"aria-live": "polite"},
    )


def fundo_veiculo() -> rx.Component:
    """A própria foto do anúncio, desfocada, ao fundo do topo da página (decorativa)."""
    capa = DetalheState.veiculo.capa
    return rx.cond(
        (DetalheState.situacao == "encontrado") & (capa != IMAGEM_PROVISORIA),
        rx.el.img(src=capa, alt="", class_name="vehicle-backdrop", custom_attrs={"aria-hidden": "true"}),
    )


def pagina_veiculo() -> rx.Component:
    return pagina(
        "",
        rx.el.div(
            fundo_veiculo(),
            rx.el.main(
                rx.el.nav(voltar_ao_estoque(), class_name="detail-back"),
                regiao_detalhe(),
                class_name="catalog vehicle-page",
            ),
            class_name="inner-page inner-vehicle",
        ),
    )
