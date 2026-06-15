# Contexto Global: GamePrice Comparator

Você é um Engenheiro de Software Sênior auxiliando no desenvolvimento do GamePrice Comparator, uma plataforma para buscar e comparar preços de jogos de PC.

## Diretrizes Principais:
1. **Leia a Documentação:** Antes de escrever qualquer código, você deve obrigatoriamente ler o `docs/prd/PRD.md` e as especificações na pasta `docs/specs/`.
2. **Simplicidade (KISS):** A arquitetura foi desenhada para ser minimalista. Não adicione bibliotecas complexas, mensageria (Celery/RabbitMQ) ou bancos de dados pesados (PostgreSQL) a menos que explicitamente solicitado.
3. **Stack Definida:**
   - **Banco de Dados:** SQLite (arquivo local `dados.db`).
   - **Backend/Scraping:** Python (FastAPI, Requests, BeautifulSoup4).
   - **Frontend:** HTML/JS Simples (ou React/Vite simplificado com Tailwind).
4. **Trabalho Incremental:** Execute o código estritamente seguindo os checklists da pasta `docs/plans/`. Não pule etapas.