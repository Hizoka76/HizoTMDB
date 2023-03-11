#!/usr/bin/python3
# -*- coding: utf-8 -*-


####################################
## Importation des modules python ##
####################################
# unidecode : Sert à virer les accents pour les recherches
# requests : Sert à faire des requêtes http
# json : Sert à lire le retour des requêtes
# shutil : Permet d'enregistrer simplement les images

try:
    import importlib

except:
    exit("Warning: Impossible to find importlib module !")

for Module in ["requests", "shutil", "json", "unidecode"]:
    try:
        # Import des modules entiers
        globals()[Module] = importlib.import_module(f"{Module}")

    except:
        exit(f"Error: Impossible to find the {Module} module !")


################################
## Importation des modules Qt ##
################################
from ModulesQt import *


##############################################################################
## Raccourci permettant d'améliorer la lisibilité des lignes de traductions ##
##############################################################################
def timeNow():
    return QTime().currentTime().toString("HH:mm:ss")


#################################################################
## Classe des signaux de la classe travaillant en arrière plan ##
#################################################################
class ThreadSignals(QObject):
    # Message d'information à afficher
    Info = Signal(list)

    # Demande de création d'un bouton de film
    AddMovieButton = Signal(str, object)

    # Recherche d'une page d'un film terminée
    MovieFinished = Signal(object)

    # Recherche des posters d'un film terminée
    MoviePicturesFinished = Signal(object)

    # Affiche téléchargée
    DownloadPictureFinished = Signal(object)

    # Dossier en cours de téléchargement
    DownloadFolder = Signal(QDir)


#####################################################
## Classe lançant les téléchargements en parallèle ##
#####################################################
class ThreadActions(QRunnable):
    # https://www.pythonguis.com/tutorials/multithreading-pyqt-applications-qthreadpool/
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, *args, **kwargs):
        super(ThreadActions, self).__init__()

        ### Traductions
        self.Translations = {}
        self.Translations["ActionMissing"] = translate("ErrorMessage", "An error occurred while using the thread, it is missing the action.")
        self.Translations["ActionUnknow"] = translate("ErrorMessage", "An error occurred while using the thread, the action is unknown.")
        self.Translations["ArgMissing"] = translate("ErrorMessage", "An error occurred while using the {0} function, {1} is missing.", "{0} = function name, {1} = Argument name")
        self.Translations["SearchStarts"] = translate("InfoMessage", "Launching the search for the page n°{}.", "{} = Page Number")
        self.Translations["SearchPosters"] = translate("InfoMessage", "Search the images of the video id {}.", "{} = Movie id")
        self.Translations["FolderNotExists"] = translate("ErrorMessage", "The folder {} does not exist !", "{} = Folder path")
        self.Translations["PosterDownloaded"] = translate("InfoMessage", "{0} donwloaded into the folder {1}.", "{0} = Poster name, {1} = Download folder path")
        self.Translations["FolderCreation"] = translate("ErrorMessage", "Impossible to create the {} folder !", "{} = Folder path")
        self.Translations['ErrorDownloadPictures'] = translate("InfoMessage", "An error occurred while downloading this image,")
        self.Translations["MoviePictures"] = translate("InfoMessage", "An error occurred while searching for the images of the movie,")
        self.Translations["TryAgain"] = translate("InfoMessage", "try again...")
        self.Translations["TryMax"] = translate("InfoMessage", "max number of try reached.")
        self.Translations["ErrorMovies"] = translate("InfoMessage", "An error occurred during the search for the movie,")
        self.Translations["ErrorSearch"] = translate("InfoMessage", "The search for the movie returns a code other than 200,")

        ### Chargement des signaux
        self.Signals = ThreadSignals()

        ### Variable stoppante
        self.StopThread = False

        ### Vérification de l'action
        if not kwargs.get('Action'):
            self.Signals.Info.emit([timeNow(), 'ERROR', "ThreadActions", self.Translations["ActionMissing"]])
            self.Action = None

        elif kwargs.get('Action') not in ["Movie", "MoviePictures", "DownloadPicture"]:
            self.Signals.Info.emit([timeNow(), 'ERROR', "ThreadActions", self.Translations["ActionUnknow"]])
            self.Action = None

        else:
            self.Action = kwargs['Action']


        ### Vérification des arguments communs
        for Arg in ['MovieName', 'MoviePage', 'TryMax', 'TimeOut', 'Headers']:
            if not kwargs.get(Arg):
                self.Signals.Info.emit([timeNow(), 'ERROR', "ThreadActions", self.Translations["ArgMissing"].format("Movie", Arg)])

                # Impossible de foutre un return ici, le run est lancé quand même
                self.Action = None

        if self.Action:
            self.MovieName = kwargs['MovieName']
            self.MoviePage = kwargs['MoviePage']
            self.TryMax = kwargs['TryMax']
            self.TimeOut = kwargs['TimeOut']
            self.Headers = kwargs['Headers']


        ### Vérifications des arguments
        # Vérifie les présences des arguments pour l'action DownloadPictures
        if self.Action == "Movie":
            for Arg in ['IncludeAdultSearch', 'Language', 'SourcesSearch', 'DlFolder']:
                if not kwargs.get(Arg):
                    self.Signals.Info.emit([timeNow(), 'ERROR', "ThreadActions", self.Translations["ArgMissing"].format("Movie", Arg)])
                    self.Action = None

            self.IncludeAdultSearch = kwargs['IncludeAdultSearch']
            self.Language = kwargs['Language']
            self.SourcesSearch = kwargs['SourcesSearch']
            self.DlFolder = kwargs['DlFolder']

        # Vérifie les présences des arguments pour l'action MoviePictures
        elif self.Action == "MoviePictures":
            for Arg in ['MovieId', 'DlFolder', 'Widget', 'Source', 'ImagesLanguages', 'ImagesTypes']:
                if not kwargs.get(Arg):
                    self.Signals.Info.emit([timeNow(), 'ERROR', "ThreadActions", self.Translations["ArgMissing"].format("MoviePictures", Arg)])
                    self.Action = None

            self.MovieId = kwargs['MovieId']
            self.DlFolder = kwargs['DlFolder']
            self.Widget = kwargs['Widget']
            self.Source = kwargs['Source']
            self.InfoSource = f"{self.MovieName}-{self.MovieId}"
            self.ImagesTypes = kwargs['ImagesTypes']
            self.ImagesLanguages = kwargs['ImagesLanguages']


        # Vérifie les présences des arguments pour l'action DownloadPictures
        elif self.Action == "DownloadPicture":
            for Arg in ['DlFolder', 'Picture']:
                if not kwargs.get(Arg):
                    self.Signals.Info.emit([timeNow(), 'ERROR', "ThreadActions", self.Translations["ArgMissing"].format("DownloadPictures", Arg)])
                    self.Action = None

            self.DlFolder = kwargs['DlFolder']
            self.Picture = kwargs['Picture']

            self.MovieDlFolder = self.DlFolder
            if kwargs.get('MovieDlFolder'):
                self.MovieDlFolder = kwargs['MovieDlFolder']

            self.Data = None
            if kwargs.get('Data'):
                self.Data = kwargs['Data']

            self.Widget = None
            self.InfoSource = self.MovieName

            if kwargs.get('Widget'):
                self.Widget = kwargs['Widget']
                self.InfoSource = f"{self.MovieName}-{kwargs['Widget'].id}"


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def run(self):
        # Stoppe le travail si clic sur le bouton stop
        if self.StopThread:
            return

        # Lancement de la fonction demandée
        if self.Action == "Movie":
            self.Movie()

        elif self.Action == "MoviePictures":
            self.MoviePictures()

        elif self.Action == "DownloadPicture":
            self.DownloadPictures()


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def stopAllNow(self):
        """Fonction de mise à jour de la variable stoppante."""
        self.StopThread = True


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def Movie(self):
        """Fonction de recherche de films."""
        # Prise en charge de la recherche de contenu adulte, true si valeur = 1 ou 2
        IncludeAdult = "false"
        if self.IncludeAdultSearch:
            IncludeAdult = "true"

        # Liste des films regroupés si plusieurs pages
        AllMovies = []

        # Nettoyage du nom et des accents
        NameFinded = self.MovieName.lower().replace("*", "")
        NameFinded = unidecode.unidecode(NameFinded)

        # Message informatif
        self.Signals.Info.emit([timeNow(), 'INFO', self.MovieName, self.Translations["SearchStarts"].format(self.MoviePage)])

        # Langue du texte
        Language = "en_US"
        if self.Language == "Français":
            Language = "fr-FR"

        # Variable indiquant si la boucle s'est terminé à TryMax
        TryMaxReached = True

        # Boucle au maximum au nombre de tentative
        for Try in range(self.TryMax):
            # Stoppe le travail si clic sur le bouton stop
            if self.StopThread:
                return

            # Envoi de la requête à l'API de TMDB
            try:
                if "movie" in self.SourcesSearch and "tv" in self.SourcesSearch:
                    Source = "multi"

                elif "movie" in self.SourcesSearch:
                    Source = "movie"

                elif "tv" in self.SourcesSearch:
                    Source = "tv"

                Requete = requests.get("https://api.themoviedb.org/3/search/{}?language={}&query={}&page={}&include_adult={}".format(Source, Language, NameFinded.replace(" ", "%20"), self.MoviePage, IncludeAdult), headers=self.Headers, timeout=self.TimeOut)

                # Si le code retour n'est pas 200, on relance la fonction
                if Requete.status_code != 200:
                    self.Signals.Info.emit([timeNow(), 'ERROR', self.MovieName, "Page {} {} {}".format(self.MoviePage, self.Translations['ErrorSearch'], self.Translations['TryAgain'])])
                    continue

            # En cas d'échec de connexion, on relance la fonction
            except:
                self.Signals.Info.emit([timeNow(), 'ERROR', self.MovieName, "Page {} {} {}".format(self.MoviePage, self.Translations['ErrorMovies'], self.Translations['TryAgain'])])
                continue

            # Stoppe la boucle si tout est bien passé
            TryMaxReached = False
            break


        # Si le nombre de tentative a été atteint, arrêt complet de la recherche
        if TryMaxReached:
            self.Signals.Info.emit([timeNow(), 'ERROR', self.MovieName, "Page {} {} {}".format(self.MoviePage, self.Translations['ErrorMovies'], self.Translations['TryMax'])])
            self.Signals.MovieFinished.emit([{"NbMovie": 0, "MovieName": self.MovieName, "MoviePage": self.MoviePage}])
            return

        # Liste des films correspondants
        AllMovies = []

        # Remplissage de la liste des films retournés
        for Movie in Requete.json()['results']:
            # Stoppe le travail si clic sur le bouton stop
            if self.StopThread:
                return

            # Saute l'élément si c'est une personne dans le cas de la recherche multiple
            if Movie.get('media_type') == 'person':
                continue

            # Variable permettant de respecter de la demande de contenu adulte
            MovieAdultOK = False

            # Si on ne veut que des films adultes
            if self.IncludeAdultSearch == 2:
                if not Movie["adult"]:
                    continue

            # Dans le cas des series, ce n'est pas title mais name
            if Movie.get("name") and not Movie.get("title"):
                Movie["title"] = Movie["name"]

            if Movie.get("original_name") and not Movie.get("original_title"):
                Movie["original_title"] = Movie["original_name"]

            for Title in ["title", "original_title"]:
                # Si le titre n'existe pas
                if not Movie.get(Title):
                    continue

                # Nettoyage du nom
                TitleFinded = Movie[Title].lower()
                TitleFinded = unidecode.unidecode(TitleFinded)

                # Si l'étoile est utilisée dans la recherche
                if "*" in self.MovieName:
                    # Si le nom est entouré, on le reprend
                    if self.MovieName[0] != "*" or self.MovieName[-1] != "*":
                        # Si le nom doit commencer par... (Iron*)
                        if self.MovieName[-1] == "*" and not TitleFinded.startswith(NameFinded):
                            continue

                        # Si le nom doit finir par... (Iron*)
                        if self.MovieName[0] == "*" and not TitleFinded.endswith(NameFinded):
                            continue

                # Sinon, c'est qu'on veut le nom exacte
                else:
                    if NameFinded != TitleFinded:
                        continue

                # Indique qu'il faut reprendre le film et arrêter la boucle de comparaison des noms
                MovieAdultOK = True
                break


            # Si on ne doit pas reprendre le film, on le saute
            if not MovieAdultOK:
                continue

            # Ne traite pas les films sans poster
            if not Movie.get('poster_path'):
                continue

            # Utilisation d'une date par défaut bidon pour le tri
            if not Movie.get('release_date'):
                Movie['release_date'] = "9999-99-99"

            # Ajout du film à la liste
            AllMovies.append(Movie)


        # Nombre de film renvoyé
        NbMovie = len(AllMovies)

        # Si aucun retour, on arrête là
        if not NbMovie:
            self.Signals.MovieFinished.emit([{"NbMovie": 0,
                                              "MovieName": self.MovieName,
                                              "MoviePage": self.MoviePage}])

            return

        MovieReturn = []

        # for Index, Movie in enumerate(sorted(AllMovies, key=lambda k: (k['release_date'], k['title']))):
        for Index, Movie in enumerate(AllMovies):
            # Stoppe le travail si clic sur le bouton stop
            if self.StopThread:
                return

            if not Movie.get("media_type"):
                if "movie" in self.SourcesSearch:
                    Movie["media_type"] = "movie"

                elif "tv" in self.SourcesSearch:
                    Movie["media_type"] = "tv"

            MovieReturn.append({"DlFolder": self.DlFolder,
                                "Picture": f"https://image.tmdb.org/t/p/w500{Movie['poster_path']}",
                                "Data": Movie,
                                "NbMovie": NbMovie,
                                "MovieName": self.MovieName,
                                "MoviePage": self.MoviePage,
                                "TryMax": self.TryMax,
                                "Headers": self.Headers,
                                "TimeOut": self.TimeOut
                                })

        self.Signals.MovieFinished.emit(MovieReturn)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ### Fonction de recherche des images d'un film
    def MoviePictures(self):
        # Recherche des posters du film
        self.Signals.Info.emit([timeNow(), 'INFO', self.InfoSource, self.Translations["SearchPosters"].format(self.MovieId)])

        # Variable indiquant si la boucle s'est terminé à TryMax
        TryMaxReached = True

        # Boucle au maximum au nombre de tentative
        for Try in range(self.TryMax):
            # Stoppe le travail si clic sur le bouton stop
            if self.StopThread:
                return

            # Envoi de la requête à l'API de TMDB
            try:
                Requete = requests.get("https://api.themoviedb.org/3/{}/{}/images?language=fr-FR&include_image_language={}".format(self.Source, self.MovieId, self.ImagesLanguages), headers=self.Headers, timeout=self.TimeOut)

                # Si le code retour n'est pas 200, on relance la fonction
                if Requete.status_code != 200:
                    self.Signals.Info.emit([timeNow(), 'ERROR', self.InfoSource, "{} {}".format(self.Translations['MoviePictures'], self.Translations['TryAgain'])])
                    continue

            # En cas d'échec de connexion, on relance la fonction
            except:
                self.Signals.Info.emit([timeNow(), 'ERROR', self.InfoSource, "{} {}".format(self.Translations['MoviePictures'], self.Translations['TryAgain'])])
                continue

            # Stoppe la boucle si tout est bien passé
            TryMaxReached = False
            break

        # Si le nombre de tentative a été atteint, arrêt complet de la recherche
        if TryMaxReached:
            self.Signals.Info.emit([timeNow(), 'ERROR', self.InfoSource, "{} {}".format(self.Translations['MoviePictures'], self.Translations['TryMax'])])

            self.Signals.MoviePicturesFinished.emit([{"DlFolder": self.DlFolder,
                                                      "MovieDlFolder": self.DlFolder,
                                                      "MovieName": self.MovieName,
                                                      "MoviePage": self.MoviePage,
                                                      "Widget": self.Widget,
                                                      "NbMovie": 0}])

            return

        ImagesReturn = []

        for ImagesType in self.ImagesTypes:
            # S'il n'y aura pas d'image de ce type, on saute
            if not len(Requete.json()[ImagesType]):
                continue

            # Variable permettant de supprimer le dossier en cas d'annulation
            self.Signals.DownloadFolder.emit(self.DlFolder)

            # S'il n'y a qu'un type, pas de sous dossier
            if len(self.ImagesTypes) == 1:
                if not self.DlFolder.exists():
                    if not QDir().mkpath(self.DlFolder.absolutePath()):
                        self.Signals.Info.emit([timeNow(), 'ERROR', self.InfoSource, self.Translations['FolderCreation'].format(self.DlFolder.absolutePath())])
                        return

                DlFolder = self.DlFolder

            # Sinon création de sous dossiers
            else:
                AbsoluePath = self.DlFolder.absolutePath() + "/" + ImagesType

                if not QDir().mkpath(AbsoluePath):
                    self.Signals.Info.emit([timeNow(), 'ERROR', self.InfoSource, self.Translations['FolderCreation'].format(AbsoluePath)])
                    return

                DlFolder = QDir(AbsoluePath)

            for Poster in Requete.json()[ImagesType]:
                # Stoppe le travail si clic sur le bouton stop
                if self.StopThread:
                    return

                ImagesReturn.append({"DlFolder": DlFolder,
                                     "MovieDlFolder": self.DlFolder,
                                     "Picture": f"https://image.tmdb.org/t/p/original{Poster['file_path']}",
                                     "MovieName": self.MovieName,
                                     "MoviePage": self.MoviePage,
                                     "TryMax": self.TryMax,
                                     "Headers": self.Headers,
                                     "TimeOut": self.TimeOut,
                                     "Widget": self.Widget
                                     })

        self.Signals.MoviePicturesFinished.emit(ImagesReturn)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ## Fonction de téléchargement des images
    def DownloadPictures(self):
        DlFolderPath = self.DlFolder.absolutePath()
        PictureName = self.Picture.split("/")[-1]

        if not self.DlFolder.exists():
            self.Signals.Info.emit([timeNow(), 'ERROR', self.InfoSource, self.Translations["FolderNotExists"].format('ERROR', DlFolderPath)])
            self.Signals.DownloadPictureFinished.emit({"MovieName": self.MovieName, "MoviePage": self.MoviePage, "DlFolder": self.MovieDlFolder, "Widget": self.Widget})
            return

        # Variable indiquant si la boucle s'est terminé à TryMax
        TryMaxReached = True

        # Boucle au maximum au nombre de tentative
        for Try in range(self.TryMax):
            # Stoppe le travail si clic sur le bouton stop
            if self.StopThread:
                return

            # Envoi de la requête à l'API de TMDB
            try:
                Requete = requests.get(self.Picture, headers=self.Headers, timeout=self.TimeOut, stream=True)

                # Si le code retour n'est pas 200, on relance la fonction
                if Requete.status_code != 200:
                    self.Signals.Info.emit([timeNow(), 'ERROR', self.InfoSource, "{}: {} {}".format(PictureName, self.Translations['ErrorDownloadPictures'], self.Translations['TryAgain'])])
                    continue

            # En cas d'échec de connexion, on relance la fonction
            except:
                self.Signals.Info.emit([timeNow(), 'ERROR', self.InfoSource, "{}: {} {}".format(PictureName, self.Translations['ErrorDownloadPictures'], self.Translations['TryAgain'])])
                continue

            # Stoppe la boucle si tout est bien passé
            TryMaxReached = False
            break

        # Si le nombre de tentative a été atteint, arrêt complet de la recherche
        if TryMaxReached:
            self.Signals.Info.emit([timeNow(), 'ERROR', self.InfoSource, "{}: {} {}".format(PictureName, self.Translations['ErrorDownloadPictures'], self.Translations['TryMax'])])

        # Si tout est OK
        else:
            # Stoppe le travail si clic sur le bouton stop
            if self.StopThread:
                return

            # Le try permet d'éviter des erreurs lors de l'annulation
            try:
                # Sauvegarde du poster sur le disque
                with open(f"{DlFolderPath}/{PictureName}", 'wb') as out_file:
                    shutil.copyfileobj(Requete.raw, out_file)

            except:
                return

            # Signaux pas forcément utilisés
            self.Signals.AddMovieButton.emit(self.MovieName, self.Data)
            self.Signals.Info.emit([timeNow(), 'INFO_OK', self.InfoSource, self.Translations["PosterDownloaded"].format(PictureName, DlFolderPath)])

        self.Signals.DownloadPictureFinished.emit({"MovieName": self.MovieName, "MoviePage": self.MoviePage, "DlFolder": self.MovieDlFolder, "Widget": self.Widget})
