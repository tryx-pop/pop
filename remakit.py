import os
import discord
from discord.ext import tasks
from datetime import datetime, timezone, timedelta

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN non défini dans les variables d’environnement")


CHANNEL_NAME = "📩┃deadline-check"
CHECK_HOUR = 23
CHECK_MINUTE = 00
LOCAL_TZ = timezone(timedelta(hours=1))  

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Connecté en tant que {client.user}")
    check_deadlines.start()  

@tasks.loop(minutes=1)
async def check_deadlines():
    now = datetime.now(LOCAL_TZ)
    if now.hour == CHECK_HOUR and now.minute == CHECK_MINUTE:
        print("Vérification des deadlines en cours...")

        
        guild = client.guilds[0]  
        channel = discord.utils.get(guild.text_channels, name=CHANNEL_NAME)
        if not channel:
            print(f"Channel '{CHANNEL_NAME}' non trouvé")
            return

        
        messages = [msg async for msg in channel.history(limit=100)]

        today = now.date()
        posted_users = set()

        for msg in messages:
            
            local_msg_date = msg.created_at.astimezone(LOCAL_TZ).date()
            if local_msg_date == today:
                posted_users.add(msg.author.id)

        
        clipper_role = discord.utils.get(guild.roles, name="Clipper")
        if not clipper_role:
            print("Le rôle 'Clipper' n'existe pas sur le serveur !")
            return

        
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


client.run(TOKEN)
