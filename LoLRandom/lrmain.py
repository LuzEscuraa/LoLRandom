
from __future__ import annotations

import random
import time
from enum import Enum
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

from rotas_comuns import joga_na_rota

BASE_DIR = Path(__file__).parent
DDRAGON = "https://ddragon.leagueoflegends.com"
IDIOMA = "pt_BR"
CACHE_TTL = 6 * 60 * 60  # 6 horas

app = FastAPI(
    title="Sorteador LoL",
    description="Sorteia campeão e rota do League of Legends.",
    version="1.0.0",
)


# ---------- Modelos ----------
class Rota(str, Enum):
    top = "top"
    jungle = "jungle"
    mid = "mid"
    adc = "adc"
    suporte = "suporte"


class Classe(str, Enum):
    assassin = "Assassin"
    fighter = "Fighter"
    mage = "Mage"
    marksman = "Marksman"
    support = "Support"
    tank = "Tank"


ROTAS_NOMES = {
    Rota.top: "Topo",
    Rota.jungle: "Selva",
    Rota.mid: "Meio",
    Rota.adc: "Atirador (Bot)",
    Rota.suporte: "Suporte",
}


class Campeao(BaseModel):
    id: str
    nome: str
    titulo: str
    classes: list[str]
    icone: str


class RotaInfo(BaseModel):
    id: Rota
    nome: str


class Sorteio(BaseModel):
    campeao: Campeao
    rota: RotaInfo


class SorteioTime(BaseModel):
    time: list[Sorteio]


# ---------- Dados (Data Dragon + cache) ----------
_cache: dict = {"campeoes": [], "expira_em": 0.0}


async def carregar_campeoes() -> list[Campeao]:
    if _cache["campeoes"] and time.time() < _cache["expira_em"]:
        return _cache["campeoes"]

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            versoes = (await client.get(f"{DDRAGON}/api/versions.json")).json()
            versao = versoes[0]
            resp = await client.get(
                f"{DDRAGON}/cdn/{versao}/data/{IDIOMA}/champion.json"
            )
            resp.raise_for_status()
            dados = resp.json()["data"]
    except (httpx.HTTPError, KeyError, IndexError):
        if _cache["campeoes"]:  # usa cache antigo se a Riot estiver fora
            return _cache["campeoes"]
        raise HTTPException(503, "Não foi possível obter os campeões da Riot.")

    campeoes = [
        Campeao(
            id=c["id"],
            nome=c["name"],
            titulo=c["title"],
            classes=c["tags"],
            icone=f"{DDRAGON}/cdn/{versao}/img/champion/{c['image']['full']}",
        )
        for c in dados.values()
    ]
    campeoes.sort(key=lambda c: c.nome)
    _cache.update(campeoes=campeoes, expira_em=time.time() + CACHE_TTL)
    return campeoes


def filtrar(campeoes: list[Campeao], classe: Classe | None) -> list[Campeao]:
    if classe:
        campeoes = [c for c in campeoes if classe.value in c.classes]
    if not campeoes:
        raise HTTPException(404, "Nenhum campeão encontrado com esse filtro.")
    return campeoes


def rota_info(rota: Rota) -> RotaInfo:
    return RotaInfo(id=rota, nome=ROTAS_NOMES[rota])


# ---------- Endpoints ----------
@app.get("/", include_in_schema=False)
async def front_end():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/rotas", response_model=list[RotaInfo], tags=["Listagem"])
async def listar_rotas():
    return [rota_info(r) for r in Rota]


@app.get("/campeoes", response_model=list[Campeao], tags=["Listagem"])
async def listar_campeoes(classe: Classe | None = None, rota: Rota | None = None):
    """Lista campeões. Com `rota`, traz só os comuns naquela rota."""
    campeoes = filtrar(await carregar_campeoes(), classe)
    if rota:
        campeoes = [c for c in campeoes if joga_na_rota(c.id, c.classes, rota.value)]
    return campeoes


@app.get("/sortear", response_model=Sorteio, tags=["Sorteio"])
async def sortear(rota: Rota | None = None, classe: Classe | None = None):
    """Sorteia um campeão e uma rota. Filtros opcionais: `rota` e `classe`."""
    campeoes = filtrar(await carregar_campeoes(), classe)
    return Sorteio(
        campeao=random.choice(campeoes),
        rota=rota_info(rota or random.choice(list(Rota))),
    )


@app.get("/sortear/campeao", response_model=Campeao, tags=["Sorteio"])
async def sortear_campeao(classe: Classe | None = None):
    return random.choice(filtrar(await carregar_campeoes(), classe))


@app.get("/sortear/rota", response_model=RotaInfo, tags=["Sorteio"])
async def sortear_rota():
    return rota_info(random.choice(list(Rota)))


@app.get("/sortear/time", response_model=SorteioTime, tags=["Sorteio"])
async def sortear_time(
    repetir_campeoes: bool = Query(False, description="Permitir campeões repetidos"),
    limitar_por_rota: bool = Query(
        False, description="Sortear só campeões comuns em cada rota"
    ),
):
    """Sorteia um time de 5: uma rota para cada jogador, sem repetir rota."""
    campeoes = await carregar_campeoes()
    rotas = random.sample(list(Rota), k=len(Rota))

    if limitar_por_rota:
        usados: set[str] = set()
        escolhidos: list[Campeao] = []
        for rota in rotas:
            opcoes = [
                c for c in campeoes
                if joga_na_rota(c.id, c.classes, rota.value)
                and (repetir_campeoes or c.id not in usados)
            ]
            if not opcoes:
                raise HTTPException(404, f"Sem campeões disponíveis para {rota.value}.")
            escolhido = random.choice(opcoes)
            usados.add(escolhido.id)
            escolhidos.append(escolhido)
    elif repetir_campeoes:
        escolhidos = random.choices(campeoes, k=len(rotas))
    else:
        escolhidos = random.sample(campeoes, k=len(rotas))

    return SorteioTime(
        time=[Sorteio(campeao=c, rota=rota_info(r)) for c, r in zip(escolhidos, rotas)]
    )
