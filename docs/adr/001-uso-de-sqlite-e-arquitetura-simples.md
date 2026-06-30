# ADR 001: Adoção de Arquitetura Minimalista e SQLite

## Contexto
O projeto precisa armazenar dados de jogos e histórico de preços capturados por scrapers. Inicialmente, cogitou-se o uso de PostgreSQL + TimescaleDB e filas assíncronas (Celery/Redis).

## Decisão
Optamos por utilizar **SQLite** local (`dados.db`) e extração de dados síncrona/sequencial via `requests` e `BeautifulSoup4`.

## Justificativa (Viés AI-First)
1. **Limitação da Janela de Contexto:** Como o desenvolvimento é guiado por IA, stacks complexas (Docker, Postgres, Mensageria) exigem muitos arquivos de configuração, o que sobrecarrega a janela de contexto e faz a IA "alucinar" (esquecer regras anteriores).
2. **Princípio KISS (Keep It Simple, Stupid):** O SQLite atende perfeitamente à demanda de leitura/escrita do MVP sem adicionar sobrecarga cognitiva à IA.
3. **Alinhamento ao Princípio 4:** "Escolha a ferramenta pela necessidade". A complexidade da solução agora está proporcional à complexidade do problema.

## Consequências
- **Positivas:** Desenvolvimento extremamente ágil, baixo índice de erros da IA, facilidade de rodar o projeto localmente por qualquer avaliador.
- **Negativas:** Não escala para milhões de requisições simultâneas (o que é aceitável para o escopo atual do MVP).