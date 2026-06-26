# Plano de Execução 02: Motor de Scraping

## Objetivo
Criar os scripts que farão a extração de preços (Steam, Epic, Nuuvem, GOG), normalizarão os dados e salvarão no banco de dados SQLite existente.

## Contexto Necessário para a IA
- Arquivo de leitura obrigatória: `docs/specs/01-scraping-pc.md`.
- Os scrapers devem reutilizar as funções de inserção do arquivo `src/database.py` e os modelos do `src/models.py` criados na Fase 1.

## Checklist de Implementação (Passo a Passo)

- [ ] **Passo 1: Lógica de Extração (`src/scrapers.py`)**
  - Criar funções separadas para extrair dados das 4 lojas usando `requests` e `BeautifulSoup`.
  - `scrape_steam(termo)`: Buscar via API pública da Steam.
  - `scrape_gog(termo)`: Buscar via API pública da GOG.
  - `scrape_nuuvem(termo)`: Buscar via HTML parsing (BeautifulSoup).
  - `scrape_epic(termo)`: Buscar via API/GraphQL da Epic (ou fallback simples se for complexo).

- [ ] **Passo 2: Normalização dos Dados**
  - Todas as funções de scraping devem retornar uma lista de dicionários no formato padronizado: `{"jogo": str, "loja": str, "preco": float, "url_compra": str}`.

- [ ] **Passo 3: Orquestrador (`src/atualizar_precos.py`)**
  - Criar um script principal que recebe o nome de um jogo, chama os 4 scrapers simultaneamente (ou sequencialmente).
  - Pega os resultados normalizados e salva no banco de dados chamando as funções do `database.py`.