DTCEverywhere - Un outil de lecture hors-ligne et en CLI pour les citations de DansTonChat
========================================================================================

**DansTonChatEverywhere** (DTCE pour les intimes) est un petit module Python donnant accès à une commande, `dtceverywhere`, permettant de lire des citations de [DansTonChat](https://danstonchat.com/) en ligne de commande et hors-ligne.

Il permet aussi, de manière configurable, de colorer les pseudos dans les citations pour une lecture plus facile.

# Installation

DTCE n'est pas encore disponnible sur PyPi. Pour l'installer, vous devez télécharger ce dépôt et lancer le script d'installation.

    $ python3 setup.py install

# Avertissement

Le développeur de ce script n'est en aucune façon lié à DansTonChat. Les citations restent la propriété de leurs auteurs. De même, DansTonChat reste la propriété de Rémi Cieplicki.

Aussi, ce script est toujours en développement et ses commandes sont succeptibles de ne pas fonctionner correctement. Le cas échéant, n'hésitez pas à reporter le moindre bug dans le bugtracker. Merci !

# Utilisation

DTCE fourni une commande à tout faire : `dtceverywhere`.

Dans les versions futures, il sera possible de la lancer une seule fois. Pour l'instant, le seul mode disponnible est le mode interactif, à lancer avec `dtceverywhere -i`.

## Mode interactif

En mode interactif, un shell est disponnible pour lancer plusieurs commandes internes à DTCE.

### startdb

Cette commande permet de créer une base de données (avec SQLite) permettant de stocker les citations localement. **Elle doit être lancée une fois avant utilisation.**

### flushdb

Permet de vider complètement la base de données. Demande une confirmation.

### listlocals

Liste les IDs de toutes les citations enregistrées localement.

### dlquote <ID>

Télécharge une citation pour l'enregistrer dans la BDD locale. Prend son ID en argument (sans le `#`).

### dlpage <page>

Télécharge toutes les citations d'une page (parmis `https://danstonchat.com/latest/1.html`) localement. Prend le numéro de la page en argument.

### dlall

Télécharge **toutes** les citations de DansTonChat localement. **Ce processus est très chronophage et demande beaucoup de ressources au serveur de DansTonChat.** Pour cette raison, un délai de 5 secondes est prévu entre chaque page afin de limiter la charge du serveur. Demande une confirmation.

### viewquote <ID> / v <ID>

Comme `dlquote`, mais permet de lire la citation.

Alias : `v <ID>`

### random / r

Affiche une citation au hasard.

Alias : `r`

### random0 / r0

Affiche une citation au hasard, mais ayant un score supérieur à zéro.

Alias : `r0`

### ascii

Affiche le logo de DansTonChat en ASCII.

### reloadcfg

Recharge la configuration de DTCE et met à jour le statut de la connection réseau.

### version

Affiche la version installée de DTCE.

### exit / q / Ctrl+D

Quitte le shell interactif.

# Configuration

DTCE fourni un fichier de configuration (`dtce.cfg`) dans le même dossier que son code. Il permet notamment de désactiver l'utilisation des couleurs pour les pseudos.

# Coming soon

- Possibilité d'afficher la configuration actuelle.
- Possibilité de modifier la configuration à la volée.
- Cacher la liste des citations stockées localement.

# Licence

DTCE est distribué sous la licence AGPLv3, dont les termes sont disponnibles dans le fichier [LICENCE](LICENCE).
