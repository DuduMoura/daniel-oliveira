import logging
import re
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}

TIMEOUT = 10

def _normalizar(jogo: str, loja: str, preco: float, url_compra: Optional[str]) -> Dict[str, Any]:
    return {
        "jogo": jogo,
        "loja": loja,
        "preco": round(float(preco), 2),
        "url_compra": url_compra,
    }

def scrape_steam(termo: str) -> List[Dict[str, Any]]:
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
            if not nome or not price_info:
                continue
            preco_centavos = price_info.get("final")
            if preco_centavos is None:
                continue
            preco = preco_centavos / 100
            link = f"https://store.steampowered.com/app/{app_id}"
            resultados.append(_normalizar(nome, "Steam", preco, link))
    except (requests.RequestException, ValueError, KeyError):
        pass
    return resultados

# ---------------------------------------------------------------------------
# GOG - DEFINITIVA (Padrão 'like:' sem filtros restritivos)
# ---------------------------------------------------------------------------
def scrape_gog(termo: str) -> List[Dict[str, Any]]:
    """
    Busca jogos na GOG usando o prefixo 'like:' sem parâmetros de região.
    Isso evita o bug de filtro da API que zerava resultados.
    """
    url = "https://catalog.gog.com/v1/catalog"
    
    # O diagnóstico provou que 'like:' é o prefixo necessário e que
    # os parâmetros de região/moeda quebram a consulta.
    params = {
        "query": f"like:{termo}",
        "limit": 10
    }

    # Cabeçalhos padrão, mantendo Referer para boa conduta
    headers = {
        **HEADERS,
        "Referer": "https://www.gog.com/",
        "Accept": "application/json"
    }

    resultados: List[Dict[str, Any]] = []
    
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        
        dados = resp.json()
        produtos = dados.get("products", [])

        if not produtos:
            return []

        for produto in produtos:
            nome = produto.get("title")
            price_info = produto.get("price", {})
            
            # Nota: Como não passamos BRL, o 'amount' pode vir em USD ou EUR.
            # A API da GOG retorna o valor como string centesimal.
            amount = price_info.get("finalMoney", {}).get("amount")
            
            if not nome or amount is None:
                continue
                
            # Conversão básica de centavos para unidade (ex: 1999 -> 19.99)
            preco = float(amount) / 100

            slug = produto.get("slug")
            link = f"https://www.gog.com/game/{slug}" if slug else None

            resultados.append(_normalizar(nome.strip(), "GOG", preco, link))

    except Exception as e:
        logger.warning(f"[GOG] Falha ao processar resposta: {e}")

    return resultados

def scrape_epic(termo: str) -> List[Dict[str, Any]]:
    url = "https://store.epicgames.com/graphql"
    headers_epic = {
        **HEADERS,
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://store.epicgames.com/pt-BR/browse",
        "Origin": "https://store.epicgames.com",
    }
    query_string = (
        "query searchStoreQuery($keywords:String,$country:String!,$locale:String){"
        "Catalog{searchStore(keywords:$keywords,country:$country,locale:$locale,count:10){"
        "elements{title productSlug urlSlug price(country:$country){totalPrice{discountPrice}}}}}}"
    )
    payload = {
        "operationName": "searchStoreQuery",
        "query": query_string,
        "variables": {"keywords": termo, "country": "BR", "locale": "pt-BR"},
    }
    resultados: List[Dict[str, Any]] = []
    try:
        resp = requests.post(url, headers=headers_epic, json=payload, timeout=TIMEOUT)
        if resp.status_code == 200:
            dados = resp.json()
            elementos = dados.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
            for item in elementos:
                nome = item.get("title")
                price_block = item.get("price", {}).get("totalPrice", {})
                preco_centavos = price_block.get("discountPrice")
                if not nome or preco_centavos is None:
                    continue
                preco = preco_centavos / 100
                slug = item.get("urlSlug") or item.get("productSlug")
                link = f"https://store.epicgames.com/pt-BR/p/{slug}" if slug else None
                resultados.append(_normalizar(nome, "Epic Games", preco, link))
    except Exception:
        pass
    return resultados

def scrape_nuuvem(termo: str) -> List[Dict[str, Any]]:
    locale = "br-pt"
    termo_url = termo.replace(" ", "%20")
    url = f"https://www.nuuvem.com/{locale}/catalog/page/1/search/{termo_url}"
    resultados: List[Dict[str, Any]] = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        links_produto = soup.select('a[href*="/item/"], a[href*="/bundle/"]')
        for link_tag in links_produto:
            nome = link_tag.get("title") or link_tag.get_text(strip=True)
            if not nome: continue
            href = link_tag.get("href")
            if href and href.startswith("/"):
                href = f"https://www.nuuvem.com{href}"
            preco = _extrair_preco_brl(link_tag.get_text(" ", strip=True))
            if preco is None: continue
            resultados.append(_normalizar(nome.strip(), "Nuuvem", preco, href))
    except Exception:
        pass
    return resultados

def _extrair_preco_brl(texto: str) -> Optional[float]:
    matches = re.findall(r"R\$\s*(\d{1,3}(?:\.\d{3})*,\d{2}|\d+,\d{2})", texto)
    if not matches: return None
    valor = matches[-1]
    valor = valor.replace(".", "").replace(",", ".") if "." in valor else valor.replace(",", ".")
    try: return float(valor)
    except ValueError: return None