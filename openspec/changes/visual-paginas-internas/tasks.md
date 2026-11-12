# Tasks

## 1. Implementação

- [x] 1.1 Criar em `components.py` o banner das páginas de estoque e o invólucro `inner-page`, e na página do veículo o fundo com a capa desfocada; verificar com testes em `frontend/tests/` (um único `h1` por página de estoque, fotos próprias diferentes das da Home e com menos de 420 KB, Home sem as novas classes)
- [ ] 1.2 Acrescentar em `styles.css` os gradientes, os cartões, a página do veículo, o simulador e as entradas escalonadas, limitados às páginas internas; verificar no Safari em desktop e 375 px, sem rolagem horizontal e com “Reduzir movimento” — implementado; durações dentro do limite de 0,4 s da Change `animacoes-interface`; desfoque mais leve no celular; desktop confirmado pelo usuário no Safari (desktop) em 27/10/2026; pendente 375 px, rolagem horizontal e “Reduzir movimento”

## 2. Verificação

- [x] 2.1 Executar os testes, `reflex compile` e `openspec validate visual-paginas-internas --strict`; verificar que passam e que a Home, `xano/` e `frontend-html/` não foram alterados — verificado em 21/10/2026 na auditoria: testes, compilação e validação passam; nenhuma função da Home mudou e as regras novas valem só para `.inner-page`, `.page-banner`, `.vehicle-backdrop` e `.inner-vehicle`; `xano/` e `frontend-html/` sem alterações
