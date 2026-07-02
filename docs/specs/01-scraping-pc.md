# Spec 01: Extração de Dados (Scraping de Lojas de PC)

## 1. Objetivo
Criar rotinas simples de extração de dados para buscar os preços dos jogos e suas capas exclusivamente nas 4 principais lojas de PC do Brasil: Steam, Epic Games, Nuuvem e GOG.

## 2. Abordagem Tecnológica Minimalista
* **Linguagem:** Python
* **Bibliotecas:** `requests` para baixar as páginas/APIs e `BeautifulSoup4` para ler o HTML estático.
* **Complexidade reduzida:** Sem uso de ferramentas pesadas de simulação de navegador (como Playwright ou Selenium) para manter a execução rápida e simples.

## 3. Lojas e Estratégia de Captura
* **Steam:** Utilizar a API oficial pública (`store.steampowered.com/api/storesearch/`).
* **GOG:** Utilizar a API de catálogo moderna (`catalog.gog.com/v1/catalog`) com o prefixo de busca `like:` para contornar bloqueios de filtro.
* **Epic Games:** Realizar requisições diretas no endpoint GraphQL, exigindo cabeçalhos AJAX (`XMLHttpRequest`) e formato JSON rigoroso para evitar bloqueio (Erro 400).
* **Nuuvem:** Fazer o parsing direto do HTML da página de busca (`/catalog/page/1/search/`) usando BeautifulSoup.

## 4. Normalização de Dados
Independente da loja, o script de extração deve retornar sempre um formato simples padronizado, contendo também a URL da imagem (thumbnail) do jogo. 

O formato de saída final deve ser:
`{ "jogo": "Nome", "capa": "https://url-da-imagem.jpg", "loja": "Steam", "preco": 199.90, "url_compra": "https://url-da-loja.com" }`