# Design

## Context

Requisitos: ver `specs/contato-vendedor/spec.md`. A documentação descreve a Revaulte como loja, com administrador gerenciando os veículos e contato “com a loja”. O usuário redefiniu a plataforma como marketplace, com anunciantes e contato entre comprador e vendedor. O endpoint de detalhe `GET /vehicles/{vehicle_id}` existe desde 07/11/2026 (etapa B de `detalhes-veiculo`) e esta Change o amplia.

## Goals / Non-Goals

**Goals:** contato real e autorizado; exposição mínima de dados pessoais; nenhuma tecnologia nova (link `https://wa.me/`).

**Non-Goals:** autocadastro de anunciantes, chat, verificação de número.

## Decisions

### 1. Anunciante como entidade própria

Tabela `seller` no Xano (aprovada pelo usuário em 27/10/2026): `id`, `created_at`, `display_name`, `whatsapp` (somente dígitos, com DDI e DDD, opcional, marcado como `sensitive`), `contact_authorized` (bool, padrão falso) e `contact_authorized_at` (timestamp opcional, data da autorização, registro de consentimento para a LGPD; nunca exposto). `vehicle` ganha `seller_id` opcional (referência a `seller`). Nesta etapa, os anunciantes são cadastrados pelo painel do Xano por um membro do grupo; quando houver cadastro e login, o anunciante passa a ser associado a uma conta.

Alternativa: usar a tabela `user` existente. Adiada: misturaria dados de autenticação com dados públicos antes de existir a Change de cadastro e login.

### 2. Exposição só no detalhe

O endpoint de detalhe inclui `seller: {display_name, whatsapp}` apenas para veículo `available`; `whatsapp` vai nulo quando `contact_authorized` é falso. Veículo vendido ou sem anunciante recebe `seller` nulo. `seller_id`, `contact_authorized` e `contact_authorized_at` são removidos da resposta (`|unset:"seller_id"`); a decisão é tomada no backend, e o número nunca chega ao navegador sem autorização. `GET /vehicles` não muda, pois a sua lista de campos é explícita. Refeito em `xano/` em 07/11/2026 e validado com `xano_validate_xanoscript`: `output` de `vehicle` inclui `seller_id`; só se `status == "available"` e `seller_id != null` o anunciante é lido (`db.query seller` com `return = {type: "single"}` e `output` com `display_name`, `whatsapp`, `contact_authorized`); `whatsapp` só é copiado quando `contact_authorized == true` e o número não é vazio; a resposta é `$vehicle|unset:"seller_id"|set:"modifications":...|set:"seller":$seller`, em que `seller` é `{display_name, whatsapp}` ou nulo. `vehicle` ganha índice em `seller_id`; `whatsapp` e `contact_authorized_at` são `sensitive`.

### 3. Link do WhatsApp

`https://wa.me/<número>?text=<mensagem codificada>`, com a mensagem “Olá! Tenho interesse no <título> <ano> anunciado na Revaulte.”. Decisão do usuário em 07/11/2026: sem endereço do anúncio e nunca `localhost`; o endereço entra quando houver domínio público, em Change futura. O link abre em nova aba com `rel="noopener noreferrer"`. O número só aparece no link e no navegador quando autorizado. O frontend monta o link somente se o número tiver de 12 a 13 dígitos ASCII, o anunciante tiver nome e o veículo não estiver vendido (conferência repetida no frontend, além do backend); caso contrário, exibe “Contato não disponível”.

### 3a. Bloco “Anunciado por” no lugar do interesse demonstrativo

Aprovado pelo usuário em 07/11/2026: o botão demonstrativo “Tenho interesse” de `detalhes-veiculo` é removido. Veículo Disponível exibe o bloco “Anunciado por” (nome, quando há anunciante) com “Conversar no WhatsApp” ou “Contato não disponível”; Vendido mantém o aviso de indisponibilidade, sem contato. O requisito “Interesse demonstrativo” de `detalhes-veiculo` recebe o delta MODIFIED no arquivamento (tarefa 4.1).

### 4. Ordem de implementação e dados de teste

Aprovado pelo usuário em 27/10/2026: esta Change é implementada depois de concluída e testada a etapa B de `detalhes-veiculo`, com cópia de segurança, prévia `--dry-run` e envio parcial sem `--sync`/`--delete`, como naquela Change. Não há anunciantes reais autorizados no momento: nenhum anunciante é cadastrado no Xano, os veículos existentes ficam com `seller_id` nulo e a verificação no Xano cobre o caso “contato não disponível”. Os casos com anunciante e contato autorizado são cobertos por testes automatizados com dados simulados, que existem só nos testes.

## Risks / Trade-offs

- [Mudança de identidade do produto (loja → marketplace)] → atualizar a documentação somente após aprovação do usuário (tarefa 1.1).
- [Número exposto pode receber spam] → exibição só com autorização explícita; o anunciante pode revogar.
- [Dados de teste com contatos inventados] → usar somente contatos reais de pessoas que autorizaram; sem anunciante, a página mostra “contato não disponível”.
- [LGPD] → coleta mínima, finalidade declarada (contato sobre o anúncio) e consentimento registrado em `contact_authorized` e `contact_authorized_at`.
