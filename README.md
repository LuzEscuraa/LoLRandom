# 🎲 Sorteador de Campeão e Rota – League of Legends

API REST em Python (FastAPI) com front-end integrado que sorteia **campeão** e **rota** do League of Legends. Dá para sortear um jogador, ou um time completo de 5, com a opção de limitar os campeões ao que é comum em cada rota.

## Funcionalidades

- Sorteio de campeão e rota, com filtros por rota e por classe
- Sorteio de time de 5, cada jogador em uma rota diferente e sem campeões repetidos
- Modo **"só campeões comuns na rota"**: um Teemo no suporte deixa de sair
- Lista de campeões sempre atualizada pela [Data Dragon](https://developer.riotgames.com/docs/lol#data-dragon) da Riot, em português, com ícones
- Cache de 6 horas, com uso do cache antigo se a Riot estiver fora do ar
- Documentação interativa gerada automaticamente (Swagger)

## Tecnologias

- Python 3.10+
- [FastAPI](https://fastapi.tiangolo.com/) e Uvicorn
- httpx
- HTML, CSS e JavaScript puros no front-end, sem dependências

## Como rodar

```bash
git clone https://github.com/SEU-USUARIO/lol-sorteador.git
cd lol-sorteador

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

uvicorn main:app --reload
```

| O que | Endereço |
|---|---|
| Front-end | http://127.0.0.1:8000/ |
| Documentação da API (Swagger) | http://127.0.0.1:8000/docs |

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| GET | `/sortear` | Sorteia campeão e rota. Filtros opcionais: `rota`, `classe` |
| GET | `/sortear/campeao` | Sorteia só o campeão (filtro opcional: `classe`) |
| GET | `/sortear/rota` | Sorteia só a rota |
| GET | `/sortear/time` | Sorteia um time de 5. Opções: `repetir_campeoes`, `limitar_por_rota` |
| GET | `/campeoes` | Lista campeões (filtros opcionais: `classe`, `rota`) |
| GET | `/rotas` | Lista as rotas |

**Valores aceitos**
- `rota`: `top`, `jungle`, `mid`, `adc`, `suporte`
- `classe`: `Assassin`, `Fighter`, `Mage`, `Marksman`, `Support`, `Tank`

**Exemplo**

```bash
curl "http://127.0.0.1:8000/sortear/time?limitar_por_rota=true"
```

```json
{
  "time": [
    {
      "campeao": {
        "id": "Darius",
        "nome": "Darius",
        "titulo": "a Mão de Noxus",
        "classes": ["Fighter", "Tank"],
        "icone": "https://ddragon.leagueoflegends.com/cdn/.../Darius.png"
      },
      "rota": { "id": "top", "nome": "Topo" }
    }
  ]
}
```

(a resposta real traz os 5 jogadores)

## Estrutura do projeto

```
lol-sorteador/
├── main.py            # API FastAPI e regras de sorteio
├── rotas_comuns.py    # mapa editável de campeões por rota
├── requirements.txt
└── static/
    └── index.html     # front-end
```

## Personalizando o mapa de rotas

A Riot não publica quais campeões jogam em cada rota, então o mapa em `rotas_comuns.py` é uma curadoria geral e não uma estatística oficial. Para ajustar, mova o nome do campeão entre as listas do arquivo (os nomes seguem os IDs da Data Dragon, por exemplo `MonkeyKing` para Wukong). Campeões que não estiverem mapeados, como lançamentos novos, usam a classe principal como palpite.

Dica: `GET /campeoes?rota=mid` lista o que está valendo para uma rota.

## Aviso legal

Este projeto não é endossado pela Riot Games e não reflete as opiniões ou posições da Riot Games ou de quem trabalha com League of Legends. League of Legends e Riot Games são marcas registradas da Riot Games, Inc.
