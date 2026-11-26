# Design

## Decisões

1. **Lista no frontend, sem esquema novo.** A constante `IDS_DESTAQUES = (4, 5, 6)` em `frontend/revaulte/state.py` define o conjunto editorial. Evita alterar o esquema do Xano, os onze campos públicos do catálogo (spec `catalogo-publico`) e os registros dos veículos originais. Contrapartida: mudar os destaques exige alterar o código.
2. **Regra.** Dada a lista do catálogo (já do mais recente para o mais antigo): (a) selecionar os Disponíveis cujo id está em `IDS_DESTAQUES`, na ordem da lista; (b) completar até três com os Disponíveis que não estão em `IDS_DESTAQUES`, também na ordem da lista; (c) cortar em três. Vendidos nunca entram.
3. **Compatibilidade.** `aplicar_recorte` ganha o parâmetro opcional `ids_destaque` (padrão `IDS_DESTAQUES`), usado só pelo recorte `destaques`; os demais recortes e a ordenação do Estoque ficam intactos. Os testes injetam `ids_destaque` para não depender dos identificadores reais.
4. **Datas reais.** Os veículos novos entram com `created_at` real (mais recente que os originais); por isso passam a aparecer primeiro no Estoque, que continua do mais novo para o mais antigo.
5. **Veículo 7.** É Rascunho, nunca vem do catálogo público e não participa.

## Riscos

- Os identificadores 4, 5 e 6 são específicos desta instalação do Xano; em outro banco, a regra cai no comportamento atual (completar com os mais recentes).

## Verificação

Testes unitários de `aplicar_recorte` (três presentes, um indisponível, ausentes e lista vazia), suíte completa e `reflex compile --dry`. Verificação no navegador depois da inserção dos veículos novos: a Home deve continuar mostrando 6, 5 e 4.
