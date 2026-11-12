# Proposal

## Why

A Home transmite a identidade de marketplace premium com o carrossel fotográfico, mas as páginas internas (Estoque, Usados, Modificados e a página do veículo) têm fundo preto liso e pouca personalidade. Para a apresentação, essas páginas precisam do mesmo nível de acabamento, sem mudar funcionalidades.

## What Changes

- Banner horizontal com fotografia escurecida, título e texto curto no topo de `/estoque`, `/usados` e `/modificados`, com fotos próprias, diferentes das do carrossel da Home, enquadradas na parte direita do banner para o carro não ficar sob o texto.
- Fundo das páginas internas com gradientes em preto e grafite e névoa vermelha atrás da área dos cartões, perceptível sem poluir.
- Cartões das páginas internas com sombra, borda e efeito de passagem do cursor mais elaborados.
- Página do veículo com a própria foto do anúncio desfocada ao fundo, moldura e sombra na foto principal, ficha técnica em blocos e simulador destacado.
- Entrada suave e escalonada das seções, desativada com movimento reduzido.

### Fora do escopo

- Home e carrossel (inalterados, inclusive os cartões de destaque).
- Conteúdo, rotas, pesquisa, filtros, simulador e backend Xano.

## Capabilities

### New Capabilities

- `visual-paginas-internas`: apresentação visual das páginas de estoque e da página do veículo.

### Modified Capabilities

Nenhuma.

## Impact

- **Frontend Reflex**: banner e invólucro das páginas internas em `components.py`; estilos novos em `styles.css`, limitados às páginas internas.
- **Backend Xano**: nenhum.
- **Imagens**: três fotos novas do Pexels (licença “Free”, registradas no `frontend/README.md`): `banner-estoque.jpg` (Alfa Romeo 8C em garagem escura, Quentin Martinez), `banner-usados.jpg` (Chevrolet Nomad clássico de perfil, Jvxhn Visuals) e `banner-modificados.jpg` (Subaru WRX preparado de perfil, Erik Mclean); até 1920 px e menos de 420 KB cada, sem placas legíveis. A página do veículo usa a capa do anúncio.
