# Design

## Context

Requisitos: ver `specs/contato-vendedor/spec.md`. A documentação descreve a Revaulte como loja, com administrador gerenciando os veículos e contato “com a loja”. O usuário redefiniu a plataforma como marketplace, com anunciantes e contato entre comprador e vendedor. O endpoint de detalhe `GET /vehicles/{vehicle_id}` ainda não existe (etapa B de `detalhes-veiculo`, dependente de autorização).

## Goals / Non-Goals

**Goals:** contato real e autorizado; exposição mínima de dados pessoais; nenhuma tecnologia nova (link `https://wa.me/`).

**Non-Goals:** autocadastro de anunciantes, chat, verificação de número.

## Decisions

### 1. Anunciante como entidade própria

Tabela `seller` no Xano (nome a confirmar): `id`, `created_at`, `display_name`, `whatsapp` (somente dígitos, com DDI e DDD, opcional), `contact_authorized` (bool, padrão falso). `vehicle` ganha `seller_id` opcional (referência a `seller`). Nesta etapa, os anunciantes são cadastrados pelo painel do Xano por um membro do grupo; quando houver cadastro e login, o anunciante passa a ser associado a uma conta.

Alternativa: usar a tabela `user` existente. Adiada: misturaria dados de autenticação com dados públicos antes de existir a Change de cadastro e login.

### 2. Exposição só no detalhe

O endpoint de detalhe inclui `seller: {display_name, whatsapp}` apenas para veículo `available`; `whatsapp` vai nulo quando `contact_authorized` é falso. `GET /vehicles` não muda. Sintaxe de relação e saída condicional a confirmar no Xano Developer MCP e validar com `xano_validate_xanoscript`.

### 3. Link do WhatsApp

`https://wa.me/<número>?text=<mensagem codificada>`, com a mensagem “Olá! Tenho interesse no <título> anunciado na Revaulte: <endereço do anúncio>.”. O link abre em nova aba com `rel="noopener noreferrer"`. O número só aparece no link e no navegador quando autorizado.

## Risks / Trade-offs

- [Mudança de identidade do produto (loja → marketplace)] → atualizar a documentação somente após aprovação do usuário (tarefa 1.1).
- [Número exposto pode receber spam] → exibição só com autorização explícita; o anunciante pode revogar.
- [Dados de teste com contatos inventados] → usar somente contatos reais de pessoas que autorizaram; sem anunciante, a página mostra “contato não disponível”.
- [LGPD] → coleta mínima, finalidade declarada (contato sobre o anúncio) e consentimento registrado em `contact_authorized`.
