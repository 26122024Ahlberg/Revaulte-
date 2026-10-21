# Proposal

## Why

A Revaulte é um marketplace especializado em carros clássicos, esportivos e modificados, em que cada anúncio tem um anunciante. Na página do veículo, o comprador interessado precisa saber quem anuncia e como falar com essa pessoa por um meio que ela autorizou. Hoje a documentação prevê apenas o “contato com a loja”, sem forma definida (`docs/domain-model.md`, seção 11), e a página do veículo terá só um botão “Tenho interesse” demonstrativo.

## What Changes

- Novo conceito de domínio **Anunciante**: quem anuncia o veículo, com nome de exibição e meio de contato autorizado (inicialmente WhatsApp).
- Cada veículo publicado fica vinculado a um anunciante no Xano.
- Página do veículo Disponível passa a exibir o nome do anunciante e o botão “Conversar no WhatsApp”, que abre o WhatsApp com uma mensagem inicial citando o anúncio. Sem integração com a API do WhatsApp: apenas um link.
- Contato exibido somente quando o anunciante autorizou sua exibição; caso contrário, a página informa que o contato não está disponível.
- Substitui o requisito “Interesse demonstrativo” da Change `detalhes-veiculo`.
- Backend (somente após autorização do usuário): tabela de anunciantes, vínculo do veículo ao anunciante e inclusão dos dados públicos do anunciante no endpoint de detalhe.

### Fora do escopo

- Cadastro do anunciante pelo próprio site, “Anunciar veículo” e “Meus anúncios” (dependem de cadastro e login; Change futura).
- Chat interno (Change `chat-interno`).
- Verificação do número, avaliações e reputação do anunciante.
- Exibição de e-mail, CPF, endereço ou qualquer outro dado pessoal do anunciante.

## Capabilities

### New Capabilities

- `contato-vendedor`: identificação do anunciante e contato autorizado na página do veículo, com os dados públicos do anunciante expostos pelo backend.

### Modified Capabilities

Nenhuma nesta proposta. A `detalhes-veiculo` ainda não foi arquivada; quando for, esta Change ganha um delta MODIFIED que troca o requisito “Interesse demonstrativo” pelo contato do anunciante.

## Impact

- **Domínio e documentação**: `docs/project-overview.md` e `docs/domain-model.md` passam de “loja” para “marketplace com anunciantes” (Anunciante, relação Veículo → Anunciante, Interesse/Contato com o anunciante). Definição de marketplace aprovada pelo usuário em 21/10/2026 e já registrada nos documentos; o detalhamento do Anunciante acompanha esta Change.
- **Backend Xano** (somente após autorização): nova tabela, campo de referência em `vehicle` e alteração do endpoint de detalhe previsto em `detalhes-veiculo` (etapa B). `GET /vehicles` não passa a expor dados do anunciante.
- **Frontend Reflex**: bloco do anunciante na página do veículo.
- **Dados**: os anunciantes e contatos de teste precisam ser pessoas reais que autorizaram a exibição (por exemplo, membros do grupo); nenhum contato é inventado.
- **Dependências**: depois de `detalhes-veiculo` etapa B.
