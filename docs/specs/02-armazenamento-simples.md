# Spec 02: Armazenamento Local e Minimalista

## 1. Objetivo
Garantir que as buscas sejam instantâneas e permitir a criação do gráfico de "Histórico de Preços", sem a necessidade de infraestrutura complexa ou servidores de banco de dados externos.

## 2. Abordagem Tecnológica Minimalista
* **Tecnologia:** SQLite
* **Por que?** O SQLite é um banco de dados embutido, que funciona como um simples arquivo local (`dados.db`). Não requer instalação (ex: Docker, PostgreSQL) e é perfeitamente compreendido pela IA.

## 3. Estrutura das Tabelas (Esquema Simples)
O banco precisará de apenas duas tabelas básicas:
* **Tabela `jogos`:** Guarda apenas o nome canônico do jogo e a URL da capa (thumbnail).
* **Tabela `precos`:** Guarda os registros diários. Colunas: `id_jogo`, `loja`, `preco`, `data_captura`, `url_compra`.

## 4. Estratégia de Atualização (Sem ferramentas complexas)
Em vez de usar agendadores pesados como Celery/Redis, a atualização dos preços será feita por um script Python simples (`atualizar_precos.py`) que pode ser executado manualmente ou automatizado via Cron Job do sistema operacional ou GitHub Actions.