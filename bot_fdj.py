import discord # import de toutes les bibliothèques contenant les commandes pour la création du bot
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import json
import asyncio

TOKEN = "123456789" # token du bot créer sur le portail développeur de Discord
CHANNEL_ID = 123456789  # ID du salon Discord visé
URL_ACTUS = "https://www.fdj.fr/mag/actus" # url visée pour le scrapping (modifiable sur la page qui vous interesse)
FICHIER_JEUX = "jeux_connus.json" # initialisation de la variable qui permet d'attribuer le fichier .json (qui sera mis à jour directement par le bot lui même)
MAX_DISCORD_MSG_LEN = 2000  # Discord limite officielle pour 1 message

MAX_TITLE_LEN = 100  # limite la taille titre individuel pour éviter l'envoie de trop gros trucs inutiles (sert aussi de filtre pour les div inutiles en plus de la selection par titre "jeux à gratter")

try:
    with open(FICHIER_JEUX, "r", encoding="utf-8") as f: # ouvre le fichier .json pour vérification de doublon
        jeux_connus = json.load(f) # lit le fichier déja ouvert dans la variable f
    if not isinstance(jeux_connus, list): # permet de verifier que jeux_connus n'est pas une liste; isinstance renvoie true 
        print("⚠ jeux_connus n'est pas une liste, réinitialisation.") # s'il ne trouve pas le fichier .json contenant le tableau alors il renverra ce message d'erreur
        jeux_connus = [] # et il va créer par la suite sa propre liste le rendant ainsi autonome au niveau des màj
except FileNotFoundError: # capture une erreur spécifique (FileNotFoundError)
    jeux_connus = [] # si cette erreur est déctée alors il créée une liste 

verif_active = False # au démarage le bot ne vérifie pas, il attends qu'on lui lance la commande donc elle est par défaut sur false

intents = discord.Intents.default() # mise en place de l'intent à fin que le bot puisse lire les messages précédents et en envoyer (l'intent est à activer aussi sur le portail developpeur)
intents.message_content = True # permet au bot de voire et de lire le contenue des messages 
bot = commands.Bot(command_prefix='!', intents=intents) # préfixe le plus courant pour les commandes bot Discord

def nettoyer_titre(t): # définition de la variable de nettoyage des titres
    t = t.strip() # l'utilisation de ce strip permet de retirer les espaces pour qu'il puisse vraiment nettoyer les lignes (lire) à voir si avec le temps ça sert vraiment ou pas (présence de noms à rallonge, etc..)
    if len(t) > MAX_TITLE_LEN: # si le texte dépasse la taille maximale 
        t = t[:MAX_TITLE_LEN-3] + "..." # alors on va retirer les 3 derniers caractères donc on en aura 97 et on remplace les 3 manquants par les "..."
    return t # on retourne le titre (il finit par ... s'il est trop long)

async def verifier_nouveaux_jeux(): # mise en place d'une async def: comme il y a des commandes avec lesquelles le bot interragie la boucle peut se stoper si on lui lance la comande et reprendre une vérifcation plus tard
    global jeux_connus # création d'une variable globale pour pouvoir mettre à jour le fichier .json
    await bot.wait_until_ready() # permet lors du lancement du bot sa pleine initialisation (il n'appraitra conncté qu'une fois que le serveur sera bien synchronisé)
    while not bot.is_closed() and verif_active: # tant que le bot est allumé en verification alors la boucle de verifcation se fait toujours (mem si ici c'est pas utile comme c'est pas héberger en continue; ça serait utile eventuellement lors d'un déploiement sur un VPS)
        try:
            resp = requests.get(URL_ACTUS) # il utilise une comande de la bibli request, pour faire une requete url (ici sur la variable qu'on a définit au début)
            soup = BeautifulSoup(resp.text, "html.parser") # utilisation d'une commande de la biblie BeautifulSoup, qui permet ici de récuperer le texte d'une page web en html (ça marche aussi pour du xml), cette commande permet de manier le texte (afficher les différentes balises html dans notre cas)

            candidats = [] # création d'une liste "candidats" où on va stocker les jeux qui apraissents
            for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "strong", "span", "p", "div"]): # vérifcation sur le html dans toutes les balises citées (généralement c'est dans des divs sur cette page web, mais je préferais élargier pour un max de fléxibilité; ça peut être un soucis s'il y a beaucoup de texte à regarder)
                text = tag.get_text(strip=True) # pour chaque texte trouvé il prends tout et il retire les espaces au début et à la fin pour éviter la casse et les pavers 
                if text and "Nouveau jeu à gratter" in text.lower(): # si dans les textes trouvés il y a jeu à gratter sans tenir compte de la formes (maj ou min)
                    candidats.append(text) # alors il ajoute l'extrait (toujours limité à 100 char) à la liste candidats 

            nouveautes = list(dict.fromkeys(candidats)) # comme candidats filtre pas, il se peut que parfois on retrouve le même texte sur une page web, pour cela on va créer un dictionnaier (dict) ui permet avec .fromkeys de séparer les doublons car les keys sont unique donc le programme va automatiquement supprimer le doublon s'il voit 2 fois un texte similaire

            nouveaux = [] # création d'une liste "nouveaux"
            jeux_connus_lower = [j.lower() for j in jeux_connus] # on parcours chaque éléement j (qui correspond à une ligne dans le fichier json) et on le mets en minuscule pour éviter la casse
            for titre in nouveautes: # pour chaque titre dans la liste nouveautes qu'on a définit précédement
                titre_nettoye = nettoyer_titre(titre) # on appelle la fonction nettoyer_titre pour normaliser le texte, et on stock le résultat dans titre_nettoye
                if titre_nettoye.lower() not in jeux_connus_lower: # si une fois le texte nettoyé en petit (toujours pour éviter la casse et uniformiser le texte) s'il n'apprait pas dans la liste jeux_connus_lower (définit précedement)
                    nouveaux.append(titre_nettoye) # alors on ajoute ce texte à la liste nouveaux (ce qui selectionne les nouveaux jeux à gratter)

            channel = bot.get_channel(CHANNEL_ID) # récupère l'id du channel pour que le bot envoie le message au bon endroit
            if channel is None: # si le channel id n'existe pas
                print(f"❌ Impossible de trouver le channel avec l'id {CHANNEL_ID}") # alors il enverra ce message d'erreur (dans le terminal) contenant ce message + l'id du chanel visé
            else: # sinon
                if nouveaux: # si nouveaux contient du texte
                    msg = "🆕 Nouveaux jeux à gratter détectés 🔊: \n" # alors il construit un message unique listant tous les nouveaux titres qu'il y en ai un ou plusieurs, la présentation est la même
                    for jeu in nouveaux: # lance une boucle pour ecrire à l'interieur du message (tant qu'il y du texte dans la liste nouveaux)
                        ligne = f"- **{jeu}**\n" # création de la ligne pour 1 jeu à gratter à chaque fois il retournera à la ligne
                        if len(msg) + len(ligne) > MAX_DISCORD_MSG_LEN: # Vérifie que le message reste dans la limite de Discord pour éviter de prendre tout le contenue (sinon le message est bloqué au dessus de 1900 char.) donc si en ajoutant cette ligne, on dépasse la taille max autorisée par Discord
                            msg += "... (et plus)\n" # on affiche "..." +  qu'il y a plus de contenu non affiché (et plus)
                            break # on sort de la boucle, et on arrete d'ajouter et plus car peut-etre que le texte qui arrive après sera plus court et ne necessitera donc pas cette ajout
                        msg += ligne # sinon on ajoute la ligne

                    print(f"📢 Envoi message:\n{msg}") # utile pour le débugage dans la console, ça me permet de statuer sur l'execution des commandes
                    try: # on essaie
                        await channel.send(msg) # d'envoyer un message sur le channel Discord (fonction asynchrone donc attente que tout fonctionne)
                    except Exception as e: # avec le except on va capturer les erreurs si le message echoue; l'exception permet aussi de capturer les erreur et de les detecters
                        print(f"⚠ Erreur lors de l'envoi Discord : {e}") # si l'envoie du message échoue lors de la l75 alors on va recevoir un message d'erreur avec le texte + le contenue de l'erreur (e)

                    jeux_connus.extend(nouveaux) # mise à jour de la liste jeux_connus initialisé au début, où on ajoute le contenu de la liste nouveaux (les nouveaux jeux à gratter son automatiquement ajouter, permettant ainsi une màj à chaque lancement)
                    with open(FICHIER_JEUX, "w", encoding="utf-8") as f: # ouvre la variable fichier_jeux (qui contient le chemin du .json), en mode écriture (w pour write; le contenue sera ecrasé si le chemin existe et sinon le fichier sera créer par défaut) et le "encoding="utf-8" permet de spécifier l'encodage (ici en utf-8; comme le html: ça permet la prise en compte des chars. spéciaux notamment) ; le with permet de fermer le fichier à la fin du bloc d'instruction ; on assigne l'ouverture à f
                        json.dump(jeux_connus, f, ensure_ascii=False, indent=2) # convertie la liste jeux_connus en .json et écrit dans le fichier de la variable fichier_jeux; le "ensure_ascii=false" permet de garder les chars spéciaux (comme les accents ou la ponctuation); le indent=2 permet de faire un espace de 2 pour éviter de faire un "gros tas" dans le fichier
                else: # sinon
                    msg_aucun = "❌ Aucun nouveau jeu à gratter détecté aujourd'hui." # création de la variable msg_aucun qui contient le texte 
                    print(msg_aucun) # on écrit le contenu de la variable msg_aucun
                    await channel.send(msg_aucun) # on re utilise await pour verifier que la sycnhronisation est bonne et le bot envoie dans le channel définit au début, le contenu de msg_aucun

        except Exception as e: # on re capture les erreurs et on les attribue à e
            print(f"⚠ Erreur pendant la vérification : {e}") # pour le debogage, le bot écrit dans la console le texte + l'erreur (e)

        await asyncio.sleep(86400)  # cherche toutes les 24h de base, je l'ai mis pour un eventuelle déploiement sur un VPS; mais dans mon cas pour l'instant ce n'est pas utile car je l'éxécute en local (c'est pour ça ue j'ai ajouté les commandes sinon il tourne en permanence)

@bot.event # précision pour que le bot prenne en compte ce qui suit
async def on_ready(): # lorsqu'il est pret (que le serveur se synchronise, etc..)
    print(f"✅ Connecté en tant que {bot.user}") # dans la console il marque le texte + son nom complet (avec le #); c'est pratique pour le debogage, car si ce message s'affiche pas alors rien s'affiche
 
@bot.command() # déclare une commande pour un bot ici c'est le !start
@commands.is_owner() # restreint la commande à moi (le créateur du bot), aucun autres utilisateurs ne pourra donc gérer le bot, même s'il est sur un chanel spécifique
async def start(ctx): # fonction qui s'execute quand la command est appele (ctx verifie qui lance); ici c'est start
    global verif_active # indique que la commande va modifier la globale verif_active
    if not verif_active: # si la global verif_active n'est pas encore active
        verif_active = True # alors il la lance
        await ctx.send("✅ Lancement de la recherche de nouveau jeu à gratter.") # et il envoie un message dans le channel avec le contenu qui indique que la recherche se lance
        bot.loop.create_task(verifier_nouveaux_jeux()) # le bot lance alors la tache "verifier_nouveaux_jeux()" sans l'arreter  
    else: # sinon
        await ctx.send("⚠️ La recherche est déjà active. ⚠️") # ça veut dire qu'elle est déja active alors il envoie ce message

@bot.command() # déclare une commande pour un bot ici c'est le !stop
@commands.is_owner() #  restreint la commande à moi (le créateur du bot), aucun autres utilisateurs ne pourra donc gérer le bot, même s'il est sur un chanel spécifique
async def stop(ctx): # fonction qui s'execute quand la command est appelé (ctx verifie qui lance); ici c'est stop
    global verif_active # indique que la commande va modifier la globale verif_active
    if verif_active: # si la globale verif_active est lancée
        verif_active = False # alors il l'arrete 
        await ctx.send("🛑 Recherche arrêtée.") # il l'indique dans un message qu'il envoei sur le channel
    else: # sinon
        await ctx.send("⚠️ La recherche n'était pas active. ⚠️") # il indique que la recherche n'était déja pas active (donc il peut pas arreter quelque chose qui tourne pas)

@bot.command() # déclare une commande pour un bot ici c'est le !shutdown pour le déconnecter sans repasser par mon terminal 
@commands.is_owner() #  restreint la commande à moi (le créateur du bot)
async def shutdown(ctx):  # fonction qui s'execute quand la command est appele (ctx verifie qui lance); ici c'est shutdown pour la deconnexion (l'extinction)
    await ctx.send("👋 Je me déconnecte, à plus les addicts! 🎰") # il envoie un message de confirmation sur le channel pour confirmer qu'il se deconnecte bien
    await bot.close() # ferme le bot (le force à ce déconnecter)

bot.run(TOKEN) # permet le demarage du bot et donc l'enchainement des blocs du dessus; le systèpe lance le token de mon bot que je possède sur le portail developpeur de Discrod (le token est unique, il peut-être regénérer)

# pour lancer le bot et utiliser les commandes il faut juste ajouter avant la variable le prefix définit l29
# pour un hébérgement sur vps il faudra que l'app tourne en continue (l'app tourne mais le bot ne se lance que quand on lui dit de start) donc cela passera surement par un allumage console via une interface (à tester)
# je pense qu'on peut aussi simplifier la lecture/modification du json avec la màj d'une seule liste qui ecraserai le fichier à la fin de la boucle (simplifier celui déjà presents)