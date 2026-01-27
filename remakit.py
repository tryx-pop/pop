import discord
import os 
TOKEN = os.getenv("DISCORD_TOKEN")
from discord.ext import tasks
from datetime import datetime, timezone, timedelta

# -------------------- CONFIG --------------------
TOKEN = "MTQ2NTQ1NTc4NzY2ODI3NTIyMA.GEvMZK._t2eDpUlTvHa04gHbE75J84OpJgN3zWdItQ4wI"  # 🔑 Remplace par ton token
CHANNEL_NAME = "📩┃deadline-check"
CHECK_HOUR = 18
CHECK_MINUTE = 43
LOCAL_TZ = timezone(timedelta(hours=1))  # France = UTC+1 / UTC+2 en été
# ------------------------------------------------

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # nécessaire pour ping les membres

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Connecté en tant que {client.user}")
    check_deadlines.start()  # démarre la tâche quotidienne

@tasks.loop(minutes=1)
async def check_deadlines():
    now = datetime.now(LOCAL_TZ)
    if now.hour == CHECK_HOUR and now.minute == CHECK_MINUTE:
        print("Vérification des deadlines en cours...")

        # Récupère le serveur et le channel
        guild = client.guilds[0]  # si ton bot est sur un seul serveur
        channel = discord.utils.get(guild.text_channels, name=CHANNEL_NAME)
        if not channel:
            print(f"Channel '{CHANNEL_NAME}' non trouvé")
            return

        # Récupère les 100 derniers messages
        messages = [msg async for msg in channel.history(limit=100)]

        today = now.date()
        posted_users = set()

        for msg in messages:
            # Convertit le timestamp UTC du message en heure locale
            local_msg_date = msg.created_at.astimezone(LOCAL_TZ).date()
            if local_msg_date == today:
                posted_users.add(msg.author.id)

        # Récupère le rôle "Clipper"
        clipper_role = discord.utils.get(guild.roles, name="Clipper")
        if not clipper_role:
            print("Le rôle 'Clipper' n'existe pas sur le serveur !")
            return

        # Ping uniquement les membres qui ont le rôle "Clipper" et n'ont pas posté
        for member in guild.members:
            if (
                not member.bot
                and member.id not in posted_users
                and clipper_role in member.roles
            ):
                try:
                    await channel.send(
                        f"{member.mention} 🚨 N'oublie pas ta deadline check ! Ceci doit être réalisé avant 23h."
                    )
                except Exception as e:
                    print(f"Impossible de ping {member}: {e}")

        print("Vérification terminée")

# Démarre le bot
client.run(TOKEN)
