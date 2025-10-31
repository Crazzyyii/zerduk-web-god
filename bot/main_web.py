# Ejemplo de integración del bot: crear partida y mandar links hacia la web.
# NOTA: reemplaza TOKEN/IDs y adapta a tu lógica real si ya la tienes.
import os, random, string, json
import discord
import requests

from pathlib import Path
from importlib import import_module

# Si tienes champion_images.py y utilidades en tu proyecto original,
# puedes importarlas así (ajusta la ruta si es necesario):
# from champion_images import CHAMPION_IMAGES

TOKEN = os.getenv("TOKEN")  # Exporta TOKEN en tu entorno
ANNOUNCE_CHANNEL_ID = int(os.getenv("ANNOUNCE_CHANNEL_ID", "0"))
WEB_BASE = os.getenv("WEB_BASE", "http://localhost:5000")  # URL de tu Flask web (local o deploy)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)

def gen_code(k=6):
    al = string.ascii_uppercase + string.digits
    return "LOL" + "".join(random.choice(al) for _ in range(k))

@client.event
async def on_ready():
    print(f"Conectado como {client.user}")

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    if message.content.startswith("!impostor"):
        if len(message.mentions) < 3:
            await message.channel.send("Necesitas al menos 3 jugadores mencionados.")
            return

        players = message.mentions
        code = gen_code()

        # Seleccionar impostores
        roll = random.random()
        if roll <= 0.12 and len(players) >= 4:
            impostor_count = 2
        else:
            impostor_count = 1
        impostors = random.sample(players, impostor_count)

        # Campeón único para todos por defecto (puedes alternar)
        champions = ["Ahri","Lux","Garen","Ezreal","Leona","Ashe","Zed","Caitlyn","Yasuo","Jinx"]
        chosen = random.choice(champions)

        # Armar payload para /api/create_game
        payload_players = {}
        for p in players:
            payload_players[str(p.id)] = {
                "name": p.display_name,
                "impostor": (p in impostors),
                "champion": None if p in impostors else chosen,
                "alive": True
            }

        try:
            r = requests.post(f"{WEB_BASE}/api/create_game", json={
                "code": code,
                "host_id": message.author.id,
                "players": payload_players
            }, timeout=10)
            r.raise_for_status()
        except Exception as e:
            await message.channel.send(f"❌ No pude crear la partida en la web: {e}")
            return

        await message.channel.send(f"🎮 Partida creada: {WEB_BASE}/game/{code}")

        # Enviar links individuales por DM
        for p in players:
            try:
                link = f"{WEB_BASE}/role/{code}?user={p.id}"
                await p.send(f"🔗 Tu rol: {link}")
            except discord.Forbidden:
                await message.channel.send(f"❌ No pude enviar DM a {p.display_name}")

    if message.content.startswith("!ranking"):
        await message.channel.send(f"🏆 Ranking: {WEB_BASE}/ranking")

# Para ejecutar: export TOKEN y luego python bot/main_web.py
if __name__ == "__main__":
    if not TOKEN or not ANNOUNCE_CHANNEL_ID:
        print("Configura las variables de entorno TOKEN y ANNOUNCE_CHANNEL_ID.")
    client.run(TOKEN)
