# Proposal

## Why

Hoje a raiz do site redireciona direto para o estoque: não há uma página que apresente a Revaulte. Para a apresentação do MVP, a primeira impressão precisa comunicar a especialidade da loja (carros antigos, clássicos, esportivos e modificados/preparados) e levar o visitante aos veículos reais.

## What Changes

- Página inicial em `/`, substituindo a página inicial provisória criada pela Change `navegacao-principal`.
- Banner principal (hero) em carrossel com 3 slides (esportivo, modificado e clássico), cada um com foto horizontal e frase de impacto, setas e indicadores para troca manual e o botão “Explorar estoque” para `/estoque`.
- Seção “Veículos em destaque” com os 3 veículos Disponíveis mais recentes vindos do Xano, nos mesmos cartões do catálogo, e link para o estoque completo.
- Seção sobre a proposta da Revaulte (especialização em antigos, clássicos, esportivos e preparados), sem afirmar serviços ou garantias ainda não definidos.
- Estados de carregamento, falha e ausência de destaques na seção de destaques, sem veículos fictícios.
- Animações leves de entrada no banner e nas seções da Home, desativadas para quem prefere movimento reduzido.

### Fora do escopo

- Campo ou critério administrativo de destaque (`is_featured`); o critério adotado é “os 3 Disponíveis mais recentes”.
- Rotação automática dos slides, financiamento e contato. As animações das demais páginas continuam na Change `animacoes-interface`.
- Alterações no backend Xano.

## Capabilities

### New Capabilities

- `pagina-inicial`: conteúdo e comportamento da página inicial, incluindo banner, destaques e seção de proposta.

### Modified Capabilities

- `navegacao-site`: remove o requisito “Página inicial provisória”, substituído pela página inicial completa.

## Impact

- **Frontend Reflex**: página `/` em `revaulte.py`, componentes do banner e das seções em `components.py`, recorte de destaques no `CatalogState`, novos estilos em `styles.css` e as três imagens do carrossel em `frontend/assets/` (fotos do Pexels, licença registrada no `frontend/README.md`).
- **Backend Xano**: nenhum; reutiliza `GET /vehicles` (já ordenado do mais recente para o mais antigo).
- **Documentação**: registrar em `docs/project-overview.md` e `docs/domain-model.md` o critério de destaque adotado.
- **Dependências**: depois de `navegacao-principal` (rota `/estoque` e menu).
