# Zerduk Web (Starter)

## Estructura
- `web/`: Flask + Socket.IO (UI, lobby, roles, ranking)
- `bot/`: ejemplo de bot que crea partidas y manda links
- `shared/`: archivos compartidos (`db.json`, `stats.json`, utilidades `db.py`)

## Cómo correr local
1) Crea un virtualenv e instala dependencias
```
pip install -r requirements.txt
```
2) Inicia la web
```
python web/app.py
```
3) Exporta variables de entorno y corre el bot
```
set TOKEN=TU_TOKEN_DISCORD
set ANNOUNCE_CHANNEL_ID=ID_CANAL
set WEB_BASE=http://localhost:5000
python bot/main_web.py
```
4) En Discord, crea una partida:
```
!impostor @jug1 @jug2 @jug3
```
Verás el lobby en: `http://localhost:5000/game/LOLXXX...` y los jugadores tendrán su link privado `role`.

## Producción
- Sube `web/` a Railway/Render y deja vivo el Socket.IO.
- Ajusta `WEB_BASE` a la URL pública y listo.
