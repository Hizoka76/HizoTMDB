#!/usr/bin/python3
# -*- coding: utf-8 -*-


################################
## Importation des modules Qt ##
################################
from ModulesQt import *



#############################################################################
class QToolButtonCustom(QToolButton):
    def __init__(self, parent=None, icon=None, temp=None, ImageSize=200, downloadFolder=None, data=None):
        # Ne pas utiliser super().__init__(*args, **kwargs) car QToolButton ne connaît pas mes variables
        super(QToolButtonCustom, self).__init__()

        # Variables
        self.TemporaryImage = icon
        self.data = data
        self.id = data.get("id")
        self.Source = data.get("media_type")
        self.Title = data.get("title")
        OriginalTitle = data.get("original_title")
        ToolTipText = data.get("overview")
        ReleaseDate = data.get("release_date")
        self.generateDownloadFolder(downloadFolder)

        if OriginalTitle and self.Title and self.Title != data.get('original_title'):
            ToolTipTitle = f"{OriginalTitle}<br>{self.Title}"
        else:
            ToolTipTitle = self.Title

        # Config par défaut
        self.setEnabled(False)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        # Gestion de la taille du bouton en fonction de celle de l'image'
        self.setMinimumWidth(ImageSize)
        self.setMinimumHeight(ImageSize)
        self.setMaximumWidth(ImageSize)
        self.setIconSize(QSize(ImageSize, ImageSize))

        # Gestion du texte
        self.setText(f"{self.Source} {self.id}\n{self.Title}\n{OriginalTitle}\n{ReleaseDate}")

        palette = self.palette()

        if self.Source.lower() == "tv":
            palette.setColor(QPalette.ButtonText, Qt.darkGreen)
        else:
            palette.setColor(QPalette.ButtonText, Qt.darkBlue)

        self.setPalette(palette)


        # Gestion de l'icône
        if icon:
            self.setIcon(QIcon(icon))

        # Gestion de l'info bulle
        if self.Title and ToolTipText:
            self.setToolTip(f"<div style='width: 500px;'><b>{self.Title}</b><br>-----<br>{ToolTipText}</div>")

        elif self.Title:
            self.setToolTip(f"<div style='width: 500px;'><b>{self.Title}</b></div>")

        # Chargement des textes de base
        self.updateLang()


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateLang(self):
        """Fonction permettant de mettre à jour les textes lors des changements de langue."""
        # Traductions
        self.Translations = {}
        self.Translations["DownloadAction"] = translate("QToolButtonCustom", "Open the download folder")
        self.Translations["ViewImageAction"] = translate("QToolButtonCustom", "Open the temporary poster")
        self.Translations["GoWebSiteAction"] = translate("QToolButtonCustom", "Go to the movie page on TMDB")
        self.Translations["setStatusTip"] = translate("QToolButtonCustom", "There is a context menu with right click.")

        # Maj du status tip
        self.setStatusTip(self.Translations["setStatusTip"])

        # Recréation du menu
        self.menuCreation()


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def menuCreation(self):
        """Création du context menu."""
        self.contextMenu = QMenu(self)

        DownloadAction = QAction(QIcon.fromTheme("folder-download", QIcon("Ressources:folder-download.svg")), self.Translations["DownloadAction"], self.contextMenu)
        DownloadAction.triggered.connect(self.openDownloadFolder)
        self.contextMenu.addAction(DownloadAction)

        ViewImageAction = QAction(QIcon.fromTheme("viewimage", QIcon("Ressources:viewimage.svg")), self.Translations["ViewImageAction"], self.contextMenu)
        ViewImageAction.triggered.connect(self.openTemporaryPoster)
        self.contextMenu.addAction(ViewImageAction)

        self.contextMenu.addSeparator()

        GoWebSiteAction = QAction(QIcon.fromTheme("link", QIcon("Ressources:link.svg")), self.Translations["GoWebSiteAction"], self.contextMenu)
        GoWebSiteAction.triggered.connect(lambda: QDesktopServices.openUrl(QUrl(f"https://www.themoviedb.org/{self.Source}/{self.id}")))
        self.contextMenu.addAction(GoWebSiteAction)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def openTemporaryPoster(self):
        """Fonction ouvrant le poster temporaire."""
        if QDir().exists(self.TemporaryImage):
            temp = QDesktopServices.openUrl(QUrl(self.TemporaryImage))


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def openDownloadFolder(self):
        """Fonction ouvrant le dossier de téléchargement."""
        if QDir().exists(self.downloadFolder):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.downloadFolder))


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def generateDownloadFolder(self, downloadFolder):
        """Fonction générant un nom de dossier de téléchargement."""
        self.downloadFolder = QTemporaryDir(downloadFolder + "/" + self.Title).path()


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def mousePressEvent(self, event):
        """Fonction de récupération des touches souris utilisées."""
        # Affichage du menu au clic droit
        if event.button() == Qt.RightButton:
            if QtVersion == 6:
                # PySide6
                self.contextMenu.exec(QCursor.pos())

            else:
                # PySide2
                self.contextMenu.exec_(QCursor.pos())

        # Accepte l'événement
        super().mousePressEvent(event)
