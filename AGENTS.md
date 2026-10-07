# AGENTS.md — GhostPay

## Contexto obrigatório

Antes de realizar mudanças significativas no projeto, consulte:

- `docs/project-overview.md`
- `docs/domain-model.md`
- `openspec/config.yaml`
- especificações e Changes relevantes existentes em `openspec/`

Não presuma requisitos que não estejam definidos nesses documentos ou na Change atual.

## Processo de desenvolvimento

O GhostPay deve ser desenvolvido incrementalmente utilizando OpenSpec.

Mudanças funcionais ou estruturais relevantes devem ser especificadas antes da implementação.

O fluxo preferencial é:

Explore → Propose → Review → Apply → Verify → Archive

Evite implementar várias funcionalidades independentes em uma única Change.

## Arquitetura e tecnologias

Respeite as tecnologias definidas para o projeto e para a disciplina.

O backend deve utilizar Xano/XanoScript.

Utilize o Xano Developer MCP para consultar documentação e validar XanoScript quando necessário.

Utilize o Xano CLI para operações de sincronização com o ambiente Xano.

Não introduza novas tecnologias, frameworks ou alterações arquiteturais significativas sem justificativa e aprovação.

## Código

- Reutilize estruturas existentes quando adequado.
- Evite duplicação desnecessária.
- Não altere funcionalidades fora do escopo da Change atual sem justificativa.
- Mantenha as mudanças pequenas, compreensíveis e verificáveis.
- Não implemente requisitos indefinidos por suposição.

## Modelo de domínio

Respeite os conceitos e relações definidos em `docs/domain-model.md`.

O modelo de domínio representa conceitos do sistema e não deve ser tratado automaticamente como um esquema físico de banco de dados.

O banco de dados deve evoluir de forma incremental conforme as funcionalidades forem especificadas e implementadas.

## Segurança

- Funcionalidades administrativas devem exigir autorização adequada.
- Autorização deve ser aplicada no backend.
- Dados pessoais e credenciais devem ser tratados de maneira segura.
- Não armazene tokens, senhas ou credenciais sensíveis em arquivos versionados.
- Não conceda permissões desnecessárias a ferramentas ou integrações.

## Verificação

Toda mudança funcional deve possuir uma estratégia de verificação.

Antes de considerar uma implementação concluída:

- revise as alterações realizadas;
- verifique se correspondem à especificação;
- execute validações relevantes;
- consulte erros e diagnósticos disponíveis;
- revise o `git diff` quando aplicável.

## Xano

Não presuma sintaxe ou comportamento do Xano/XanoScript quando houver dúvida.

Priorize a documentação oficial e o Xano Developer MCP para confirmar sintaxe, recursos e comportamentos.

O Xano Developer MCP auxilia com documentação e validação; ele não substitui o Xano CLI para sincronização com o workspace.

## Idioma

Documentação do projeto, artefatos OpenSpec e explicações relacionadas ao projeto devem ser escritos em português brasileiro, salvo quando nomes técnicos, comandos ou código exigirem outro idioma.