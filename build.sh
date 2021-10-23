#! /bin/bash

# set -e
# set -v

# Fichier servant :
# - Lors de la création du paquet sources
# - Après la création d'un paquet source, les fichiers sont supprimés, il faut donc les recréer


### Gestion de l'emplacement
chemin="$(cd "$(dirname "$0")";pwd)"
cd "${chemin}"


### Mise à jour des fichiers ts : -noobsolete
if [[ $(which "pyside6-lupdate") ]]
then
    pyside6-lupdate *.py QWidgetsCustom/*.py -ts Languages/hizo-tmdb_fr_FR.ts Languages/hizo-tmdb_en_EN.ts

elif [[ $(which "pylupdate6") ]]
then
    pylupdate6 *.py QWidgetsCustom/*.py -ts Languages/hizo-tmdb_fr_FR.ts Languages/hizo-tmdb_en_EN.ts

elif [[ $(which "pylupdate5") ]]
then
    pylupdate5 *.py QWidgetsCustom/*.py -ts Languages/hizo-tmdb_fr_FR.ts Languages/hizo-tmdb_en_EN.ts

else
    echo "cannot find 'lupdate'"
    exit 1
fi


### Conversion des fichiers ts en qm
if [[ $(which pyside6-lrelease) ]]
then
    pyside6-lrelease Languages/*.ts

elif [[ $(which lrelease) ]]
then
    lrelease Languages/*.ts

elif [[ -e "/usr/lib/x86_64-linux-gnu/qt5/bin/lrelease" ]]
then
    /usr/lib/x86_64-linux-gnu/qt5/bin/lrelease Languages/*.ts

elif [[ -e "/usr/lib/i386-linux-gnu/qt5/bin/lrelease" ]]
then
    /usr/lib/i386-linux-gnu/qt5/bin/lrelease Languages/*.ts

else
    echo "cannot find 'lrelease'"
    exit 1
fi
