![icon](Ressources/qtesseract5.svg)

# HizoTMDB

## Version Française

![02](https://user-images.githubusercontent.com/48289933/138588207-f381af95-e5e2-4ea8-ad11-67b935b52601.png)

Forum Ubuntu-fr : http://forum.ubuntu-fr.org/viewtopic.php?id=1508741

### Histoire :
Après avoir créé un système d'affichage de vignettes de fichiers matroska (mkv), il me fallait trouver facilement des affiches de qualité pour les ajouter dans les conteneurs mkv.

### Principe de base :
HizoTMDB est écrit en **python3 + Qt6** mais fonctionne avec **Qt5** pour **Linux**.

Téléchargement de masse d'affiches de film depuis le site The Movie Data Base en 2 étapes :
 - Recherche de films.
 - Clic sur le(s) film(s) voulu(s).

Pour fonctionner il faut obligatoirement un compte avec activation de l'API v4 : (https://www.themoviedb.org/settings/api?language=fr-FR)

Les affiches sont téléchargées en parallèle en fonction du nombre de thread du processeur.
Avec un bon processeur et une bonne connexion internet, il suffit de 5 secondes pour télécharger plus de 50 affiches.

### Installation :
 - Depuis le ppa : https://launchpad.net/~hizo/+archive/ubuntu/python3
 - Depuis le paquet Debian du ppa : https://launchpad.net/~hizo/+archive/ubuntu/python3/+packages?field.name_filter=hizo-tmdb
 - Depuis les sources compilées (seules les traductions le sont) ici même.
 - Depuis les sources après execution du fichier build.sh.

### Dépendances :
 - Lors de la création des sources via le fichier build.sh :
   - pyside6-lupdate / pylupdate6 / pylupdate5
     - pip install pyside6
     - pip install pyqt6
     - sudo apt install pyqt5-dev-tools
   - pyside6-lrelease / lrelease
     - pip install pyside6
     - sudo apt install qttools5-dev-tools
 - Pour l'utilisation du logiciel :
   - PySide6 / PyQt6 / PySide2 / PyQt5
     - pip install pyside6
     - pip install pyqt6
     - sudo apt install python3-pyqt5
     - sudo apt install python3-pyside2*
   - unidecode : 
     - pip install unidecode
     - sudo apt install python3-unidecode


### Configuration :
 - Jeton de l'API : **Obligatoire**.
 - Dossier de téléchargement des affiches.
 - Langues des affiches à télécharger, tous les films ne proposent pas toutes les langues.
 - Taille des vignettes affichées.
 - Nombre de page de la recherche.
 - Nombre de tentative de connexion à l'API.
 - Ouverture automatique du dossier de téléchargement.
 - Récupération automatique des affiches lorsque la recherche ne renvoie qu'un film.
 - Lancer automatiquement la recherche des films entrés en arguments.

### Recherches :
Les possibilités de recherches sont :
 - Une recherche exacte : _Iron Man_
 - Une recherche de titres commençants par : _Iron *_
 - Une recherche de titres finissants par : _* Man_
 - Une recherche très approximative : _*man*_
La casse n'est pas prise en compte.

*** ***

## English Version :
![01](https://user-images.githubusercontent.com/48289933/138588354-986b4f2a-55fc-4f87-8c37-906515a34e99.png)


### History:
After creating a thumbnail display system for matroska (mkv) files, I needed to easily find quality posters to add into the mkv containers.

### Basic principle:
HizoTMDB is written in **python3 + Qt6** but works with **Qt5** for **Linux**.

Mass download of movie posters from The Movie Data Base in 2 steps:
 - Search for movies.
 - Click on the movie(s) you want.

To work, you need an account with API v4 activation : (https://www.themoviedb.org/settings/api?language=fr-FR)

Posters are downloaded in parallel according to the number of processor threads.
With a good processor and a good internet connection, it only takes 5 seconds to download more than 50 posters.

### Installation:
 - From the ppa: https://launchpad.net/~hizo/+archive/ubuntu/python3
 - From the Debian package of the ppa : https://launchpad.net/~hizo/+archive/ubuntu/python3/+packages?field.name_filter=hizo-tmdb
 - From the compiled sources (only translations are) here.
 - From the sources after execution of the build.sh file.

### Dependencies:
 - When creating the sources via the build.sh file:
   - pyside6-lupdate / pylupdate6 / pylupdate5
     - pip install pyside6
     - pip install pyqt6
     - sudo apt install pyqt5-dev-tools
   - pyside6-lrelease / lrelease
     - pip install pyside6
     - sudo apt install qttools5-dev-tools
 - To use the :
   - PySide6 / PyQt6 / PySide2 / PyQt5
     - pip install pyside6
     - pip install pyqt6
     - sudo apt install python3-pyqt5
     - sudo apt install python3-pyside2*
   - unidecode : 
     - pip install unidecode
     - sudo apt install python3-unidecodeAprès avoir créé un système d'affichage de vignettes de fichiers matroska (mkv), il me fallait trouver facilement des affiches de qualité pour les ajouter dans les conteneurs mkv.

### Configuration:
 - API Token: **Mandatory**.
 - Poster download folder.
 - Languages of the posters to download, all the films do not propose all the languages.
 - Size of the thumbnails displayed.
 - Number of pages in the search.
 - Number of connection attempts to the API.
 - Automatic opening of the download folder.
 - Automatic recovery of posters when the search returns only one movie.
 - Automatically start the search for movies entered in arguments.

### Searches:
The search possibilities are:
 - An exact search : _Iron Man_
 - A search for titles beginning with : _Iron *_
 - A search for titles ending with : _* Man_
 - A very approximate search : _*man*_
Case is not taken into account.

