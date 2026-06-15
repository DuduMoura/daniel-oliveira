# Plano de Execução 01: Setup, Banco e Backend Básico

## Objetivo
Inicializar o projeto, configurar o banco de dados SQLite e criar a estrutura base da API FastAPI (atendendo às Specs 02 e 03).

## Contexto Necessário para a IA
- Arquivos de leitura obrigatória antes de executar: `docs/specs/02-armazenamento-simples.md` e `docs/specs/03-backend-api.md`.

## Checklist de Implementação (Passo a Passo)

- [ ] **Passo 1: Setup do Ambiente Python**
  - Criar ambiente virtual (`venv`).
  - Criar arquivo `requirements.txt` com as dependências básicas: `fastapi`, `uvicorn`, `requests`, `beautifulsoup4`.
  - Criar a pasta `src/` para conter o código-fonte.

- [ ] **Passo 2: Banco de Dados (`src/database.py`)**
  - Criar a conexão com o SQLite local (`dados.db`).
  - Criar uma função de inicialização (`init_db`) que crie as tabelas `jogos` e `precos` caso não existam.

- [ ] **Passo 3: Modelos de Dados (`src/models.py`)**
  - Criar as classes (ex: Pydantic) para padronizar os dados de entrada e saída (Jogo, Oferta).

- [ ] **Passo 4: API Básica (`src/main.py`)**
  - Inicializar a aplicação FastAPI.
  - Criar o endpoint `GET /api/search` (mesmo que inicialmente retornando dados fictícios apenas para testar a rota).
  - Criar o endpoint `GET /api/prices/{id_jogo}`.