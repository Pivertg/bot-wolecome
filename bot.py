import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Configuration - À MODIFIER avec tes IDs directement dans le code
GUILD_ID = 1437060358081745062  # ID de ton serveur
WELCOME_CHANNEL_ID = 1437161002180411543  # ID du channel de bienvenue
ALLOWED_ROLE_ID = 1437160650198745228  # ID du rôle autorisé pour +annonce

# Permissions du bot
intents = discord.Intents.default()
intents.members = True  # Nécessaire pour détecter les nouveaux membres
intents.message_content = True  # Nécessaire pour lire les commandes

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user}")
    print(f"📋 Serveur surveillé : {GUILD_ID}")
    print(f"💬 Channel de bienvenue : {WELCOME_CHANNEL_ID}")
    print(f"🔐 Rôle autorisé : {ALLOWED_ROLE_ID}")

@bot.event
async def on_member_join(member):
    """Envoie un message de bienvenue quand quelqu'un rejoint le serveur"""
    
    # Vérifier que c'est le bon serveur
    if member.guild.id != GUILD_ID:
        return
    
    # Récupérer le channel de bienvenue
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if not channel:
        print(f"❌ Channel de bienvenue introuvable : {WELCOME_CHANNEL_ID}")
        return
    
    # Créer l'embed de bienvenue
    embed = discord.Embed(
        title="🎉 Nouveau membre !",
        description=f"**Bienvenue sur le serveur __{member.guild.name}__ !**\n\nTu es le **{member.guild.member_count}ème membre** !",
        color=discord.Color.red()
    )
    
    # Ajouter la photo de profil
    embed.set_thumbnail(url=member.display_avatar.url)
    
    try:
        # Envoyer le ping ET l'embed dans le même message
        await channel.send(content=f"{member.mention}", embed=embed)
        print(f"✅ Message de bienvenue envoyé pour {member.name}")
    except Exception as e:
        print(f"❌ Erreur envoi bienvenue : {e}")

@bot.command(name="annonce")
async def annonce(ctx):
    """Commande pour créer une annonce (réservée aux personnes avec le rôle autorisé)"""
    
    # Vérifier les permissions
    has_permission = False
    
    # Vérifier si l'utilisateur a le rôle autorisé
    if ALLOWED_ROLE_ID != 0:
        role = discord.utils.get(ctx.guild.roles, id=ALLOWED_ROLE_ID)
        if role in ctx.author.roles:
            has_permission = True
    
    # Vérifier si l'utilisateur est administrateur
    if ctx.author.guild_permissions.administrator:
        has_permission = True
    
    if not has_permission:
        await ctx.send("❌ Tu n'as pas la permission d'utiliser cette commande !")
        return
    
    # Supprimer la commande initiale
    try:
        await ctx.message.delete()
    except:
        pass
    
    # Demander le contenu de l'annonce
    question1 = await ctx.send("📝 **Quel est le contenu de ton annonce ?**\n*(Réponds dans ce channel)*")
    
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    
    try:
        # Attendre le message (60 secondes max)
        message_content = await bot.wait_for('message', check=check, timeout=60.0)
        content = message_content.content
        
        # Supprimer la question et la réponse
        try:
            await question1.delete()
            await message_content.delete()
        except:
            pass
        
        # Demander où envoyer l'annonce
        question2 = await ctx.send("📍 **Où veux-tu envoyer l'annonce ?**\n*(Mentionne le channel avec #)*")
        
        channel_msg = await bot.wait_for('message', check=check, timeout=60.0)
        
        # Récupérer le channel mentionné
        if channel_msg.channel_mentions:
            target_channel = channel_msg.channel_mentions[0]
        else:
            await ctx.send("❌ Aucun channel valide mentionné. Annulation.")
            return
        
        # Supprimer la question et la réponse
        try:
            await question2.delete()
            await channel_msg.delete()
        except:
            pass
        
        # Demander si on veut envoyer avec un délai (optionnel)
        question3 = await ctx.send("⏱️ **Veux-tu envoyer l'annonce après un délai ?**\n*(Réponds avec un nombre de secondes, ou 'non' pour envoyer maintenant)*")
        
        delay_msg = await bot.wait_for('message', check=check, timeout=60.0)
        send_delay = None
        
        if delay_msg.content.lower() not in ['non', 'no', 'n']:
            try:
                send_delay = int(delay_msg.content)
            except:
                send_delay = None
        
        # Supprimer la question et la réponse
        try:
            await question3.delete()
            await delay_msg.delete()
        except:
            pass
        
        # Créer l'embed d'annonce
        embed = discord.Embed(
            title="📢 Annonce",
            description=content,
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Annonce par {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        
        # Envoyer l'annonce immédiatement ou après un délai
        if send_delay:
            confirmation = await ctx.send(f"⏱️ Annonce programmée dans {send_delay} secondes pour {target_channel.mention}")
            await confirmation.delete(delay=5)
            await asyncio.sleep(send_delay)
        
        sent_message = await target_channel.send(embed=embed)
        
        # Confirmer l'envoi
        confirmation = await ctx.send(f"✅ Annonce envoyée dans {target_channel.mention} !")
        await confirmation.delete(delay=5)
    
    except asyncio.TimeoutError:
        await ctx.send("⏱️ Temps écoulé ! Commande annulée.")
    except Exception as e:
        await ctx.send(f"❌ Erreur lors de la création de l'annonce : {e}")
        print(f"Erreur annonce : {e}")

async def start_bot(token):
    """Fonction pour démarrer le bot"""
    try:
        await bot.start(token)
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        raise

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if TOKEN:
        asyncio.run(start_bot(TOKEN))
    else:

        print("❌ DISCORD_TOKEN manquant dans .env")

