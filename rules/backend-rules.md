# Regras de Backend (Python)

1. **Type Hints:** Todas as funções Python devem, obrigatoriamente, possuir tipagem estática (Type Hints) nos parâmetros e retornos (ex: `def funcao(termo: str) -> List[Dict[str, Any]]:`).
2. **Tratamento de Erros:** Nenhuma função de extração de dados (scraping) pode quebrar o servidor. Todos os requests externos devem estar contidos em blocos `try/except`.
3. **Resiliência:** Sempre defina um `timeout` explícito em chamadas de rede (ex: `requests.get(url, timeout=10)`).
4. **Logs:** Utilize a biblioteca `logging` do Python para registrar erros e informações em vez de usar `print()` nativo.