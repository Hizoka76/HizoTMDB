#!/bin/python3
# This Python file uses the following encoding: utf-8


# https://fr.wikipedia.org/wiki/Liste_des_codes_ISO_639-1
# https://www.drapeauxdespays.fr/registration

import requests

from PySide6.QtGui import QIcon, QPixmap

from PySide6.QtCore import QDir, QSettings


Configs = QSettings(QSettings.NativeFormat, QSettings.UserScope, "hizo-service-menus")
Token = Configs.value("hizo-tmdb/Token")

Headers = { 'Authorization': f"Bearer {Token}", 'Content-Type': "application/json;charset=utf-8" }
TimeOut = 3


while True:
    # Envoi de la requête à l'API de TMDB
    try:
        Requete = requests.get("https://api.themoviedb.org/3/configuration/languages", headers=Headers, timeout = TimeOut)

    # En cas d'échec de connexion, on relance la fonction
    except:
        continue

    # Si le code retour n'est pas 200, on relance la fonction
    if Requete.status_code != 200:
        continue

    break

# Ouverture du fichier des langues pour y écrire
with open("LanguageList.py", 'w') as out_file:
    # Début du fichier
    out_file.write("# Modules PySide\n")
    out_file.write("from PySide6.QtGui import QIcon\n\n")
    out_file.write("# List of the avalaible languages on TMDB\n")
    out_file.write("LanguageList = [\n")

    # Traitement du retour, la variable est rangée par nom de langue
    for Return in sorted(Requete.json(), key=lambda k: k['english_name']) :
        # Gestion du nom de la langue
        if Return['name']: Text = f"{Return['iso_639_1']} - {Return['english_name']} ({Return['name']})"
        else: Text = f"{Return['iso_639_1']} - {Return['english_name']}"

        # Gestion de l'icône
        if QDir().exists(f"Flags/{Return['iso_639_1']}.svg"): icon = f""", "icon": QIcon(QPixmap(":/Flags/{Return['iso_639_1']}.svg"))"""
        else: icon =""

        # Écriture de la ligne
        out_file.write(f"""    {{ "text": "{Text}", "data": "{Return['iso_639_1']}"{icon} }}, \n""")

    # Fin du fichier
    out_file.write("]\n")
