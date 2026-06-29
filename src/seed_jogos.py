"""
src/seed_jogos.py

Popula o dados.db com uma lista de jogos chamando o orquestrador
atualizar_precos() (Fase 2) para cada um — sem duplicar nenhuma lógica de
scraping ou de gravação no banco, só reaproveita o que já existe.

Uso:
    python src/seed_jogos.py
    python src/seed_jogos.py "Hollow Knight" "Hades"   # lista customizada

Precisa ser executado a partir da raiz do projeto, do mesmo jeito que
atualizar_precos.py (os imports dele são relativos à pasta src/).
"""

import sys
import time

from atualizar_precos import atualizar_precos
from database import init_db

# Lista padrão usada quando nenhum jogo é passado por linha de comando.
JOGOS_SEED = [
    "Hollow Knight",
    "Hades",
    "Stardew Valley",
    "Elden Ring",
    "Celeste",
    "Cyberpunk 2077",
    "The Witcher 3: Wild Hunt",
    "Slay the Spire",
    "Terraria",
    "Dark Souls III",
    "Red Dead Redemption 2",
    "Divinity: Original Sin 2",
    "Cuphead",
    "Dead Cells",
    "The Binding of Isaac: Rebirth",
    "Subnautica",
    "Factorio",
    "Ori and the Will of the Wisps",
    "Control",
    "Sekiro: Shadows Die Twice",
    "Grand Theft Auto V",
    "Monster Hunter: World",
    "Doom Eternal",
    "Hollow Knight: Silksong",
    "Baldur's Gate 3",
    "Disco Elysium",
    "Outer Wilds",
    "Forza Horizon 5",
    "Resident Evil Village",
    "Hitman 3",
    "The Elder Scrolls V: Skyrim",
    "Assassin's Creed Valhalla",
    "Far Cry 6",
    "Death Stranding",
    "Nier: Automata",
    "The Legend of Zelda: Breath of the Wild",
    "Metroid Dread",
    "Super Mario Odyssey",
    "Animal Crossing: New Horizons",
    "Mario Kart 8 Deluxe",
    "The Legend of Zelda: Tears of the Kingdom",
    "Splatoon 3",
    "Bayonetta 3",
    "Xenoblade Chronicles 3",
    "Fire Emblem: Three Houses",
    "Octopath Traveler",
    "Bravely Default II",
    "Triangle Strategy",
    "Shin Megami Tensei V",
    "Resident Evil 4",
]

# Pausa entre jogos para não martelar as 4 lojas em sequência muito rápida
# (a Nuuvem em especial faz parsing de HTML e pode bloquear/limitar acessos
# muito frequentes). Ajuste ou zere se não for um problema no seu caso.
PAUSA_ENTRE_JOGOS_SEGUNDOS = 1.5


def seed(jogos: list[str]) -> None:
    init_db()  # garante que as tabelas existem antes de qualquer insert

    falhas = []

    for i, jogo in enumerate(jogos, start=1):
        print(f"\n[{i}/{len(jogos)}] {jogo}")
        try:
            atualizar_precos(jogo)
        except Exception as e:
            # Uma falha pontual (ex: timeout numa loja) não deve
            # interromper o lote inteiro.
            print(f"  -> falhou: {e}")
            falhas.append(jogo)

        if i < len(jogos):
            time.sleep(PAUSA_ENTRE_JOGOS_SEGUNDOS)

    print(f"\nSeed concluído: {len(jogos) - len(falhas)}/{len(jogos)} jogos processados com sucesso.")
    if falhas:
        print(f"Falharam: {', '.join(falhas)}")


if __name__ == "__main__":
    jogos = sys.argv[1:] if len(sys.argv) > 1 else JOGOS_SEED
    seed(jogos)
