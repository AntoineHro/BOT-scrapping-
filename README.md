## Descriptif README.
### 🚨 ** J'ai commenté tout le code directement à l'interieur du fichier, il n'y aura donc ici que l'explication et la procédure d'installation. ** 🚨
# But du BoT:
Le boT va regarder si sur le site de la fdj il y a de nouveaux jeux à gratter et envoie un message sur un channel Discord. Seul le créateur de l'application sur le portail Developpeur de Discord peut jouer les commandes.
<br>
Le but de ce boT est sur le long terme de l'héberger sur un VPS (il est configuré pour).
Je travaille aussi sur une eventuelle optimisation de la recherche et des commandes (ajout).
<br>

# Prérequis:

Être admin sur le serveur où l'on veut ajouter le boT.
<br> Avoir créé une apllication sur le portail développeur.
<br> Ajouter cette application sur votre serveur via le portail de l'application Discord.
<br> Télecharger les 2 fichiers du projets (placez les dans un répertoire où vous voulez)

# Descriptif du contenu du dépôt:

<mark>BoT_fdj</mark> 
	Code source du boT
<br>
<mark>jeux_connus.json</mark> 
  Contient un tableau avec les jeux connus (évite le double enregistrement)
<br>

[Les commandes](#commandes)

# <mark>Procédure d'installation:</mark> 
# I-Ajout du token de l'application sur le boT
<br> Pour ce faire nous allons d'abord nous connecter sur le portail développeur Discord.
CLiquez sur l'application que l'on veut ajouter.
<br> Allez dans la section Bot
<br> Faire reset Token et copier celui fournit (attention celui-ci est unique si vous le modifier plus tard, pensez à le modifier dans le code)
<br> Ouvrir le fichier bot_fdj.py avec un ide (VScode ou notepad ++)
<br> Modifier la variable TOKEN (L8) en remplaçant le token existant par celui de votre application.
<br> <img src="https://antoine-haro.fr/"  width="100"/>

# II-Ajout de l'id du channel sur le boT
<br> Il faut d'abbord activer l'option développeur sur votre application Discord (accessible depuis les paramètres.
<br> Une fois l'option activée faites click droit sur le channel où vous voulez que le bot s'exécute.
<br> Cliquez sur "Copiez l'id du salon."
<br> Ouvrir le fichier bot_fdj.py
<br> Modifier la variable CHANNEL_ID (L9) en remplaçant sa valeur par l'id du salon.
<br> <img src="https://antoine-haro.fr/"  width="100"/>

# III-Lancement du boT par ide
<br> Rendez vous sur votre ide (de préférence VScode)
<br> Sélectionnez le bot_fdj.py de sorte à voire le code source.
<br> Appuyer sur la flêche de lancement en haut à droite (ça va ouvrir un terminal)
<br> <img src="https://antoine-haro.fr/"  width="100"/>

# IV-Lancement du boT par terminal
<br> Ouvrez un terminal 
<br> Déplacez vous jusqu'à votre répertoire où ce situe le bot
<br> Rentrez la commande python3 bot_fdj.py

# commandes
Les commandes sont les suivantes:
<br> !start == démarre la recherche (fais une requête web)
<br> !stop == arrête la recherche: comme dit précedement le bot est fait pour être déployé sur un vps donc qui tourne en permanence (1 requête toutes les 24 heures) donc pour arrêter cette boucle il faut jouer cette commande
<br> !shutdown == déconnecte le bot et le désactive (kill), utile car comme j'ai pas fais de commande de start (lancement manuel depuis le terminal) ça m'évite de revenir dessus
