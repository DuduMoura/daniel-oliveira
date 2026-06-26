"""
src/scrapers.py

Rotinas de extração de preços de jogos nas 4 lojas de PC suportadas:
Steam, GOG, Epic Games e Nuuvem.

Conforme Spec 01 (docs/specs/01-scraping-pc.md):
- Sem Playwright/Selenium - apenas `requests` + `BeautifulSoup4`.
- Saída sempre normalizada no formato:
  {"jogo": str, "loja": str, "preco": float, "url_compra": str}
"""

import logging
import re
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# User-Agent "de navegador" para reduzir a chance de bloqueio 403 em lojas
# que recusam requisições vindas de clientes não identificados como browser.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}

TIMEOUT = 10  # segundos


def _normalizar(jogo: str, loja: str, preco: float, url_compra: Optional[str]) -> Dict[str, Any]:
    """Garante o formato padrão definido na Spec 01."""
    return {
        "jogo": jogo,
        "loja": loja,
        "preco": round(float(preco), 2),
        "url_compra": url_compra,
    }


# ---------------------------------------------------------------------------
# STEAM
# ---------------------------------------------------------------------------
def scrape_steam(termo: str) -> List[Dict[str, Any]]:
    """
    Busca jogos na Steam via API pública de busca da loja.
    Endpoint: store.steampowered.com/api/storesearch
    """
    url = "https://store.steampowered.com/api/storesearch/"
    params = {"term": termo, "l": "portuguese", "cc": "BR"}

    resultados: List[Dict[str, Any]] = []
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        dados = resp.json()

        for item in dados.get("items", []):
            nome = item.get("name")
            app_id = item.get("id")
            price_info = item.get("price")

            # Jogos free-to-play ou ainda sem preço não trazem o bloco "price"
            if not nome or not price_info:
                continue

            preco_centavos = price_info.get("final")
            if preco_centavos is None:
                continue

            preco = preco_centavos / 100
            link = f"https://store.steampowered.com/app/{app_id}"

            resultados.append(_normalizar(nome, "Steam", preco, link))

    except requests.RequestException as e:
        logger.warning(f"[Steam] Falha na requisição para '{termo}': {e}")
    except (ValueError, KeyError) as e:
        logger.warning(f"[Steam] Falha ao interpretar resposta para '{termo}': {e}")

    return resultados


# ---------------------------------------------------------------------------
# GOG
# ---------------------------------------------------------------------------
def scrape_gog(termo: str) -> List[Dict[str, Any]]:
    """
    Busca jogos na GOG via endpoint público de busca filtrada da loja.
    Endpoint: gog.com/games/ajax/filtered
    """
    url = "https://www.gog.com/games/ajax/filtered"
    params = {"mediaType": "game", "search": termo, "currency": "BRL"}

    resultados: List[Dict[str, Any]] = []
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        dados = resp.json()

        for produto in dados.get("products", []):
            nome = produto.get("title")
            price_info = produto.get("price", {}) or {}

            # 'finalAmount' costuma vir como string, ex.: "59.99"
            preco_str = price_info.get("finalAmount")
            if not nome or preco_str is None:
                continue

            url_jogo = produto.get("url")
            if url_jogo and url_jogo.startswith("/"):
                link = f"https://www.gog.com{url_jogo}"
            else:
                link = url_jogo

            resultados.append(_normalizar(nome, "GOG", float(preco_str), link))

    except requests.RequestException as e:
        logger.warning(f"[GOG] Falha na requisição para '{termo}': {e}")
    except (ValueError, KeyError, TypeError) as e:
        logger.warning(f"[GOG] Falha ao interpretar resposta para '{termo}': {e}")

    return resultados


# ---------------------------------------------------------------------------
# EPIC GAMES
# ---------------------------------------------------------------------------
def scrape_epic(termo: str) -> List[Dict[str, Any]]:
    """
    Busca jogos na Epic Games Store via GraphQL (searchStoreQuery).
    Conforme Spec 01: sem ferramentas de browser; em caso de bloqueio/erro
    a função degrada graciosamente e retorna lista vazia (fallback simples).
    """
    url = "https://www.epicgames.com/graphql"

    query = """
    query searchStoreQuery($keywords: String, $country: String!, $locale: String) {
      Catalog {
        searchStore(keywords: $keywords, country: $country, locale: $locale) {
          elements {
            title
            productSlug
            urlSlug
            price(country: $country) {
              totalPrice {
                discountPrice
                currencyCode
              }
            }
          }
        }
      }
    }
    """

    payload = {
        "query": query,
        "variables": {"keywords": termo, "country": "BR", "locale": "pt-BR"},
    }

    resultados: List[Dict[str, Any]] = []
    try:
        resp = requests.post(url, headers=HEADERS, json=payload, timeout=TIMEOUT)
        resp.raise_for_status()
        dados = resp.json()

        elementos = (
            dados.get("data", {})
            .get("Catalog", {})
            .get("searchStore", {})
            .get("elements", [])
        )

        for item in elementos:
            nome = item.get("title")
            price_block = (item.get("price") or {}).get("totalPrice", {}) or {}
            preco_centavos = price_block.get("discountPrice")

            if not nome or preco_centavos is None:
                continue

            preco = preco_centavos / 100
            slug = item.get("urlSlug") or item.get("productSlug")
            link = f"https://store.epicgames.com/pt-BR/p/{slug}" if slug else url

            resultados.append(_normalizar(nome, "Epic Games", preco, link))

    except requests.RequestException as e:
        logger.warning(f"[Epic] Falha na requisição GraphQL para '{termo}': {e}")
    except (ValueError, KeyError, TypeError) as e:
        logger.warning(f"[Epic] Falha ao interpretar resposta para '{termo}': {e}")

    return resultados


# ---------------------------------------------------------------------------
# NUUVEM
# ---------------------------------------------------------------------------
def scrape_nuuvem(termo: str) -> List[Dict[str, Any]]:
    """
    Busca jogos na Nuuvem via parsing direto do HTML da página de busca
    (não há API pública documentada, conforme Spec 01).

    Atenção: por ser parsing de HTML, os seletores CSS abaixo são os mais
    estáveis observados no layout atual do site, mas podem precisar de
    ajuste caso a Nuuvem mude o front-end.
    """
    url = "https://www.nuuvem.com/br-en/search"
    params = {"q": termo}

    resultados: List[Dict[str, Any]] = []
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=TIMEOUT)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.select("li.product-item")

        for card in cards:
            tag_nome = card.select_one(".product-item--info-title")
            tag_preco = card.select_one(
                ".product-price--value, .product-item--info-prices .price"
            )
            tag_link = card.select_one("a.product-item--link, a")

            if not tag_nome or not tag_preco or not tag_link:
                continue

            nome = tag_nome.get_text(strip=True)
            preco_texto = tag_preco.get_text(strip=True)
            link = tag_link.get("href")

            if link and link.startswith("/"):
                link = f"https://www.nuuvem.com{link}"

            preco = _extrair_preco_brl(preco_texto)
            if preco is None:
                continue

            resultados.append(_normalizar(nome, "Nuuvem", preco, link))

    except requests.RequestException as e:
        logger.warning(f"[Nuuvem] Falha na requisição para '{termo}': {e}")
    except Exception as e:  # parsing de HTML pode falhar de várias formas
        logger.warning(f"[Nuuvem] Falha ao interpretar HTML para '{termo}': {e}")

    return resultados


def _extrair_preco_brl(texto: str) -> Optional[float]:
    """
    Converte texto de preço no formato brasileiro (ex.: 'R$ 79,90')
    para float (79.90). Retorna None se não conseguir extrair um número.
    """
    match = re.search(r"(\d{1,3}(?:\.\d{3})*,\d{2}|\d+,\d{2}|\d+\.\d{2})", texto)
    if not match:
        return None

    valor = match.group(1)
    if "," in valor and "." in valor:
        valor = valor.replace(".", "").replace(",", ".")  # 1.234,56 -> 1234.56
    elif "," in valor:
        valor = valor.replace(",", ".")  # 79,90 -> 79.90

    try:
        return float(valor)
    except ValueError:
        return None
