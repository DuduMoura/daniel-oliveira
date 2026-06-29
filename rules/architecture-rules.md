# Regras de Arquitetura - GamePrice Comparator

1. **Restrição de Banco de Dados:** É estritamente proibido o uso de SGBDs externos (como PostgreSQL ou MySQL). Todo armazenamento deve ser feito exclusivamente em SQLite local (`dados.db`).
2. **Restrição de Frontend:** O frontend não deve utilizar Node.js, NPM, React, Vue ou Angular. Deve ser mantido estritamente em HTML, CSS (Tailwind via CDN) e JavaScript puro (Vanilla JS).
3. **Comunicação:** O Frontend deve se comunicar com o Backend apenas via chamadas de API (fetch) assíncronas.