"""Campeões que costumam jogar em cada rota.

Os nomes são os IDs da Data Dragon (ex.: Wukong = "MonkeyKing", Kai'Sa = "Kaisa").
Um campeão pode aparecer em várias rotas. Edite as listas à vontade: é uma
curadoria geral, não uma estatística oficial da Riot.

Campeões que não estiverem listados (lançamentos novos, por exemplo) usam a
classe principal como palpite, ver FALLBACK_POR_CLASSE.
"""
from __future__ import annotations

POR_ROTA: dict[str, list[str]] = {
    "top": [
        "Aatrox", "Akali", "Ambessa", "Aurora", "Camille", "Chogath", "Darius",
        "DrMundo", "Fiora", "Gangplank", "Garen", "Gnar", "Gwen", "Heimerdinger",
        "Illaoi", "Irelia", "Jax", "Jayce", "KSante", "Kayle", "Kennen", "Kled",
        "Malphite", "Maokai", "Mordekaiser", "Nasus", "Olaf", "Ornn", "Pantheon",
        "Poppy", "Quinn", "Renekton", "Riven", "Rumble", "Sett", "Shen", "Singed",
        "Sion", "Smolder", "Teemo", "Trundle", "Tryndamere", "Urgot", "Vayne",
        "Volibear", "Yone", "Yorick", "MonkeyKing",
    ],
    "jungle": [
        "Amumu", "Ambessa", "Belveth", "Briar", "Diana", "Ekko", "Elise",
        "Evelynn", "Fiddlesticks", "Gragas", "Graves", "Hecarim", "Ivern",
        "JarvanIV", "Jax", "Karthus", "Kayn", "Khazix", "Kindred", "LeeSin",
        "Lillia", "MasterYi", "Naafiri", "Nidalee", "Nocturne", "Nunu", "Olaf",
        "Rammus", "RekSai", "Rengar", "Sejuani", "Shaco", "Shyvana", "Skarner",
        "Sylas", "Taliyah", "Talon", "Trundle", "Udyr", "Vi", "Viego", "Volibear",
        "Warwick", "MonkeyKing", "XinZhao", "Zac",
    ],
    "mid": [
        "Ahri", "Akali", "Akshan", "Anivia", "Annie", "AurelionSol", "Aurora",
        "Azir", "Cassiopeia", "Corki", "Diana", "Ekko", "Fizz", "Galio", "Hwei",
        "Irelia", "Jayce", "Kassadin", "Katarina", "Leblanc", "Lissandra", "Lux",
        "Malzahar", "Mel", "Naafiri", "Neeko", "Orianna", "Qiyana", "Ryze",
        "Smolder", "Swain", "Sylas", "Syndra", "Taliyah", "Talon", "TwistedFate",
        "Veigar", "Velkoz", "Vex", "Viktor", "Vladimir", "Xerath", "Yasuo", "Yone",
        "Zed", "Ziggs", "Zoe", "Tristana",
    ],
    "adc": [
        "Aphelios", "Ashe", "Caitlyn", "Draven", "Ezreal", "Jhin", "Jinx",
        "Kaisa", "Kalista", "KogMaw", "Lucian", "MissFortune", "Nilah", "Samira",
        "Senna", "Sivir", "Smolder", "Tristana", "Twitch", "Varus", "Vayne",
        "Xayah", "Yunara", "Zeri", "Ziggs",
    ],
    "suporte": [
        "Alistar", "Bard", "Blitzcrank", "Brand", "Braum", "Janna", "Karma",
        "Leona", "Lulu", "Lux", "Maokai", "Mel", "Milio", "Morgana", "Nami",
        "Nautilus", "Neeko", "Pyke", "Rakan", "Rell", "Renata", "Senna",
        "Seraphine", "Sona", "Soraka", "Swain", "TahmKench", "Taric", "Thresh",
        "Velkoz", "Xerath", "Yuumi", "Zilean", "Zyra", "Zoe", "Hwei",
    ],
}

# Palpite para campeões fora das listas acima, usando a classe principal.
FALLBACK_POR_CLASSE: dict[str, list[str]] = {
    "Marksman": ["adc"],
    "Support": ["suporte"],
    "Mage": ["mid"],
    "Assassin": ["mid", "jungle"],
    "Fighter": ["top"],
    "Tank": ["top", "suporte"],
}

# campeão -> rotas (montado uma vez a partir de POR_ROTA)
_POR_CAMPEAO: dict[str, set[str]] = {}
for _rota, _ids in POR_ROTA.items():
    for _id in _ids:
        _POR_CAMPEAO.setdefault(_id, set()).add(_rota)


def joga_na_rota(campeao_id: str, classes: list[str], rota: str) -> bool:
    """True se o campeão é comum na rota (ou, se não estiver mapeado, pela classe)."""
    if campeao_id in _POR_CAMPEAO:
        return rota in _POR_CAMPEAO[campeao_id]
    principal = classes[0] if classes else ""
    return rota in FALLBACK_POR_CLASSE.get(principal, [])
