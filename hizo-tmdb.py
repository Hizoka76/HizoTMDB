#!/usr/bin/python3
# -*- coding: utf-8 -*-


# News : prise en compte du cas où il n'y a aucune image à dl


####################################
## Importation des modules python ##
####################################
# os : Pour le reboot, facultatif
# requests : Pour toutes les requêtes http au site tmdb
# shutil : Sert à créer les images et dans le try de chargement de Qt
# time : Sert à ne pas aller trop vite
# json : Sert à lire le retour de la requête des langues
# functools : Permet de surcharger les connect
# importlib : Sert à charger les modules via des strings
# random : Sert à déterminer des couleurs aléatoires

try:
    import importlib

except:
    exit("Warning: Impossible to find importlib module !")


for Module in ["sys", "requests", "shutil", "time", "functools", "json", "random"]:
    try:
        # Import des modules entiers
        globals()[Module] = importlib.import_module(f"{Module}")

    except:
        exit(f"Error: Impossible to find the {Module} module !")


# Pour le reboot, facultatif
try:
    import os

except:
    print("Warning: Impossible to find the os module ! Impossible to reboot with the right click on exit button.")
    pass


############################################################
## Importation des modules Qt depuis le fichier ModulesQt ##
############################################################
try:
    from ModulesQt import *

except:
    # Message d'erreur
    Text = """Impossible to find PySide6 / PyQt6 / PySide2 / PyQt5.

You need to install one of them (eg with Ubuntu):
    PySide6: pip3 install PySide6
    PyQt5: pip3 install PyQt6
    PySide2: sudo apt install python3-pyside2
    PyQt5: sudo apt install python3-pyqt5"""

    # Affichage du texte dans le terminal
    print(Text)

    # Si os a pu être chargé
    if "os" in globals():
        # Si kdialog est installé, on l'utilise pour afficher le message
        if shutil.which("kdialog"):
            os.popen(f"""kdialog --title "Hizo-TMDB" --error "{Text}" """)

        # Si zenity est installé, on l'utilise pour afficher le message
        elif shutil.which("zenity"):
            # f"" interdit l'utilisation de '\' entre {}
            os.popen(f"""zenity --error --no-wrap --title "Hizo-TMDB" --text "{Text}" """)

    exit(1)


###########################################
## Importation des modules personnalisés ##
###########################################
from QWidgetsCustom.QCheckComboBox import QCheckComboBox
from QWidgetsCustom.QToolButtonCustom import QToolButtonCustom
from QWidgetsCustom.QScrollAreaCustom import QScrollAreaCustom
from QWidgetsCustom.QPushQuitButton import QPushQuitButton
from QWidgetsCustom.QFlowLayout import QFlowLayout
from QWidgetsCustom.QDialogWhatsUp import QDialogWhatsUp
from QWidgetsCustom.QSliderCustom import QSliderCustom
from QWidgetsCustom.QTabWidgetCustom import QTabWidgetCustom
from QWidgetsCustom.QThreadActions import ThreadActions


##############################################################################
## Raccourci permettant d'améliorer la lisibilité des lignes de traductions ##
##############################################################################
def timeNow():
    return QTime().currentTime().toString("HH:mm:ss")



##########################################################################
## Classe permettant de pas attendre avant l'affichage des infos bulles ##
##########################################################################
class MyProxyStyle(QProxyStyle):
    def styleHint(self, hint, option = None, widget = None, returnData = None):
        # On peut ajouter des conditions de fonctionnement sur certains widgets uniquement
        if hint == QStyle.SH_ToolTip_WakeUpDelay:
            return 0

        return QProxyStyle().styleHint(hint, option, widget, returnData)




#############################################################################
class WinHizoTMDB(QMainWindow):
    """Fenêtre de configuration du code."""
    # Signal permettant de descendre dans le Scroll des barres de dl
    goScrolltoBottom = Signal()

    # Signal indiquant aux threads d'arrêter
    stopWork = Signal()


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, Parent=None):
        super().__init__(Parent)

        ### Variables
        self.AutoDlToolButton = None
        self.MoviesTab = {}

        # Gestionnaire des actions, ne pas utiliser globalInstance ! Sinon ça freeze pendant le travail...
        self.GestionnaireActions = QThreadPool()

        # Liste des ProgressBar
        self.ProgressBarWidgets = {}

        QCheckComboBoxIcons = {
            "Copy": QIcon.fromTheme("edit-select-text", QIcon("Ressources:edit-select-text.svg")),
            "Undo": QIcon.fromTheme("edit-undo", QIcon("Ressources:edit-undo.svg")),
            "Redo": QIcon.fromTheme("edit-redo", QIcon("Ressources:edit-redo.svg")),
            "AllCheck": QIcon.fromTheme("edit-select-all", QIcon("Ressources:edit-select-all.svg")),
            "AllUncheck": QIcon.fromTheme("edit-select-none", QIcon("Ressources:edit-select-none.svg")),
            "DefaultValues": QIcon.fromTheme("edit-reset", QIcon("Ressources:edit-reset.svg"))
            }

        # Connexion du signal
        self.goScrolltoBottom.connect(self.ScrolltoBottom)


        ### Fenêtre
        self.setWindowFlags(Qt.WindowTitleHint)
        self.setMinimumWidth(840)
        self.setMinimumHeight(400)
        self.resize(Global['WinWidth'], Global['WinHeight'])
        self.setWindowTitle("{} v{}".format(QCoreApplication.applicationName(), QCoreApplication.applicationVersion()))
        self.setAttribute(Qt.WA_DeleteOnClose)

        # Acceptation du glisser déposer
        self.setAcceptDrops(True)

        # Status Bar
        self.StatusBar = QStatusBar(self)
        self.setStatusBar(self.StatusBar)

        # Ajout d'un bouton quitter dans la status bar
        self.ButtonQuit = QPushQuitButton(self.StatusBar)
        self.ButtonQuit.setIcon(QIcon.fromTheme("application-exit", QIcon("Ressources:application-exit.svg")))
        self.ButtonQuit.clicked.connect(self.close)

        if "os" in globals():
            self.ButtonQuit.rebootSignal.connect(self.rebootEvent)

        self.StatusBar.addPermanentWidget(self.ButtonQuit)
        self.StatusBar.setSizeGripEnabled(False)

        # Ajout du bouton A propos dans la status bar
        self.AboutButton = QPushButton()
        self.AboutButton.setIcon(QIcon.fromTheme("help-about", QIcon("Ressources:application-exit.svg")))
        self.AboutButton.clicked.connect(self.About)
        self.StatusBar.addWidget(self.AboutButton)

        # Layout principal
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        WinVLayout = QVBoxLayout(self.centralwidget)

        # Grand splitter
        self.WinSplitter = QSplitter(Qt.Vertical, self.centralwidget)
        self.WinSplitter.setChildrenCollapsible(False)
        WinVLayout.addWidget(self.WinSplitter)

        ### Partie haute avec le splitter et son layout
        self.TopSplitter = QSplitter(self.WinSplitter)
        self.TopSplitter.setChildrenCollapsible(False)

        ### Gestion de la box des noms de film à rechercher
        # Box
        self.MoviesSearchedBox = QGroupBox(self.TopSplitter)
        self.MoviesSearchedBox.setMinimumWidth(200)
        MoviesSearchedVLayout = QVBoxLayout(self.MoviesSearchedBox)

        # Zone de texte
        self.MoviesSearchedTextEdit = QPlainTextEdit(self.MoviesSearchedBox)
        #self.MoviesSearchedTextEdit.setAcceptDrops(True)
        MoviesSearchedVLayout.addWidget(self.MoviesSearchedTextEdit)

        MoviesSearchedHLayout = QHBoxLayout(None)
        MoviesSearchedVLayout.addLayout(MoviesSearchedHLayout)

        # Icône d'aide
        Icon = QIcon.fromTheme("documentinfo", QIcon("Ressources:documentinfo.svg")).pixmap(24, 24)
        self.MoviesSearchedLabel = QLabel()
        self.MoviesSearchedLabel.setPixmap(Icon)
        MoviesSearchedHLayout.addWidget(self.MoviesSearchedLabel)

        MoviesSearchedSpacer2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        MoviesSearchedHLayout.addItem(MoviesSearchedSpacer2)

        # Bouton de recherche
        self.MoviesSearchedButton = QPushButton(QIcon.fromTheme("edit-find", QIcon("Ressources:edit-find.svg")), "")
        MoviesSearchedHLayout.addWidget(self.MoviesSearchedButton)
        self.MoviesSearchedButton.clicked.connect(self.LaunchMovieSearch)


        ### Gestion de la box des retours et de la progression
        # Box et son Layout Vertical
        self.ProgressBox = QGroupBox(self.TopSplitter)
        BigProgressVLayout = QVBoxLayout(self.ProgressBox)

        # Création d'un sous widget et de son layout pour QScrollArea
        # QGroupBox (self.ProgressBox)
        #     QVBoxLayout (BigProgressVLayout)
        #         QScrollArea (ProgressScroll)
        #             QWidget (SubProgressScroll)
        #                 QVBoxLayout (self.ProgressVLayout)
        SubProgressScroll = QWidget()
        self.ProgressVLayout = QVBoxLayout(SubProgressScroll)

        # Création du QScrollArea qui contiendra le sous widget et les progress bar
        self.ProgressScroll = QScrollArea(self.ProgressBox)
        self.ProgressScroll.setWidgetResizable(True)
        self.ProgressScroll.setWidget(SubProgressScroll)
        self.ProgressScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        BigProgressVLayout.addWidget(self.ProgressScroll)

        # Zone de texte
        ProgressHLayout = QHBoxLayout(None)

        # Bouton d'info dans la ScrollBar
        self.ProgressInfoButton = QPushButton(QIcon.fromTheme("documentinfo", QIcon("Ressources:documentinfo.svg")), "", self.ProgressBox)
        self.ProgressInfoButton.clicked.connect(lambda: self.InformationsDialog.show())
        self.ProgressScroll.setCornerWidget(self.ProgressInfoButton)

        # Barre de progression
        BigProgressVLayout.addLayout(ProgressHLayout)
        self.ProgressBarMain = QProgressBar(self.ProgressBox)
        ProgressHLayout.addWidget(self.ProgressBarMain)

        # Bouton d'annulation
        self.ProgressButton = QPushButton(QIcon.fromTheme("dialog-cancel", QIcon("Ressources:dialog-cancel.svg")), "", self.ProgressBox)
        self.ProgressButton.clicked.connect(self.StopWorkinProgress)
        self.ProgressButton.setEnabled(False)
        ProgressHLayout.addWidget(self.ProgressButton)

        # Table d'affichage des retours
        self.InformationsTable = QTableWidget(0, 5)
        self.InformationsTable.setColumnHidden(0, True)
        self.InformationsTable.setColumnHidden(2, True)
        self.InformationsTable.setColumnWidth(3, 120)
        self.InformationsTable.horizontalHeader().setStretchLastSection(True)
        self.InformationsTable.horizontalHeader().setSortIndicatorShown(True)
        self.InformationsTable.horizontalHeader().sectionClicked.connect(self.SortInformations)
        self.InformationsTable.verticalHeader().setVisible(False)

        if QtVersion == 6:
            self.InformationsTable.horizontalHeader().setSortIndicatorClearable(True)

        # Fenêtre de la table des retours, ne pas utiliser setAttribute(Qt.WA_DeleteOnClose)
        self.InformationsDialog = QDialog(self)
        self.InformationsDialog.setMinimumHeight(400)
        self.InformationsDialog.setMinimumWidth(500)
        self.InformationsDialog.resize(900, 500)

        # Bouton de nettoyage
        self.InformationsClear = QPushButton(QIcon.fromTheme("edit-clear-history", QIcon("Ressources:edit-clear-history.svg")), "", self.InformationsDialog)
        self.InformationsClear.clicked.connect(self.ClearInformations)

        # Bouton de copie de la sélection
        self.InformationsCopy = QPushButton(QIcon.fromTheme("edit-copy", QIcon("Ressources:edit-copy.svg")), "", self.InformationsDialog)
        self.InformationsCopy.clicked.connect(self.CopyInformations)

        # Bouton de sortie
        self.InformationsClose = QPushButton(QIcon.fromTheme("dialog-close", QIcon("Ressources:dialog-close.svg")), "", self.InformationsDialog)
        self.InformationsClose.clicked.connect(self.InformationsDialog.hide)

        # Présentation de la fenêtre
        Layout1 = QHBoxLayout()
        Layout1.addWidget(self.InformationsClear)
        Layout1.addStretch()
        Layout1.addWidget(self.InformationsCopy)
        Layout1.addStretch()
        Layout1.addWidget(self.InformationsClose)
        Layout2 = QVBoxLayout()
        Layout2.addWidget(self.InformationsTable)
        Layout2.addLayout(Layout1)
        self.InformationsDialog.setLayout(Layout2)


        ### Gestion de la box des configs, utilisation de labels pour permettre leur traduction
        self.ConfigsBox = QGroupBox(self.TopSplitter)
        self.ConfigsBox.setMinimumWidth(410)
        ConfigLayout1 = QVBoxLayout(self.ConfigsBox)

        ConfigWidget = QWidget(None)

        ConfigScroll = QScrollArea(self.ConfigsBox)
        ConfigScroll.setWidgetResizable(True)
        ConfigScroll.setWidget(ConfigWidget)
        ConfigLayout1.addWidget(ConfigScroll)

        ProgressFLayout = QFormLayout(ConfigWidget)

        # Widget du Token
        self.TokenWidget = QLineEdit(Global['Token'], self.ConfigsBox)
        self.TokenWidget.setClearButtonEnabled(True)
        self.TokenWidget.textChanged.connect(functools.partial(self.UpdateBlockingOptions, 'Token'))
        self.TokenLabel = QLabel()
        ProgressFLayout.addRow(self.TokenLabel, self.TokenWidget)

        # Widget du nombre d'essai de connexion lors de la recherche de film
        self.TryMaxWidget = QSpinBox(self.ConfigsBox)
        self.TryMaxWidget.setMinimum(1)
        self.TryMaxWidget.setMaximum(20)
        self.TryMaxWidget.setValue(Global['TryMax'])
        self.TryMaxWidget.valueChanged.connect(functools.partial(self.UpdateOptions, 'TryMax'))
        self.TryMaxWidget.setMinimumWidth(150)
        self.TryMaxLabel = QLabel()
        ProgressFLayout.addRow(self.TryMaxLabel, self.TryMaxWidget)

        # Séparateur visuel
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        ProgressFLayout.addRow(separator)

        # Widget du dossier de téléchargement
        self.DownloadFolderWidget = QLineEdit(DownloadFolder.absolutePath(), self.ConfigsBox)
        self.DownloadFolderAction = QAction(QIcon.fromTheme("folder", QIcon("Ressources:folder.svg")), "", self.DownloadFolderWidget)
        self.DownloadFolderAction.triggered.connect(self.SelectOutputFolder)
        self.DownloadFolderWidget.addAction(self.DownloadFolderAction, QLineEdit.LeadingPosition)
        self.DownloadFolderWidget.setClearButtonEnabled(True)
        self.DownloadFolderWidget.setText(Global['DownloadFolder'].absolutePath())
        self.DownloadFolderWidget.textEdited.connect(functools.partial(self.UpdateBlockingOptions, 'DownloadFolder'))
        self.DownloadFolderWidget.setMinimumWidth(150)
        self.DownloadFolderLabel = QLabel()
        ProgressFLayout.addRow(self.DownloadFolderLabel, self.DownloadFolderWidget)

        # Widget des langues à traiter
        self.ReloadLanguagesButton = QPushButton(QIcon.fromTheme("view-refresh", QIcon("Ressources:view-refresh.svg")), "", self.ConfigsBox)
        self.ReloadLanguagesButton.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed))
        self.ReloadLanguagesButton.clicked.connect(functools.partial(self.LoadImagesLanguages, True))

        self.ImagesLanguagesWidget = QCheckComboBox(self.ConfigsBox)
        self.ImagesLanguagesWidget.setMinimumWidth(150)
        self.LoadImagesLanguages()
        self.ImagesLanguagesWidget.setStateItems(Qt.Checked, Global['ImagesLanguages'], False, False)
        self.ImagesLanguagesWidget.setIcons(QCheckComboBoxIcons)
        self.ImagesLanguagesWidget.setDefaultValues([
            {"value": "fr", "state":Qt.Checked},
            {"value": "en", "state":Qt.Checked},
            {"value": "null", "state":Qt.Checked}
            ])

        self.ImagesLanguagesWidget.currentDataChanged.connect(functools.partial(self.UpdateBlockingOptions, 'ImagesLanguages'))

        ImagesLanguagesLayout = QHBoxLayout()
        ImagesLanguagesLayout.addWidget(self.ImagesLanguagesWidget)
        ImagesLanguagesLayout.addWidget(self.ReloadLanguagesButton)

        self.ImagesLanguagesLabel = QLabel()
        ProgressFLayout.addRow(self.ImagesLanguagesLabel, ImagesLanguagesLayout)

        # Widget des types d'images à télécharger
        Liste = [{"data": "posters"}, {"data": "logos"}, {"data": "backdrops"}]

        self.ImagesTypesWidget = QCheckComboBox(self.ConfigsBox)
        self.ImagesTypesWidget.setMinimumWidth(150)
        self.ImagesTypesWidget.addItems(Liste)
        self.ImagesTypesWidget.setStateItems(Qt.Checked, Global['ImagesTypes'], False, False)
        self.ImagesTypesWidget.setDefaultValues([{"value": "Posters", "state":Qt.Checked}])
        self.ImagesTypesWidget.setIcons(QCheckComboBoxIcons)
        self.ImagesTypesWidget.currentDataChanged.connect(functools.partial(self.UpdateBlockingOptions, 'ImagesTypes'))
        self.ImagesTypesWidget.statusTipHighlighted.connect(self.ForceSetStatusTip)

        self.ImagesTypesLabel = QLabel()
        ProgressFLayout.addRow(self.ImagesTypesLabel, self.ImagesTypesWidget)

        # Widget des types d'images à télécharger
        Liste = [{"data": "movie", "text":"films"}, {"data": "tv", "text":"télé"}]

        self.SourcesSearchWidget = QCheckComboBox(self.ConfigsBox)
        self.SourcesSearchWidget.setMinimumWidth(150)
        self.SourcesSearchWidget.addItems(Liste)
        self.SourcesSearchWidget.setStateItems(Qt.Checked, Global['SourcesSearch'], False, False)
        self.SourcesSearchWidget.setDefaultValues([{"value": "movie", "state":Qt.Checked}])
        self.SourcesSearchWidget.setIcons(QCheckComboBoxIcons)
        self.SourcesSearchWidget.currentDataChanged.connect(functools.partial(self.UpdateBlockingOptions, 'SourcesSearch'))
        self.SourcesSearchWidget.setItemData(0, QColor(Qt.darkBlue), role=Qt.ForegroundRole)
        self.SourcesSearchWidget.setItemData(1, QColor(Qt.darkGreen), role=Qt.ForegroundRole)

        self.SourcesSearchLabel = QLabel()
        ProgressFLayout.addRow(self.SourcesSearchLabel, self.SourcesSearchWidget)

        # Séparateur visuel
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        ProgressFLayout.addRow(separator)

        # Widget du nombre de page à traiter lors de la recherche de film
        self.NbPageWidget = QSpinBox(self.ConfigsBox)
        self.NbPageWidget.setMinimum(1)
        self.NbPageWidget.setMaximum(20)
        self.NbPageWidget.setValue(Global['NbPage'])
        self.NbPageWidget.valueChanged.connect(functools.partial(self.UpdateOptions, 'NbPage'))
        self.NbPageWidget.setMinimumWidth(150)
        self.NbPageLabel = QLabel()
        ProgressFLayout.addRow(self.NbPageLabel, self.NbPageWidget)

        # Widget de la gestion des contenus adulte de la recherche de film
        self.IncludeAdultSearchWidget = QComboBox(self.ConfigsBox)
        self.IncludeAdultSearchWidget.addItems(["", "", ""])
        self.IncludeAdultSearchWidget.setCurrentIndex(Global['IncludeAdultSearch'])
        self.IncludeAdultSearchWidget.currentIndexChanged.connect(functools.partial(self.UpdateOptions, "IncludeAdultSearch"))

        self.IncludeAdultSearchLabel = QLabel()
        ProgressFLayout.addRow(self.IncludeAdultSearchLabel, self.IncludeAdultSearchWidget)

        # Séparateur visuel
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        ProgressFLayout.addRow(separator)

        # Widget du choix de rangement des films
        SortSearchLayout = QHBoxLayout()

        self.SortSearchWidget = QComboBox(self.ConfigsBox)
        self.SortSearchWidget.addItems(["", "", ""])
        self.SortSearchWidget.setCurrentIndex(Global['SortSearch'])
        self.SortSearchWidget.currentIndexChanged.connect(functools.partial(self.UpdateOptions, "SortSearch"))

        self.SortReverseWidget = QPushButton(self.ConfigsBox)
        self.SortReverseWidget.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed))
        self.SortReverseWidget.setIcon(QIcon.fromTheme("view-sort-ascending", QIcon("Ressources:view-sort-ascending.svg")))
        self.SortReverseWidget.setCheckable(True)
        self.SortReverseWidget.setChecked(Global['SortReverse'])
        self.SortReverseWidget.toggled.connect(functools.partial(self.UpdateOptions, "SortReverse"))

        SortSearchLayout.addWidget(self.SortSearchWidget)
        SortSearchLayout.addWidget(self.SortReverseWidget)

        self.SortSearchLabel = QLabel()
        ProgressFLayout.addRow(self.SortSearchLabel, SortSearchLayout)

        # Widget de la taille des images
        self.ImageSizeWidget = QSliderCustom(self.ConfigsBox)
        self.ImageSizeWidget.setFixedHeight(15)
        self.ImageSizeWidget.setMinimum(50)
        self.ImageSizeWidget.setMaximum(500)
        self.ImageSizeWidget.setOrientation(Qt.Horizontal)
        self.ImageSizeWidget.setValue(Global['ImageSize'])
        self.ImageSizeWidget.setMinimumWidth(150)
        self.ImageSizeWidget.continueValueChanged.connect(functools.partial(self.UpdateOptions, 'ImageSize'))
        # self.ImageSizeWidget.sliderLeaved.connect(self.ImageSizeLeave)
        # self.ImageSizeWidget.sliderEntered.connect(self.ImageSizeEnter)

        self.ImageSizeLabel = QLabel()
        # ProgressFLayout.addRow(self.ImageSizeLabel, self.ImageSizeWidget)


        # Widget des automatisations
        Liste = [{"data": "AutoOpen"}, {"data": "AutoDl"}, {"data": "AutoSearch"}]

        self.AutoOptionsWidget = QCheckComboBox(self.ConfigsBox)
        self.AutoOptionsWidget.setMinimumWidth(150)
        self.AutoOptionsWidget.addItems(Liste)
        self.AutoOptionsWidget.setStateItems(Qt.Checked, Global['AutoOptions'], False, False)
        self.AutoOptionsWidget.setIcons(QCheckComboBoxIcons)
        self.AutoOptionsWidget.currentDataChanged.connect(self.UpadeAutoOptions)
        self.AutoOptionsWidget.statusTipHighlighted.connect(self.ForceSetStatusTip)

        self.AutoOptionsLabel = QLabel()
        ProgressFLayout.addRow(self.AutoOptionsLabel, self.AutoOptionsWidget)

        # Séparateur visuel
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        ProgressFLayout.addRow(separator)

        # Widget de la langue du logiciel
        self.LanguageWidget = QComboBox(self.ConfigsBox)
        self.LanguageWidget.addItem(QIcon("Flags:en.svg"), "English")
        self.LanguageWidget.addItem(QIcon("Flags:fr.svg"), "Français")
        self.LanguageWidget.currentTextChanged.connect(self.UpdateLanguage)
        self.LanguageWidget.setMinimumWidth(150)
        self.LanguageLabel = QLabel()
        ProgressFLayout.addRow(self.LanguageLabel, self.LanguageWidget)


        ### Gestion de la box de la liste des films
        self.MoviesFindedBox = QGroupBox(self.WinSplitter)
        self.MoviesFindedBox.setMinimumHeight(200)
        MoviesFindedHLayout = QVBoxLayout(self.MoviesFindedBox)

        # Ajout du spliter dans un Widget pour qu'il ne soit pas coupé
        layout = QHBoxLayout()
        layout.addWidget(self.ImageSizeWidget)
        corner_widget = QWidget(self)
        corner_widget.setLayout(layout)
        corner_widget.setFixedHeight(30)

        # Onglets des films
        self.MoviesFindedTab = QTabWidgetCustom(self.MoviesFindedBox)
        self.MoviesFindedTab.setCornerWidget(corner_widget)
        self.MoviesFindedTab.setTabsClosable(True)
        self.MoviesFindedTab.tabCloseRequested.connect(self.RemoveMovieTab)
        MoviesFindedHLayout.addWidget(self.MoviesFindedTab)

        # Répartition du WinSplitter
        if Global['WinSplitter'] == [0, 0]:
            # 25% pour le TopSplitter dans la limite de 300px
            SubWinSplitter1 = int((self.width() * 25) / 100)

            if SubWinSplitter1 > 300:
                SubWinSplitter1 = 300

            SubWinSplitter2 = int(self.width() - SubWinSplitter1)

            self.WinSplitter.setSizes([SubWinSplitter1, SubWinSplitter2])

        else:
            self.WinSplitter.setSizes(Global['WinSplitter'])

        # Répartition du TopSplitter
        if Global['TopSplitter'] == [0, 0]:
            #45% pour le MoviesSearchedBox dans la limite de 400px
            SubTopSplitter1 = int((self.width() * 45) / 100)

            if SubTopSplitter1 > 400:
                SubTopSplitter1 = 400

            SubTopSplitter2 = int(self.width() - SubTopSplitter1)
            self.TopSplitter.setSizes([SubTopSplitter1, SubTopSplitter2])

        else:
            self.TopSplitter.setSizes(Global['TopSplitter'])


        # Installation des filtres des événements
        self.MoviesFindedTab.installEventFilter(self)
        self.MoviesSearchedTextEdit.installEventFilter(self)

        # Chargement de la langues, force l'anglais
        if Global["Language"] == "Français":
            self.LanguageWidget.setCurrentText("Français")

        else:
            self.UpdateLanguage("English")

        # Si des arguments ont été reçus
        if len(sys.argv) > 1:
            self.MovieNamesCleaner(sys.argv[1:])

        # Affichage de la fenêtre
        self.show()

        # Débloque ou non les actions si les variables sont OK
        self.LockOrUnlockActions()

        # Lancement automatique de la recherche des arguments si tout est OK
        if Global['AutoOptions'].get('AutoSearch') and self.MoviesSearchedButton.isEnabled():
            self.LaunchMovieSearch()


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ForceSetStatusTip(self, Text):
        """Permet d'afficher un texte dans la barre de statut, utilisé par les QCheckComboBox."""
        self.statusBar().showMessage(Text)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def eventFilter(self, Object, Event):
        """Filtre sur les événements."""
        # Fermeture des onglets eu clic molette
        if Object == self.MoviesFindedTab:
            if Event.type() == QEvent.Type.MouseButtonRelease:
                if Event.button() == Qt.MouseButton.MiddleButton:
                    TabIndex = self.MoviesFindedTab.tabBar().tabAt(Event.position().toPoint())
                    self.RemoveMovieTab(TabIndex)

        # Lors de l'utilisation de ctrl + entrée dans QTextEdit des noms de films
        elif Object == self.MoviesSearchedTextEdit:
            if Event.type() == QEvent.Type.KeyRelease:
                if Event.modifiers() == Qt.ControlModifier:
                    # Il semble que la touche entrée du pavé numérique ne se cumule pas avec ctrl
                    if Event.key() in [Qt.Key_Enter, Qt.Key_Return]:
                        self.MoviesSearchedButton.click()

        return False


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def MovieNamesCleaner(self, Values):
        """Fonction de nettoyage des noms de film."""
        for Value in Values:
            if type(Value) == QUrl:
                Value = Value.toDisplayString()

            # Supprime l'adresse du dossier
            NameWithExt = Value
            if "/" in Value:
                NameWithExt = Value.split("/")[-1]

            # Supprime l'extension
            Name = NameWithExt
            if "." in NameWithExt:
                Name = ''.join(NameWithExt.split(".")[0:-1])

            # Ajout du nom
            self.MoviesSearchedTextEdit.appendPlainText(Name)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def LockOrUnlockActions(self):
        """Fonction (dé)bloquant le bouton de recherche."""
        # Si tout est OK, on active tout
        if Global['Token'] and Global['ImagesLanguages'] and Global['DownloadFolder'] and Global['ImagesTypes'] and Global['SourcesSearch']:
            self.MoviesSearchedButton.setEnabled(True)

            # Déloque les boutons des films
            for MovieName in self.MoviesTab.keys():
                if "QToolButton" in self.MoviesTab[MovieName]:
                    for Button in self.MoviesTab[MovieName]['QToolButton']:
                        Button.setEnabled(True)

        # Sinon on désactive
        else:
            self.MoviesSearchedButton.setEnabled(False)

            # Bloque les boutons des films
            for MovieName in self.MoviesTab.keys():
                if "QToolButton" in self.MoviesTab[MovieName]:
                    for Button in self.MoviesTab[MovieName]['QToolButton']:
                        Button.setEnabled(False)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def RandomColor(self):
        """Fonction générant aléatoirement des couleurs lisibles. Utilisé pour définir une couleur par film."""
        while True:
            # Génération de 3 valeurs rgb
            r, g, b = [random.randint(0, 255) for _ in range(3)]

            # Si la couleur est trop claire, on recommence
            if (r + g + b) / 3 > 127:
                continue

            # Sinon on la renvoie
            else:
                return QColor(r, g, b)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ScrolltoBottom(self):
        """Fonction de descente automatique en bas de la ScrollBar des ProgressBar."""
        # Force la prise en compte des nouvelles ProgressBar
        QCoreApplication.processEvents()

        # Direction le plus en bas
        self.ProgressScroll.verticalScrollBar().setValue(self.ProgressScroll.verticalScrollBar().maximum())


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def LaunchMovieSearch(self):
        """Fonction de lancement de la recherche des films."""
        # Récupération des noms des films séparés par un saut de ligne
        MovieNames = self.MoviesSearchedTextEdit.toPlainText().split('\n')

        # Suppression des lignes vides
        while "" in MovieNames:
            MovieNames.remove('')

        # Vérifie qu'il y a bien au moins une recherche à effectuer
        if not len(MovieNames):
            return

        # Suppression des doublons
        MovieNames = list(set(MovieNames))

        # Indique le nombre de recherche à effectuer à la barre de progression
        self.ProgressBarMain.setMaximum(len(MovieNames))
        self.ProgressBarMain.setFormat(GlobalTr["MoviesProgress"])

        # Grisage des widgets
        self.WorkInProgress('Download')

        # Recrée le dossier si besoin
        if not Global['TempFolder'].exists():
            QDir().mkpath(Global['TempFolder'].absolutePath())

        self.Progress = {}
        self.Progress["Movies"] = len(MovieNames)

        # Suppression des anciennes barres de progression
        for Index in range(self.ProgressVLayout.count()):
            Item = self.ProgressVLayout.itemAt(Index)
            if Item:
                Widget = Item.widget()
                if Widget:
                        Widget.deleteLater()

        # Traitement des films un à un
        for MovieName in MovieNames:
            if not Global["MovieNamesColors"].get(MovieName):
                Global["MovieNamesColors"][MovieName] = QBrush(self.RandomColor())

            self.AddMovieTab(MovieName)
            self.Progress[MovieName] = {}
            self.Progress[MovieName]["Pages"] = 0
            self.Progress[MovieName]["PostersPage"] = {}

            ProgressBar = QProgressBar()
            ProgressBar.setValue(0)
            ProgressBar.setMaximum(Global["NbPage"])
            ProgressBar.setFormat(f"{MovieName} page : %v / %m")
            self.Progress[MovieName]["ProgressBar"] = ProgressBar
            self.ProgressVLayout.addWidget(self.Progress[MovieName]["ProgressBar"])
            self.goScrolltoBottom.emit()

            for MoviePage in range(1, Global["NbPage"] + 1):
                self.Progress[MovieName]["PostersPage"][MoviePage] = 0
                self.Progress[MovieName]["Pages"] += 1

                # Création de l'action de recherche
                SearchMovie = ThreadActions(Action = "Movie",
                                            MovieName = MovieName,
                                            MoviePage = MoviePage,
                                            IncludeAdultSearch = Global['IncludeAdultSearch'],
                                            Language = Global["Language"],
                                            SourcesSearch = Global['SourcesSearch'],
                                            DlFolder = Global['TempFolder'],
                                            TryMax = Global['TryMax'],
                                            Headers = Global['Headers'],
                                            TimeOut = Global['TimeOut'])

                # Connexion des threads => Soft
                SearchMovie.Signals.MovieFinished.connect(self.MovieFinished)
                SearchMovie.Signals.Info.connect(self.AppendInformation)

                # Signal d'arrêt du travail, Soft => thread
                self.stopWork.connect(SearchMovie.stopAllNow)

                # Ajout de la recherche de page à la liste des actions
                self.GestionnaireActions.start(SearchMovie)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def MovieFinished(self, ReturnList):
        """Fonction appelée post recherche de film."""
        # Ce n'est pas sensé arriver
        if not ReturnList:
            return

        # Récupération des infos
        MovieName = ReturnList[0]["MovieName"]
        MoviePage = ReturnList[0]["MoviePage"]

        # Si la page n'a renvoyé aucun film
        if ReturnList[0].get("NbMovie") == 0:
            # On décrémente le nombre de page à traiter
            self.Progress[MovieName]["Pages"] -= 1
            self.ProgressBarValue(self.Progress[MovieName]["ProgressBar"])

            # Si toutes les pages du film ont été traitées
            if not self.Progress[MovieName]["Pages"]:
                # On décrémente le nombre de film à traiter
                self.Progress["Movies"] -= 1

                # On fait progresser la barre de dl
                self.ProgressBarValue(self.ProgressBarMain)

                # Message d'information
                self.AppendInformation([timeNow(), 'INFO', MovieName, GlobalTr["SearchFinish"].format(MoviePage)])

                # Mode auto dl si un seul résultat
                if len(self.MoviesTab[MovieName]['QToolButton']) == 1 and Global['AutoOptions'].get('AutoDl'):
                    self.AutoDlToolButton = self.MoviesTab[MovieName]['QToolButton'][0]

                # Si tous les films ont été traités
                if not self.Progress["Movies"]:
                    # Déblocage de l'interface
                    self.StopWorkinProgress()

            # Ne crée pas de liste de téléchargement d'image
            return


        # Création d'une liste de poster à télécharger pour chaque film
        for x in ReturnList:
            # Incrémentation du nombre d'image de film pour cette page
            self.Progress[MovieName]["PostersPage"][MoviePage] += 1

            # Création des actions Téléchargement d'image
            DownloadPoster = ThreadActions(Action = "DownloadPicture", **x)

            # Connexion des threads => Soft
            DownloadPoster.Signals.AddMovieButton.connect(self.AddMovieButton)
            DownloadPoster.Signals.DownloadPictureFinished.connect(self.DownloadPictureFinished)
            DownloadPoster.Signals.Info.connect(self.AppendInformation)

            # Signal d'arrêt du travail, Soft => thread
            self.stopWork.connect(DownloadPoster.stopAllNow)

            # Ajout de la recherche de page à la liste des actions
            self.GestionnaireActions.start(DownloadPoster)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def DownloadPictureFinished(self, ReturnObject):
        """Fonction appelée post téléchargement de poster."""
        if not ReturnObject:
            return

        # Récupération des infos
        MovieName = ReturnObject["MovieName"]
        MoviePage = ReturnObject["MoviePage"]

        # Image téléchargée ou annulée, on décrémente
        self.Progress[MovieName]["PostersPage"][MoviePage] -= 1

        # Si toutes les images de la page du film ont été traitées
        if not self.Progress[MovieName]["PostersPage"][MoviePage]:
            # On décrémente le nombre de page à traiter
            self.Progress[MovieName]["Pages"] -= 1
            self.ProgressBarValue(self.Progress[MovieName]["ProgressBar"])

            # Si toutes les pages du film ont été traitées
            if not self.Progress[MovieName]["Pages"]:
                # On décrémente le nombre de film à traiter
                self.Progress["Movies"] -= 1

                # On fait progresser la barre de dl
                self.ProgressBarValue(self.ProgressBarMain)

                # Message d'information sur la fin de recherche du film
                self.AppendInformation([timeNow(), 'INFO', MovieName, GlobalTr["SearchFinish"].format(MoviePage)])

                # Mode auto dl si un seul résultat
                if len(self.MoviesTab[MovieName]['QToolButton']) == 1 and Global['AutoOptions'].get('AutoDl'):
                    self.AutoDlToolButton = self.MoviesTab[MovieName]['QToolButton'][0]

                # Si tous les films ont été traités
                if not self.Progress["Movies"]:
                    # Déblocage de l'interface
                    self.StopWorkinProgress()


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddMovieTab(self, MovieName):
        """Fonction ajoutant les retours des recherches."""
        # Suppression des anciens onglets
        if MovieName in self.MoviesTab.keys():
            self.RemoveMovieTab(self.MoviesFindedTab.indexOf(self.MoviesTab[MovieName]['QWidget1']))

        # Création de l'onglet
        self.MoviesTab[MovieName] = {}
        self.MoviesTab[MovieName]["NbMovie"] = 0
        self.MoviesTab[MovieName]['QWidget1'] = QWidget(None)
        self.MoviesTab[MovieName]['QHBoxLayout1'] = QHBoxLayout(self.MoviesTab[MovieName]['QWidget1'])

        self.MoviesTab[MovieName]['QScrollArea'] = QScrollAreaCustom(self.MoviesTab[MovieName]['QWidget1'])
        self.MoviesTab[MovieName]['QScrollArea'].setWidgetResizable(True)
        self.MoviesTab[MovieName]['QScrollArea'].signalButtonsResize.connect(self.UpadeImageSizeWheel)

        self.MoviesTab[MovieName]['QHBoxLayout1'].addWidget(self.MoviesTab[MovieName]['QScrollArea'])

        self.MoviesTab[MovieName]['QWidget2'] = QWidget(self.MoviesTab[MovieName]['QScrollArea'])
        self.MoviesTab[MovieName]['QFlowLayout'] = QFlowLayout(self.MoviesTab[MovieName]['QWidget2'], 5, 5, True, orderReverse=Global['SortReverse'])

        self.MoviesTab[MovieName]['QScrollArea'].setWidget(self.MoviesTab[MovieName]['QWidget2'])

        self.MoviesTab[MovieName]['QToolButton'] = []

        # Ajout de l'onglet de la recherche
        Index = self.MoviesFindedTab.addTab(self.MoviesTab[MovieName]['QWidget1'], GlobalTr["TabName"].format(MovieName, 0))
        self.MoviesFindedTab.setTabWhatsThis(Index, MovieName)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AddMovieButton(self, MovieName, MovieInfos):
        """Fonction ajoutant les retours des recherches."""
        # En cas de date inconnue
        if MovieInfos['release_date'] == "9999-99-99":
            MovieInfos['release_date'] = GlobalTr["DateUnknow"]

        # Création du bouton
        QToolButton = QToolButtonCustom(self.MoviesTab[MovieName]['QWidget2'],
                                        ImageSize = Global['ImageSize'],
                                        icon = Global['TempFolder'].absolutePath() + MovieInfos['poster_path'],
                                        data = MovieInfos,
                                        downloadFolder = Global['DownloadFolder'].absolutePath())

        # Création d'un nom d'objet permettant leur rangement dans le QFlowLayout
        if Global['SortSearch'] == 0:
            ObjectName = MovieInfos['title'].lower()
            for Replace in ["-", ",", ":", ";", "_", "'", '"', "/", " ", " "]:
                ObjectName = ObjectName.replace(Replace, "")

        elif Global['SortSearch'] == 1:
            ObjectName = MovieInfos['release_date']

        elif Global['SortSearch'] == 2:
            ObjectName = f"{MovieInfos['media_type']}{MovieInfos['id']:06d}"

        QToolButton.setObjectName(ObjectName)
        QToolButton.clicked.connect(lambda: self.LaunchImagesDownload(QToolButton))

        # Ajout du bouton dans le Layout et dans la liste des boutons
        self.MoviesTab[MovieName]['QFlowLayout'].addWidget(QToolButton)
        self.MoviesTab[MovieName]['QToolButton'] += [QToolButton]

        # Mise à jour de la variable du nombre de film dans l'onglet
        NbMovie = len(self.MoviesTab[MovieName]['QToolButton'])

        # Mise à jour du texte de l'onglet
        Index = self.MoviesFindedTab.indexOf(self.MoviesTab[MovieName]['QWidget1'])
        self.MoviesFindedTab.setTabText(Index, GlobalTr["TabName"].format(MovieName, NbMovie))


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def RemoveMovieTab(self, Index):
        """Fonction supprimant les onglets des films au clic sur l'icône."""
        MovieName = self.MoviesFindedTab.tabWhatsThis(Index)

        # Supprime les widgets pour ne pas les recharger si on relance la même recherche
        if MovieName in self.MoviesTab.keys():
            self.MoviesTab[MovieName]['QWidget1'].deleteLater()
            del self.MoviesTab[MovieName]

        # Supprime l'onglet
        self.MoviesFindedTab.removeTab(Index)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def LaunchImagesDownload(self, Widget):
        """Fonction de téléchargement des images de la vidéo, appelée lors d'un clic sur un QToolButtonCustom."""
        # Récupération de la palette du bouton
        Palette = Widget.palette()

        # Si le bouton est bleu, on bloque la nouvelle demande de téléchargement téléchargement
        if Palette.color(QPalette.Button) == PalettesWigets["BlueColor"]:
            return

        # Mise en bleu du bouton, reprise de la palette actuelle (pour la couleur du texte) puis ajout de la couleur du bouton
        Palette.setColor(QPalette.Button, PalettesWigets["BlueColor"])
        Widget.setPalette(Palette)

        # Génération d'un nouveau dossier dans la config du bouton
        Widget.generateDownloadFolder(Global["DownloadFolder"].absolutePath())

        # Grisage des widgets
        self.WorkInProgress('Search')

        # Recrée le dossier si besoin
        if not Global['TempFolder'].exists():
            QDir().mkpath(Global['TempFolder'].absolutePath())

        MovieName = Widget.data['title']
        MovieId = Widget.data['id']
        MovieInfo = f"{MovieName}-{MovieId}"

        if self.Progress.get("Download"):
            self.ProgressBarMain.setMaximum(self.ProgressBarMain.maximum() + 1)
            self.Progress["Download"] += 1

        else:
            self.Progress["Download"] = 1
            self.ProgressBarMain.setValue(0)
            self.ProgressBarMain.setMaximum(1)

        if not Global["MovieNamesColors"].get(MovieInfo):
            Global["MovieNamesColors"][MovieInfo] = QBrush(self.RandomColor())

        self.Progress[MovieId] = {}
        self.Progress[MovieId]["ImagesToDl"] = 0

        ProgressBar = QProgressBar()
        ProgressBar.setValue(0)
        ProgressBar.setFormat(GlobalTr["ImagesWait"].format(MovieId))
        self.Progress[MovieId]["ProgressBar"] = ProgressBar
        self.goScrolltoBottom.emit()

        self.ProgressVLayout.addWidget(self.Progress[MovieId]["ProgressBar"])

        # Création du dossier
        DlFolder = QDir(Widget.downloadFolder)
        if not DlFolder.exists():
            QDir().mkpath(DlFolder.absolutePath())

        # Création et exécution du thread
        # Donne tout de suite les variables globales afin de ne pas avoir de souci si les options sont modifiées pendant le dl
        SearchPictures = ThreadActions(Action="MoviePictures",
                                       MovieId=Widget.id,
                                       MovieName=MovieName,
                                       MoviePage=1,
                                       DlFolder=DlFolder,
                                       Widget=Widget,
                                       Source=Widget.data["media_type"],
                                       ImagesLanguages=','.join(Global['ImagesLanguages']),
                                       ImagesTypes=Global['ImagesTypes'],
                                       TryMax=Global['TryMax'],
                                       Headers=Global['Headers'],
                                       TimeOut=Global['TimeOut'])

        # Connexion des threads => Soft
        SearchPictures.Signals.MoviePicturesFinished.connect(self.MoviePicturesFinished)
        SearchPictures.Signals.Info.connect(self.AppendInformation)
        SearchPictures.Signals.DownloadFolder.connect(self.DownloadFolders)

        # Signal d'arrêt du travail, Soft => thread
        self.stopWork.connect(SearchPictures.stopAllNow)

        # Ajout de la recherche de page à la liste des actions
        self.GestionnaireActions.start(SearchPictures)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def DownloadFolders(self, DlFolder):
        """Fonction liée aux threads qui ajoute les dossiers actuellement utilisé."""
        if DlFolder not in Global["MovieFoldersDl"]:
            Global["MovieFoldersDl"].append(DlFolder)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def MoviePicturesFinished(self, ReturnList):
        """Fonction appelée post recherche de posters."""
        if not ReturnList:
            return

        # Récupération des infos
        MovieName = ReturnList[0]["MovieName"]
        MoviePage = ReturnList[0]["MoviePage"]
        MovieDlFolder = ReturnList[0]["MovieDlFolder"]
        Widget = ReturnList[0]["Widget"]
        MovieId = Widget.data['id']

        # Si la page n'a renvoyé aucun poster
        if not ReturnList[0].get("Picture"):
            self.Progress[MovieId]["ProgressBar"].setFormat(GlobalTr["NoImagesProgress"].format(MovieId))
            self.Progress[MovieId]["ProgressBar"].setMaximum(1)
            self.Progress[MovieId]["ProgressBar"].setValue(1)
            self.AppendInformation([timeNow(), 'ERROR', f"{MovieName}-{MovieId}", GlobalTr["SearchFinishNoImage"]])
            self.ProgressBarValue(self.ProgressBarMain)

            # Déblocage de l'interface
            self.StopWorkinProgress()

            # Ne crée pas de liste de téléchargement des posters
            return

        self.Progress[MovieId]["ProgressBar"].setMaximum(len(ReturnList))
        self.Progress[MovieId]["ProgressBar"].setFormat(GlobalTr["ImagesProgress"].format(MovieId))

        # Création d'une liste de poster à télécharger pour chaque film
        for x in ReturnList:
            # Incrémentation du nombre d'image de film pour cette page
            self.Progress[MovieId]["ImagesToDl"] += 1

            # Création des actions Téléchargement d'image
            DownloadPoster = ThreadActions(Action = "DownloadPicture", **x)

            # Connexion des threads => Soft
            DownloadPoster.Signals.DownloadPictureFinished.connect(self.DownloadPosterFinished)
            DownloadPoster.Signals.Info.connect(self.AppendInformation)

            # Signal d'arrêt du travail, Soft => thread
            self.stopWork.connect(DownloadPoster.stopAllNow)

            # Ajout de la recherche de page à la liste des actions
            self.GestionnaireActions.start(DownloadPoster)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def DownloadPosterFinished(self, ReturnObject):
        """Fonction appelée post téléchargement de poster."""
        if not ReturnObject:
            return

        # Récupération des infos
        MovieName = ReturnObject["MovieName"]
        DlFolder = ReturnObject["DlFolder"]
        Widget = ReturnObject["Widget"]
        MovieId = Widget.id

        # Image téléchargée ou annulée, on décrémente
        self.Progress[MovieId]["ImagesToDl"] -= 1

        # On fait progresser la barre de dl
        self.ProgressBarValue(self.Progress[MovieId]["ProgressBar"])

        # Si toutes les posters du film ont été traités
        if not self.Progress[MovieId]["ImagesToDl"]:
            self.ProgressBarValue(self.ProgressBarMain)
            self.Progress["Download"] -= 1

            # Suppression du dossier de dl dans la liste des en cours
            Global["MovieFoldersDl"].remove(DlFolder)

            if Global['AutoOptions'].get("AutoDl"):
                self.AppendInformation([timeNow(), 'INFO', MovieName, GlobalTr["AutoOpenFolder"].format(MovieName)])
                QDesktopServices.openUrl(QUrl.fromLocalFile(DlFolder.absolutePath()))

            # Mise en vert du bouton (QToolButtonCustom), reprise de la palette actuelle (pour la couleur du texte) puis ajout de la couleur du bouton
            Palette = Widget.palette()
            Palette.setColor(QPalette.Button, PalettesWigets["GreenColor"])
            Widget.setPalette(Palette)

            # Déblocage de l'interface
            if not self.Progress["Download"]:
                self.StopWorkinProgress()


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def AppendInformation(self, Information):
        """Fonction concaténant les informations envoyées depuis les threads dans la table d'info."""
        Row = self.InformationsTable.rowCount()

        # Création d'une ligne
        self.InformationsTable.insertRow(Row)

        # Définition de la couleur et mise à jour du type de texte
        if Information[1] == 'ERROR':
            Color = QBrush(QColor(100, 0, 0))

        elif Information[1] == 'INFO':
            Color = QBrush(QColor(0, 0, 100))

        else:
            Color = QBrush(QColor(0, 100, 0))

        # Ajout d'une colonne 0 pour le tri en utilisant MovieName-Date
        Item = QTableWidgetItem(f"{Information[2]}-{Information[0]}")
        self.InformationsTable.setItem(Row, 0, Item)

        for Column, Text in enumerate(Information):
            Column += 1

            # QTableWidgetItem ne prend pas en compte l'html mais est plus adapté que d'utiliser des QLabel
            Item = QTableWidgetItem(str(Text))

            if Column == 3:
                Item.setForeground(Global['MovieNamesColors'][Text])

            else:
                Item.setForeground(Color)

            # Insertion
            self.InformationsTable.setItem(Row, Column, Item)

        # Rangement par nom-date
        self.InformationsTable.sortByColumn(0, Qt.AscendingOrder)
        self.oldSort = 0


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SortInformations(self, Column):
        """Fonction de rangement du QTableWidget."""
        if Column == 3:
            # Rangement par nom-date
            if self.oldSort != Column:
                # Utilisation de la colonne cachée 0 pour le tri
                self.InformationsTable.sortByColumn(0, Qt.AscendingOrder)

                # Affiche le bouton de tri sur la colonne 3, non automatique car utilisation de la 0 ci-dessus
                self.InformationsTable.horizontalHeader().setSortIndicator(3, Qt.AscendingOrder)

                # Maj de la variable sens
                self.oldSort = 3

            else:
                # Utilisation de la colonne cachée 0 pour le tri
                self.InformationsTable.sortByColumn(0, Qt.DescendingOrder)

                # Affiche le bouton de tri sur la colonne 3, non automatique car utilisation de la 0 ci-dessus
                self.InformationsTable.horizontalHeader().setSortIndicator(3, Qt.DescendingOrder)

                # Maj de la variable sens
                self.oldSort = 0

        elif Column == 1:
            # Rangement par date
            if self.oldSort != Column:
                # Utilisation de la colonne cachée 1 pour le tri
                self.InformationsTable.sortByColumn(1, Qt.AscendingOrder)

                # Maj de la variable sens
                self.oldSort = 1

            else:
                # Utilisation de la colonne cachée 1 pour le tri
                self.InformationsTable.sortByColumn(1, Qt.DescendingOrder)

                # Maj de la variable sens
                self.oldSort = 0


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ClearInformations(self):
        """Fonction de nettoyage du QTableWidget."""
        # Global["Informations"] = []

        for x in range(self.InformationsTable.rowCount()):
            self.InformationsTable.removeRow(0)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CopyInformations(self):
        """Fonction récupérant les textes sélectionnés du QTableWidget."""
        # Dictionnaire contenant les textes par ligne et par colonne
        Texts = {}

        # Utilisation d'un QTextDocument qui permettra de virer les balises html
        document = QTextDocument()

        # Boucle sur tous les ranges
        for Range in self.InformationsTable.selectedRanges():
            # Boucle sur les lignes
            for Row in range(Range.topRow(), Range.bottomRow() + 1):
                if Row not in Texts:
                    # Création des lignes dans le dictionnaire
                    Texts[Row] = {}

                for Column in range(Range.leftColumn(), Range.rightColumn() + 1):
                    try:
                        # Récupération du texte du QLabel
                        Label = self.InformationsTable.cellWidget(Row, Column)

                        # Injection du texte au format html dans le QTextDocument
                        document.setHtml(Label.text())

                        # Ajout du texte sans balises dans sa colonne de dictionnaire
                        Texts[Row][Column] = document.toPlainText()

                    except:
                        pass

        # Texte final
        TextFinal = ""

        # Boucle sur les lignes et colonnes
        for Row in sorted(Texts.keys()):
            for Column in sorted(Texts[Row].keys()):
                # Concaténation des textes de même ligne séparés de tabulations
                TextFinal += f"{Texts[Row][Column]}\t"

            # Concaténation des lignes ensembles séparées de saut de ligne
            TextFinal = f"{TextFinal[:-1]}\n"

        # Copie du texte final dans le presse papier sans le dernier saut de ligne
        clipboard = QApplication.clipboard()
        clipboard.setText(TextFinal[:-1])


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def UpdateOptions(self, Option, Value):
        """Fonction générique de mise à jour des options."""
        # Mise à jour de la variable
        Global[Option] = Value

        # Sauvegarde de la valeur dans le fichier de config
        Configs.setValue(Option, Value)

        # Actions dans le cas où l'option modifiée est ImageSize
        if Option == "ImageSize":
            self.ImageSizeLabel.setText(f"{Value} px")

            if not self.ImageSizeWidget.isHover():
                self.ImageSizeLabel.setText(translate("ConfigBox", "Thumb Size:"))

            # Mise à jour de la taille des boutons des films
            for MovieName in self.MoviesTab.keys():
                if "QToolButton" in self.MoviesTab[MovieName]:
                    for Button in self.MoviesTab[MovieName]['QToolButton']:
                        Button.setIconSize(QSize(Value, Value))
                        Button.setMinimumWidth(Value)
                        Button.setMinimumHeight(Value)
                        Button.setMaximumWidth(Value)

        # Création d'une variable globale de connexion lors du changement de token
        elif Option == "Token":
            Global['Headers'] = { 'Authorization': f"Bearer {Global['Token']}", 'Content-Type': "application/json;charset=utf-8" }

        # Mise à jour du sens des tris dans les QFlowLayout
        elif Option == "SortReverse":
            for MovieName in self.MoviesTab.keys():
                if "QFlowLayout" in self.MoviesTab[MovieName]:
                    self.MoviesTab[MovieName]['QFlowLayout'].setOrderReverse(Value)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def UpadeImageSizeWheel(self, Value):
        """Fonction appelée lors des combo ctl + molette sur les QScrollAreaCustom."""
        # Mise à jour de la valeur de la taille des boutons, ce qui va executer UpadeOption
        self.ImageSizeWidget.setValue(self.ImageSizeWidget.value() + Value)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def UpdateBlockingOptions(self, Option, Value):
        """Fonction générique de mise à jour des options bloquantes."""
        # Liste des widgets
        Widgets = {
            'Token': self.TokenWidget,
            'SourcesSearch': self.SourcesSearchWidget,
            'ImagesTypes': self.ImagesTypesWidget,
            'ImagesLanguages': self.ImagesLanguagesWidget,
            'DownloadFolder': self.DownloadFolderWidget
            }

        # Si la valeur n'est pas vide
        if Value:
            # Mise à jour de la variable
            if Option == 'DownloadFolder':
                Global[Option] = QDir(Value)

            else:
                Global[Option] = Value

            # Sauvegarde de la valeur dans le fichier de config
            Configs.setValue(Option, Value)

            # Remise en couleur normale
            Widgets[Option].setPalette(Widgets[Option].style().standardPalette())

        # Si la valeur est vide
        else:
            # Mise à jour de la variable
            Global[Option] = None

            # Colore le widget car la valeur n'est pas bonne
            Widgets[Option].setPalette(PalettesWigets["LineEdit"])


        # Fonction de déblocage du bouton de lancement de la recherche de film
        self.LockOrUnlockActions()


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def UpadeAutoOptions(self, AutoOptionsUpdated):
        """Fonction de mise à jour des options automatiques."""
        # Dictionnaire par défaut
        Options = {"AutoDl": False, "AutoOpen": False, "AutoSearch": False}

        # mise à jour des valeurs des options
        for Option in AutoOptionsUpdated:
            Options[Option] = True

        # Attribution du nouveau dictionnaire à la variable globale
        Global['AutoOptions'] = Options

        # Sauvegarde de la valeur dans le fichier de config
        Configs.setValue("AutoOptions", AutoOptionsUpdated)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def UpdateLanguage(self, Value):
        """Fonction appelée via la combobox de la langue du soft ou au début du script qui recharge les traductions."""
        # pylupdate5 *.py -ts Languages/hizo-tmdb_fr_FR.ts Languages/hizo-tmdb_en_EN.ts # -noobsolete
        # lrelease Languages/*.ts

        # Suppression de la traduction actuelle
        HizoTMDB.removeTranslator(Global["QTranslator"])

        # Langue à utiliser
        File = "hizo-tmdb_en_EN"
        if Value in (1, "Français"):
            File = "hizo-tmdb_fr_FR"

        # Mise à jour du fichier langage de Qt, ne semble pas fonctionner... du coup traduction des quelques mots manuellement

        # Mise à jour de la langue du logiciel
        if Global["QTranslator"].load(File, f"{AbsoluteFolder}/Languages"):
            HizoTMDB.installTranslator(Global["QTranslator"])

        # En cas d'erreur de chargement de la traduction
        else:
            QMessageBox(QMessageBox.Critical, translate("UpdateLanguage", "Translation error"), translate("UpdateLanguage", "No <b>French</b> translation files found.<br/>Use of <b>English language</b>."), QMessageBox.Close, None, Qt.WindowSystemMenuHint).exec()


        # Mise à jour de la variable
        Global["Language"] = "English"
        if Value in (1, "Français"):
            Global["Language"] = "Français"

        # Sauvegarde de la valeur dans le fichier de config
        Configs.setValue("Language", Value)


        # Le changement de langue exécute l'événement changeEvent
        # Cela crée un décalage, l'event est traité plus tard
        # il vaut mieux le faire ici
        # Widgets de la fenêtre principale
        self.ButtonQuit.setText(translate("MainWindow", "Exit"))
        self.AboutButton.setText(translate("MainWindow", "About"))

        # Widgets de la SearchBox
        self.MoviesSearchedButton.setText(translate("SearchBox", "Start search"))
        self.MoviesSearchedBox.setTitle(translate("SearchBox", "Movie names searched:"))
        self.MoviesSearchedButton.setStatusTip(translate("SearchBox", "Start the movies searching."))
        self.MoviesSearchedLabel.setToolTip(translate("SearchBox", "Movie's names to search on <b>The Movie Data Base</b>.<br><br>Rules:<br> - Only one search per line.<br> - Exact names (not case sensitive).<br> - Use *'s for extended search.<br> - Name must be completed enough to be found. <br><br>Examples:<br> - Iron Man: Will return movies with the name iron man.<br> - Iron*: Will return all movies whose name starts with iron.<br> - *Man: Will return all movies whose name ends with man.<br> - *Man*: Will return all movies whose name includes man.<br><br>ctrl + enter launches the search."))

        # Widgets de la ProgressBox
        self.ProgressInfoButton.setStatusTip(translate("ProgressBox", "View all messages informations."))
        self.ProgressButton.setStatusTip(translate("ProgressBox", "Stop the work in progress..."))
        self.ProgressButton.setText(translate("ProgressBox", "Stop work"))
        self.ProgressBox.setTitle(translate("ProgressBox", "Returns and progression:"))
        self.InformationsDialog.setWindowTitle(translate("Debugger", "Debug informations"))
        self.InformationsClear.setText(translate("Debugger", "Clean the table"))
        self.InformationsCopy.setText(translate("Debugger", "Copy the selection"))
        self.InformationsClose.setText(translate("Debugger", "Close"))
        self.InformationsTable.setHorizontalHeaderLabels(["Sort",
                                                          translate("Debugger", "Hours"),
                                                          translate("Debugger", "Type"),
                                                          translate("Debugger", "Information"),
                                                          translate("Debugger", "Message")])



        ### Widgets de la ConfigBox
        self.ConfigsBox.setTitle(translate("ConfigBox", "Configuration:"))

        self.NbPageLabel.setText(translate("ConfigBox", "Nb Page to Download:"))
        self.NbPageWidget.setSuffix(translate("ConfigBox", " page(s)"))
        self.NbPageWidget.setStatusTip(translate("ConfigBox", "Number of page to download during the movies search. Between 1 page and 20 pages."))

        self.TryMaxLabel.setText(translate("ConfigBox", "Max Connection Try:"))
        self.TryMaxWidget.setStatusTip(translate("ConfigBox", "Number of connection attempts to the TMDB's API. Between 1 and 20 try."))

        self.DownloadFolderLabel.setText(translate("ConfigBox", "Download Folder:"))
        self.DownloadFolderAction.setText(translate("ConfigBox", "Folder Selector"))
        self.DownloadFolderWidget.setStatusTip(translate("ConfigBox", "Mandatory: The folder where create the movie folders uses to download posters."))
        self.ReloadLanguagesButton.setStatusTip(translate("ConfigBox", "Recreate the language list file. Need to connect and create a json file."))

        self.TokenLabel.setText(translate("ConfigBox", "Token:"))
        self.TokenWidget.setStatusTip(translate("ConfigBox", "Mandatory: The token to connect at the The Movie Data Base API v4."))

        self.ImageSizeLabel.setText(translate("ConfigBox", "Thumb Size:"))
        self.ImageSizeWidget.setStatusTip(translate("ConfigBox", "The size of the thumbnails' movie. Between 50px and 500px."))

        self.AutoOptionsLabel.setText(translate("ConfigBox", "Automatisation:"))

        self.AutoOptionsWidget.setItemInfoFromData("AutoOpen", {
            "text": translate("ConfigBox", "Open Folder Download", "Automatisation Combobox"),
            "statustip": translate("ConfigBox", "Enable/disable the auto open download folder when posters' download finished.", "Item StatusBar Automatisation Combobox")
            })
        self.AutoOptionsWidget.setItemInfoFromData("AutoDl", {
            "text": translate("ConfigBox", "Download Images Movie", "Automatisation Combobox"),
            "statustip": translate("ConfigBox", "Enable/disable the auto download of the posters when only one movie finded.", "Item StatusBar Automatisation Combobox")
            })
        self.AutoOptionsWidget.setItemInfoFromData("AutoSearch", {
            "text": translate("ConfigBox", "Launch Arguments Search", "Automatisation Combobox"),
            "statustip": translate("ConfigBox", "Enable/disable the auto search at software start if there is search value.", "Item StatusBar Automatisation Combobox")
            })
        self.AutoOptionsWidget.setTitle(translate("ConfigBox", "Actions available:", "Item Title Automatisation Combobox"))
        self.AutoOptionsWidget.setStatusTip(translate("ConfigBox", "List of automatable actions.", "Automatisation Combobox"))

        self.IncludeAdultSearchLabel.setText(translate("ConfigBox", "Adult Contents:", "Include Adulte contents Combobox"))
        self.IncludeAdultSearchWidget.setItemText(0, translate("ConfigBox", "No adulte contents", "Include Adulte contents Combobox"))
        self.IncludeAdultSearchWidget.setItemText(1, translate("ConfigBox", "With adulte contents", "Include Adulte contents Combobox"))
        self.IncludeAdultSearchWidget.setItemText(2, translate("ConfigBox", "Only adulte contents", "Include Adulte contents Combobox"))
        self.IncludeAdultSearchWidget.setStatusTip(translate("ConfigBox", "Enable (unchecked)/disable (half checked)/only (checked) adult content in the movie search."))

        self.SortSearchLabel.setText(translate("ConfigBox", "Video Sorting:", "Video Sorting contents Combobox"))
        self.SortSearchWidget.setItemText(0, translate("ConfigBox", "By Name (without special chars)", "Video Sorting Combobox"))
        self.SortSearchWidget.setItemText(1, translate("ConfigBox", "By Date", "Video SortingCombobox"))
        self.SortSearchWidget.setItemText(2, translate("ConfigBox", "By Type and Id", "Video SortingCombobox"))
        self.SortSearchWidget.setStatusTip(translate("ConfigBox", "Choice of the type of video sorting. Need to relaunch the search."))

        self.SortReverseWidget.setStatusTip(translate("ConfigBox", "Reverse the video sort. Not need to relaunch the search."))

        self.ImagesTypesLabel.setText(translate("ConfigBox", "Images' Types:"))

        self.ImagesTypesWidget.setItemInfoFromData("posters", {
            "text": translate("ConfigBox", "Posters", "Images' Type Combobox"),
            "statustip": translate("ConfigBox", "Enable/disable the posters download when a movie clicked.", "Item StatusBar Images' Type Combobox")
            })
        self.ImagesTypesWidget.setItemInfoFromData("logos", {
            "text": translate("ConfigBox", "Logos", "Images' Type Combobox"),
            "statustip": translate("ConfigBox", "Enable/disable the logos download when a movie clicked.", "Item StatusBar Images' Type Combobox")
            })
        self.ImagesTypesWidget.setItemInfoFromData("backdrops", {
            "text": translate("ConfigBox", "Wallpapers - Backdrops", "Images' Type Combobox"),
            "statustip": translate("ConfigBox", "Enable/disable the wallpapers download when a movie clicked.", "Item StatusBar Images' Type Combobox")
            })
        self.ImagesTypesWidget.setStatusTip(translate("ConfigBox", "Mandatory: The images' types to download."))
        self.ImagesTypesWidget.setTitle(translate("ConfigBox", "Types available:"))
        self.ImagesTypesWidget.contextMenuUpdate()

        self.SourcesSearchLabel.setText(translate("ConfigBox", "Images' sources:"))

        self.SourcesSearchWidget.setItemInfoFromData("movie", {
            "text": translate("ConfigBox", "Movies", "Images' Source Combobox"),
            "statustip": translate("ConfigBox", "Enable/disable the search in movie names.", "Item StatusBar Images' Source Combobox")
            })
        self.SourcesSearchWidget.setItemInfoFromData("tv", {
            "text": translate("ConfigBox", "TV Show", "Images' Source Combobox"),
            "statustip": translate("ConfigBox", "Enable/disable the search in TV show names.", "Item StatusBar Images' Source Combobox")
            })
        self.SourcesSearchWidget.setStatusTip(translate("ConfigBox", "Mandatory: The images' sources into search."))
        self.SourcesSearchWidget.setTitle(translate("ConfigBox", "Sources available:"))
        self.SourcesSearchWidget.contextMenuUpdate()

        self.LanguageLabel.setText(translate("ConfigBox", "GUI Language:"))
        self.LanguageWidget.setStatusTip(translate("ConfigBox", "Language of the GUI. The texts are changed in live."))

        self.ImagesLanguagesLabel.setText(translate("ConfigBox", "Images' Languages:"))
        self.ImagesLanguagesWidget.setStatusTip(translate("ConfigBox", "Mandatory: The images' languages to download."))

        # Les icônes plantent PyQt5
        if QtVersion == 6:
            self.ImagesLanguagesWidget.setTitle(translate("ConfigBox", "Languages available:"), QIcon.fromTheme("languages", QIcon("Ressources:edit-undo.svg")))

        else:
            self.ImagesLanguagesWidget.setTitle(translate("ConfigBox", "Languages available:"))

        self.ImagesLanguagesWidget.contextMenuUpdate()


        # Widgets de la ReturnBox
        self.MoviesFindedBox.setTitle(translate("ReturnBox", "Movies finded:"))

        # Mise à jour des textes des QToolButtonCustom
        for MovieName in self.MoviesTab.keys():
            if "QToolButton" in self.MoviesTab[MovieName]:
                for Button in self.MoviesTab[MovieName]['QToolButton']:
                    Button.updateLang()

        # QStatusTip en cours
        self.StatusBar.clearMessage()


        # Dictionnaire de traduction global pour les messages d'erreur
        GlobalTr["Error"] = translate("ErrorMessage", "ERROR")
        GlobalTr["Info"] = translate("InfoMessage", "INFO")
        GlobalTr["SearchFinish"] = translate("InfoMessage", "Search video completed.")
        GlobalTr["SearchFinishNoImage"] = translate("InfoMessage", "Search video completed, no image for the defined languages.")
        GlobalTr["AutoOpenFolder"] = translate("InfoMessage", "Automatic opening of folder video.")
        GlobalTr["NameMissing"] = translate("ErrorMessage", "An error occurred when using the Movies function, the video names are missing.")
        GlobalTr["TryMax"] = translate("InfoMessage", "max number of try reached.")
        GlobalTr["TabName"] = translate("InfoMessage", "{0} ({1} results)", "{0} = Name of the movie, {1} = Number of movie returns by the search")
        GlobalTr["DateUnknow"] = translate("InfoMessage", "Date unknow")
        GlobalTr["DownloadFolderTitle"] = translate("ConfigBox", "Select the download folder")
        GlobalTr["AutoDl"] = translate("InfoMessage", "Auto download the movie's posters.")
        GlobalTr["AboutQt"] = translate("About", "About Qt")
        GlobalTr["WhatsUp"] = translate("About", "What's up ?")
        GlobalTr["Changelog"] = translate("About", "Changelog of hizo-tmdb")
        GlobalTr["About"] = translate("About", "About hizo-tmdb")
        GlobalTr["Close"] = translate("About", "Close")
        GlobalTr["hizo-tmdb"] = translate("About", """<html><head/><body><p align="center"><span style=" font-size:12pt; font-weight:600;">hizo-tmdb v{}</span></p><p><span style=" font-size:10pt;">GUI to download movie's posters from the <a href="https://www.themoviedb.org/"><b>TMDB</b> website</a>.</span></p><p><span style=" font-size:10pt;">This software is programed in python3 + QT6 (PySide6) and is licensed under </span><span style=" font-size:8pt; font-weight:600;"><a href="{}">GNU GPL v3</a></span><span style=" font-size:8pt;">.</span></p><p>&nbsp;</p><p align="right">Created by <span style=" font-weight:600;">Belleguic Terence</span> (<a href="mailto:hizo@free.fr">Hizoka</a>), 2021</p></body></html>""")


        GlobalTr["Id"] = translate("ErrorMessage", "the id")
        GlobalTr["Name"] = translate("ErrorMessage", "the name")
        GlobalTr["DownloadFolder"] = translate("ErrorMessage", "the download folder")
        GlobalTr["Folder"] = translate("ErrorMessage", "the download folder")
        GlobalTr["URLBase"] = translate("ErrorMessage", "the url base")

        GlobalTr["MoviesProgress"] = translate("ProgressBox", "Movies: %v / %m")
        GlobalTr["ImagesProgress"] = translate("ProgressBox", "Movie Id {} image: %v / %m")
        GlobalTr["ImagesWait"] = translate("ProgressBox", "Movie Id {} image please wait...")
        GlobalTr["NoImagesProgress"] = translate("ProgressBox", "Movie Id {} have no image for the defined languages.")


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CreateLanguagesJson(self):
        """Fonction de création de la liste des langues depuis le site TMDB."""
        # Variable indiquant si la boucle s'est terminé à TryMax
        TryMaxReached = True

        # Boucle au maximum au nombre de tentative
        for Try in range(Global['TryMax'] + 1):
            # Envoi de la requête à l'API de TMDB
            try:
                Requete = requests.get("https://api.themoviedb.org/3/configuration/languages", headers=Global['Headers'], timeout=Global['TimeOut'])

                # Si le code retour n'est pas 200, on relance la fonction
                if Requete.status_code != 200:
                    continue

            # En cas d'échec de connexion, on relance la fonction
            except:
                continue

            # Stoppe la boucle si tout est bien passé
            TryMaxReached = False
            break

        # Si le nombre de tentative a été atteint, arrêt complet de la recherche
        if TryMaxReached:
            self.AppendInformation([timeNow(), 'ERROR', "CreateLanguagesJson", f"{GlobalTr['ErrorMovies']} {GlobalTr['TryMax']}"])
            return

        Languages = []

        # Traitement du retour, la variable est rangée par nom de langue
        for Return in sorted(Requete.json(), key=lambda k: k['english_name']) :
            Language = {}
            Language["data"] = Return['iso_639_1']

            # Gestion du nom de la langue
            Language["text"] = Return['english_name']

            if Return['name']:
                Language["text"] += f" ({Return['name']})"

            # Gestion de l'icône
            if QFileInfo(f"Flags:/{Return['iso_639_1']}.svg").exists():
                Language["icon"] = f"Flags:{Return['iso_639_1']}.svg"

            Languages.append(Language)

        Languages.append({"text": 'null - Aucune', "data": "null"})

        # Vérifie qu'on a les droits d'écriture sur le dossier
        # ChatGPT propose : QFile(AbsoluteFolder).permissions() & QFileDevice.ReadUser
        if QFileDevice.WriteUser in QFile(AbsoluteFolder).permissions():
            File = f"{AbsoluteFolder}/Languages.json"
        else:
            File = f"{QDir.tempPath()}/Languages.json"

        with open(File, "w") as f:
            # Enregistrer le dictionnaire en JSON dans le fichier
            json.dump(Languages, f, indent=2)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def LoadImagesLanguages(self, Delete=False):
        """Fonction chargeant les langues depuis le fichier des langues."""

        # Adresse du fichier json depuis le dossier temporaire ou du logiciel
        if QFile(f"{QDir.tempPath()}/Languages.json").exists():
            JsonFile = QFile(f"{QDir.tempPath()}/Languages.json")

        else:
            JsonFile = QFile(f"{AbsoluteFolder}/Languages.json")

        # Si on doit réinitialiser le fichier
        if Delete:
            if JsonFile.exists():
                JsonFile.remove()

        # Si le fichier n'existe pas pas ou est vide
        if not JsonFile.exists() or JsonFile.size() == 0:
            # Création de la liste des langues en json
            self.CreateLanguagesJson()

            # Si le fichier n'existe toujours pas pas ou est vide
            if not JsonFile.exists() or JsonFile.size() == 0:
                # Colore les widgets car le fichier est inexistant
                self.ImagesLanguagesWidget.setPalette(PalettesWigets["LineEdit"])
                self.ReloadLanguagesButton.setPalette(PalettesWigets["Button"])

                return

        # Remise en couleur normale
        self.ImagesLanguagesWidget.setPalette(self.ImagesLanguagesWidget.style().standardPalette())
        self.ReloadLanguagesButton.setPalette(self.ReloadLanguagesButton.style().standardPalette())

        # Chargement du fichier json dans une liste de dictionnaires
        with open(JsonFile.fileName(), 'r') as f:
            # Charger le contenu du fichier en tant que dictionnaire Python
            LanguageList = json.load(f)

        # Chargement de la liste dans le Widget des langues
        self.ImagesLanguagesWidget.clear()
        self.ImagesLanguagesWidget.addItems(LanguageList)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SelectOutputFolder(self):
        """Fonction de modification du dossier d'enregistrement des images."""
        Folder = QDir.homePath()
        if Global['DownloadFolder']:
            Folder = Global['DownloadFolder'].absolutePath()

        # fenêtre de sélection du dossier de téléchargement
        DownloadFolderTemp = QFileDialog.getExistingDirectory(self, GlobalTr["DownloadFolderTitle"], Folder, QFileDialog.ShowDirsOnly)

        # Si la sélection du dossier est OK
        if DownloadFolderTemp:
            # Mise à jour du widget et execution de son événement
            self.DownloadFolderWidget.setText(DownloadFolderTemp)
            self.DownloadFolderWidget.textEdited.emit(DownloadFolderTemp)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def ProgressBarValue(self, ProgressBar):
        """Fonction incrémentant d'1 la barre de progression."""
        ProgressBar.setValue(ProgressBar.value() + 1)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def WorkInProgress(self, BlockingWidget = 'All'):
        """Fonction Appelée au lancement d'un travail afin de (dé)bloquer les widgets."""
        # Remise à 0 de la barre de progression
        self.ProgressBarMain.setValue(0)

        # Débloque le bouton d'annulation du travail
        self.ProgressButton.setEnabled(True)

        # Bloque différents widgets
        if BlockingWidget == 'Download':
            self.MoviesSearchedTextEdit.setEnabled(False)
            self.MoviesSearchedButton.setEnabled(False)

            # Bloque les boutons des films,
            # ne pas utiliser le blocage des pages du QTabWidget car ne fait pas la même chose
            # idem, ne pas bloquer self.MoviesTab[MovieName]['QWidget1'] car sinon, impossible de se promener dedans
            for MovieName in self.MoviesTab.keys():
                if "QToolButton" in self.MoviesTab[MovieName]:
                    for Button in self.MoviesTab[MovieName]['QToolButton']:
                        Button.setEnabled(False)

        elif BlockingWidget == 'Search':
            self.MoviesSearchedTextEdit.setEnabled(False)
            self.MoviesSearchedButton.setEnabled(False)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def StopWorkinProgress(self):
        """Fonction Appelée à l'arrêt d'un travail afin de (dé)bloquer les widgets."""
        # Mode auto download
        if self.AutoDlToolButton:
            self.AppendInformation([timeNow(), 'INFO', "StopWorkinProgress", GlobalTr["AutoDl"]])
            self.LaunchImagesDownload(self.AutoDlToolButton)
            self.AutoDlToolButton = None
            return

        # Suppression des dossiers de Dl en cours
        for FolderDl in Global["MovieFoldersDl"]:
            if FolderDl.exists():
                FolderDl.removeRecursively()

        # Reset de valeurs
        self.Progress["Movies"] = 0
        self.Progress["Download"] = 0

        # Si des boutons sont bleus, ils passent en rouge
        for MovieName in self.MoviesTab.keys():
            if "QToolButton" in self.MoviesTab[MovieName]:
                for Button in self.MoviesTab[MovieName]['QToolButton']:
                    Palette = Button.palette()

                    if Palette.color(QPalette.Button) == PalettesWigets["BlueColor"]:
                        Palette.setColor(QPalette.Button, PalettesWigets["RedColor"])
                        Button.setPalette(Palette)

        # Nettoyage de la liste des actions en attente
        self.GestionnaireActions.clear()

        # Variable permettant au travail en cours de s'arrêter
        # Global['StopThread'] = True
        self.stopWork.emit()

        # (Dé)Bloque différents widgets
        self.MoviesSearchedTextEdit.setEnabled(True)
        self.MoviesSearchedButton.setEnabled(True)
        self.ProgressButton.setEnabled(False)

        # Débloque les boutons des films avec un petit temps d'arrêt histoire que des widgets ne restent pas inactifs
        time.sleep(0.5)
        for MovieName in self.MoviesTab.keys():
            if self.MoviesTab[MovieName].get('QToolButton'):
                for Button in self.MoviesTab[MovieName]['QToolButton']:
                    Button.setEnabled(True)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def About(self):
        """Fonction affichant une fenêtre d'information sur le soft."""
        ### Boutton Qt
        AboutQt = QPushButton(QIcon.fromTheme("qt", QIcon("Ressources:qt.png")), GlobalTr["AboutQt"], self)

        ### Bouton Changelog
        WhatUpButton = QPushButton(QIcon.fromTheme("text-x-texinfo", QIcon("Ressources:text-x-texinfo.svg")), GlobalTr["WhatsUp"], self)

        ### Fenêtre d'info
        Win = QMessageBox(QMessageBox.NoIcon,
                          GlobalTr["About"],
                          GlobalTr["hizo-tmdb"].format(HizoTMDB.applicationVersion(), "http://www.gnu.org/copyleft/gpl.html"),
                          QMessageBox.Close, self)

        Win.setIconPixmap(QPixmap(QIcon.fromTheme("hizo-tmdb", QIcon("Ressources:hizo-tmdb.png")).pixmap(175)))
        Win.setMinimumWidth(800)
        Win.addButton(AboutQt, QMessageBox.HelpRole)
        Win.setDefaultButton(QMessageBox.Close)
        Win.button(QMessageBox.Close).setText(GlobalTr["Close"])

        # Ajoute le bouton quoi de neuf si le fichier existe
        if QDir().exists('/usr/share/doc/hizo-tmdb/changelog.Debian.gz'):
            Win.addButton(WhatUpButton, QMessageBox.NoRole)

        # Désactivation de la fermeture de la fenêtre au clic sur les boutons d'infos
        for Button in Win.buttons():
            if Button.text() in [GlobalTr["AboutQt"], GlobalTr["WhatsUp"]]:
                Button.clicked.disconnect()

        # Activation des actions des boutons
        AboutQt.clicked.connect(lambda: QMessageBox.aboutQt(self))
        WhatUpButton.clicked.connect(lambda: QDialogWhatsUp('/usr/share/doc/hizo-tmdb/changelog.Debian.gz', 'hizo-tmdb', GlobalTr["Changelog"], GlobalTr["Close"], self))

        # Affichage de la fenêtre
        Win.exec()


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def dragEnterEvent(self, event):
        """Fonction acceptant de glisser des fichiers sur la fenêtre."""
        event.accept()


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def dropEvent(self, event):
        """Fonction traitant les déposer de fichiers sur la fenêtre pour les ajouter à la liste des recherches."""
        self.MovieNamesCleaner(event.mimeData().urls())

        event.accept()


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def preClose(self):
        """Fonction appelée lors de la fermeture ou du reboot du logiciel."""
        # Curseur de chargement
        self.setCursor(Qt.WaitCursor)

        # Suppression des dossiers de Dl en cours
        for FolderDl in Global["MovieFoldersDl"]:
            if FolderDl.exists():
                FolderDl.removeRecursively()

        # Nettoyage de la liste des actions en attente
        self.GestionnaireActions.clear()

        # Arrêt du travail en cours
        Global['StopThread'] = True

        # Sauvegarde de la taille de la fenêtre
        Configs.setValue("WinWidth", self.width())
        Configs.setValue("WinHeight", self.height())

        # Sauvegarde de la taille des Splitters
        Configs.setValue("WinSplitter", self.WinSplitter.sizes())
        Configs.setValue("TopSplitter", self.TopSplitter.sizes())

        # Force l'écriture dans le fichier de config'
        Configs.sync()

        # Suppression du dossier temporaire
        if Global['TempFolder'].exists():
            Global['TempFolder'].removeRecursively()

        # Curseur normal
        self.setCursor(Qt.ArrowCursor)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def closeEvent(self, event):
        # Traitement avant la fermeture
        self.preClose()

        # Acceptation de la fermeture
        event.accept()


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def rebootEvent(self):
        """Ce n'est pas un vrai event, il est émit par le clic droit du bouton quitter."""
        # Traitement avant la fermeture
        self.preClose()

        # Restart de la commande
        python = sys.executable
        os.execl(python, python, * sys.argv)


#############################################################################
if __name__ == '__main__':
    ####################
    ### QApplication ###
    ####################
    ### Gestion de l'emplacement du script
    FileURL = QFileInfo(sys.argv[0])

    while FileURL.isSymLink():
        FileURL = QFileInfo(FileURL.symLinkTarget())

    AbsoluteFolder = FileURL.absolutePath()

    ### Gestion des ressources
    QDir.addSearchPath('Ressources', f"{AbsoluteFolder}/Ressources/")
    QDir.addSearchPath('Flags', f"{AbsoluteFolder}/Flags/")

    # Ajout du chargement de la feuille de style
    args = list(sys.argv)
    args[1:1] = ['-stylesheet', f'{AbsoluteFolder}/Styles.qss']

    # Création de l'application
    HizoTMDB = QApplication(args)
    HizoTMDB.setApplicationVersion("23.04.10.1") # Version de l'application
    HizoTMDB.setApplicationName("HizoTMDB") # Nom de l'application
    HizoTMDB.setWindowIcon(QIcon.fromTheme("hizo-tmdb", QIcon("Ressources:hizo-tmdb.png"))) # Icône de l'application

    # Permet d'afficher les tooltip instantanément, avec pisyde2 ça consomme 8% de cpu en continue
    if QtVersion == 6:
        MyStyle = MyProxyStyle()
        HizoTMDB.setStyle(MyStyle)

    ## Création ou ouverture du fichier de config
    Configs = QSettings(QSettings.NativeFormat, QSettings.UserScope, "hizo-tmdb")

    # Ne conserve que les valeurs du bloc hizo-tmdb, les autres ne sont pas pour ce soft
    # utilisation d'un Dictionnaire car ils sont globaux de base, donc pas besoin d'utiliser global
    Global = {}
    Global['StopThread'] = False

    Global['Token'] = Configs.value("Token")
    Global['Headers'] = { 'Authorization': f"Bearer {Global['Token']}", 'Content-Type': "application/json;charset=utf-8" }
    Global['ImageSize'] = int(Configs.value("ImageSize", 200))
    Global['NbPage'] = int(Configs.value("NbPage", 1))
    Global['WinWidth'] = int(Configs.value("WinWidth", 650))
    Global['WinHeight'] = int(Configs.value("WinHeight", 550))
    Global['IncludeAdultSearch'] = int(Configs.value("IncludeAdultSearch", 0))
    Global['TryMax'] = int(Configs.value("TryMax", 5))
    Global['AlternativeTitles'] = int(Configs.value("AlternativeTitles", 0))
    Global['SortSearch'] = int(Configs.value("SortSearch", 0))

    Global['TimeOut']  = (2, 2)
    Global["WorkChecker"] = {}
    Global["MovieFoldersDl"] = []
    Global["ProgressBars"] = {}
    Global["MovieNamesColors"] = {}

    # Boolean
    Global['SortReverse'] = False
    if Configs.value("SortReverse", "").lower() == "true":
        Global['SortReverse'] = True

    # Sources des recherches, films ou series
    Global['SourcesSearch'] = Configs.value("SourcesSearch", [])

    if isinstance(Global['SourcesSearch'], str):
        Global['SourcesSearch'] = Global['SourcesSearch'].split(", ")

    # Langues des AutoOptions
    Global['AutoOptions'] = Configs.value("AutoOptions", [])

    if isinstance(Global['AutoOptions'], str):
        Global['AutoOptions'] = Global['AutoOptions'].split(", ")

    # Langues des images
    Global['ImagesLanguages'] = Configs.value("ImagesLanguages", ["en", "fr", "null"])

    if isinstance(Global['ImagesLanguages'], str):
        Global['ImagesLanguages'] = Global['ImagesLanguages'].split(", ")

    # Types des images à télécharger
    Global['ImagesTypes'] = Configs.value("ImagesTypes", ["posters"])

    if isinstance(Global['ImagesTypes'], str):
        Global['ImagesTypes'] = Global['ImagesTypes'].split(", ")

    # Pour ces valeurs, il faut que ce soit des int et non des str
    Global['WinSplitter'] = list(Configs.value("WinSplitter", [0, 0]))

    for i, element in enumerate(Global['WinSplitter']):
        Global['WinSplitter'][i] = int(element)

    Global['TopSplitter'] = list(Configs.value("TopSplitter", [0, 0]))

    for i, element in enumerate(Global['TopSplitter']):
        Global['TopSplitter'][i] = int(element)


    ### Dossiers
    # Création du dossier temporaire
    TempFolder = QTemporaryDir(QDir.tempPath() + "/HizoTMDB").path()
    QDir().mkpath(TempFolder)
    Global['TempFolder'] = QDir(TempFolder)

    # Dossier de téléchargement
    DownloadFolder = Configs.value("DownloadFolder")

    if not DownloadFolder:
        DownloadFolder = QDir(QDir().absolutePath())

        if not DownloadFolder.absolutePath().startswith("/home"):
            DownloadFolder = QDir(QDir().homePath())

    else:
        DownloadFolder = QDir(DownloadFolder)

    Global['DownloadFolder'] = DownloadFolder


    ### Traductions
    # pylupdate5 *.py QWidgetsCustom/*.py -ts Languages/hizo-tmdb_fr_FR.ts Languages/hizo-tmdb_en_EN.ts # -noobsolete
    # lrelease Languages/*.ts
    Global['Language'] = Configs.value("Language", QLocale().nativeLanguageName().capitalize())
    Global["QTranslator"] = QTranslator() # Création d'un QTranslator
    GlobalTr = {}


    ### Dictionnaires permettant de mettre en avant certains widgets
    PalettesWigets = {}

    Brush = QBrush()
    Brush.setStyle(Qt.SolidPattern)

    # Jaune
    Brush.setColor(QColor(255, 255, 125))
    PalettesWigets["LineEdit"] = QPalette()
    PalettesWigets["LineEdit"].setBrush(QPalette.Active, QPalette.Base, Brush)
    PalettesWigets["YellowButton"] = QPalette()
    PalettesWigets["YellowButton"].setBrush(QPalette.Active, QPalette.Button, Brush)

    # Uniquement les couleurs car il faut les cumuler avec la palette des textes
    PalettesWigets["RedColor"] = QColor(255, 220, 220)
    PalettesWigets["GreenColor"] = QColor(220, 255, 220)
    PalettesWigets["BlueColor"] = QColor(220, 220, 255)


    ### Permet d'éviter les fameux Erreur de segmentation (core dumped)
    QCoreApplication.processEvents()

    HizoTMDBClass = WinHizoTMDB()

    QCoreApplication.processEvents()

    if QtVersion == 6:
        # PySide6
        sys.exit(HizoTMDB.exec())

    else:
        # PySide2
        sys.exit(HizoTMDB.exec_())
