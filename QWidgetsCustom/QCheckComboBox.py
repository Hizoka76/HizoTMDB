#!/bin/python3

# Basé sur : https://gis.stackexchange.com/questions/350148/qcombobox-multiple-selection-pyqt5

# Version: 21-10-25.2

# Old :
    # Mise à jour du texte du lineEdit lors d'un changement d'état d'une case à cochée
    # utilisation de itemChanged et non de dataChanged qui ne précise pas l'item modifié
    #self.model().itemChanged.connect(self.dataItemChanged)
        # => Déconne avec le 1er élément de la liste, utilisation de highlighted + installEventFilter

    # Donne la même apparence au QLineEdit qu'un QPushButton
    #palette = qApp.palette()
    #palette.setBrush(QPalette.Base, palette.button())
    #self.lineEdit().setPalette(palette)
        # => Ne semble pas spécialement utile et plante en PyQt5

    # Prise en compte de la touche entrée
    #self.activated.connect(self.entryKeyUsed)
        # => Non fonctionnel, car il affiché le text et non le data, utilisation de : highlighted + installEventFilter


# Infos :
    # self : QComboBox
    # self.lineEdit() : QLineEdit
    # self.model() : QStandardItemModel
    # self.view() : QListView
    # self.view().viewport() : QWidget


try:
    # Modules PySide6
    from PySide6.QtGui import QPalette, QFontMetrics, QStandardItem, QAction, QIcon, QCursor, QKeySequence
    from PySide6.QtWidgets import QComboBox, QStyledItemDelegate, QLineEdit, QListView, QMenu, QApplication
    from PySide6.QtCore import QEvent, Qt, QCoreApplication, QSize, QFileInfo, QMimeDatabase, QMimeType

    PySideVersion = 6

except:
    PySideVersion = 2

    try:
        # Modules PySide2
        from PySide2.QtGui import QPalette, QFontMetrics, QStandardItem, QIcon, QCursor, QKeySequence
        from PySide2.QtWidgets import QComboBox, QStyledItemDelegate, QLineEdit, QListView, QMenu, QApplication, QAction
        from PySide2.QtCore import QEvent, Qt, QCoreApplication, QSize, QFileInfo, QMimeDatabase, QMimeType

    except:
        try:
            # Modules PyQt5
            from PyQt5.QtGui import QPalette, QFontMetrics, QStandardItem, QIcon, QCursor, QKeySequence
            from PyQt5.QtWidgets import QComboBox, QStyledItemDelegate, QLineEdit, QListView, QMenu, QApplication, QAction
            from PyQt5.QtCore import QEvent, Qt, QCoreApplication, QSize, QFileInfo, QMimeDatabase, QMimeType

        except:
            print("QCheckComboBox : Impossible de trouver PySide6 / PySide2 / PyQt5.")
            exit()



class QCheckComboBox(QComboBox):
    # Subclass Delegate to increase item height
    class Delegate(QStyledItemDelegate):
        def sizeHint(self, option, index):
            size = super().sizeHint(option, index)
            size.setHeight(20)
            return size

    def __init__(self, Parent=None, *args, **kwargs):
        # Ne pas utiliser super().__init__(*args, **kwargs) car QComboBox ne connaît pas mes variables
        super().__init__()

        # Liste des arguments possibles
        CamelArgs = ["TristateMode", "CopyIcon", "UndoIcon", "RedoIcon", "AllCheckIcon", "AllUncheckIcon", "AllPatriallyCheckIcon", "DefaultValuesIcon", "Title", "TitleIcon", "Items", "DefaultValues"]

        # Retravaille le dictionnaire pour prise en compte d'une mauvais casse
        for Key, Value in dict(kwargs).items():
            # Si la clé est bien écrite, on continue
            if Key in CamelArgs:
                continue

            else:
                for Arg in CamelArgs:
                    # Si la clé existe mais avec la mauvaise casse, on ajoute la version camel
                    if Key.lower() == Arg.lower():
                        kwargs[Arg] = Value


        # La QComboBox est éditable pour afficher un texte mais est en lecture seule pour l'utilisateur
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)

        # Pour connaitre l'item surligné par la souris ou par le clavier'
        self.ItemHighlighted = None
        self.highlighted.connect(self.comboHighlighted)

        # Mode 3 états des cases à cocher
        self.TristateMode = False

        # Indicateur de la présence d'un titre pour ne pas prendre en compte le 1er élément
        self.TitleExists = False

        # Liste des valeurs par défaut
        self.DefaultValuesCase = False
        self.DefaultValuesSave = None
        self.DefaultValues = {
            Qt.Checked: [],
            Qt.PartiallyChecked: []
            }

        # Use custom delegate
        self.setItemDelegate(QCheckComboBox.Delegate())

        # Mise en place de la surveillance des événements du lineEdit
        self.lineEdit().installEventFilter(self)
        self.closeOnLineEditClick = False

        # Mise en place de la surveillance des événements du QWidget
        self.view().viewport().installEventFilter(self)
        self.model().installEventFilter(self)

        # Pour la gestion du clic droit sur la flèche et le blocage des touches flèches
        self.installEventFilter(self)

        # Pour la gestion du coche lors d'un clic
        self.view().installEventFilter(self)

        # Variables pour la gestion de l'historique
        self.historyActions = []
        self.historyIndex = -1
        self.historyLastAction = None
        self.spaceKeyBlock = False

        # Icônes par défaut du du menu
        self.MenuIcons = {
            "Copy": QIcon.fromTheme("edit-select-text"),
            "Undo": QIcon.fromTheme("edit-undo"),
            "Redo": QIcon.fromTheme("edit-redo"),
            "AllCheck": QIcon.fromTheme("edit-select-all"),
            "AllPatriallyCheck": QIcon.fromTheme("select-rectangular"),
            "AllUncheck": QIcon.fromTheme("edit-select-none"),
            "DefaultValues": QIcon.fromTheme("edit-reset")
            }


        # Si le mode TristateMode est passé lors de la création de la classe
        if "TristateMode" in kwargs:
            self.setTristateMode(kwargs["TristateMode"])


        # Si des icônes sont passées lors de la création de la classe
        self.setIcons(
            Copy=kwargs.get("CopyIcon"),
            Undo=kwargs.get("UndoIcon"),
            Redo=kwargs.get("RedoIcon"),
            AllCheck=kwargs.get("AllCheckIcon"),
            AllUncheck=kwargs.get("AllUncheckIcon"),
            AllPatriallyCheck=kwargs.get("AllPatriallyCheckIcon"),
            DefaultValues=kwargs.get("DefaultValuesIcon"),
            )

        # Si le titre est passé lors de la création de la classe
        if "Title" in kwargs:
            # L'icône est facultative
            self.setTitle(kwargs["Title"], self.iconCreation(kwargs.get("TitleIcon")))

        # Si des items sont passées lors de la création de la classe
        if "Items" in kwargs:
            self.addItems(kwargs["Items"])

        # Si le respect de la casse par défaut est précisée
        if "DefaultValuesCase" in kwargs:
            if isinstance(kwargs["DefaultValuesCase"], bool) or kwargs["DefaultValuesCase"] in [0, 1, "0", "1", "True", "False"]:
                self.DefaultValuesCase = bool(kwargs["DefaultValuesCase"])

        # Si des valeurs par défaut ont été données
        if "DefaultValues" in kwargs:
            if isinstance(kwargs["DefaultValues"], dict):
                for State, Items in kwargs["DefaultValues"].items():
                    self.setDefaultValues(State, Items, self.DefaultValuesCase)

        # Chargement des textes de base
        self.updateLang()


    #========================================================================
    def setIcons(self, **kwargs):
        """Fonction permettant de changer les icônes par défaut."""
        # Arguments acceptés, sert à ne pas prendre en compte la casse
        ArgumentsOK = {
            "copy": "Copy",
            "undo": "Undo",
            "redo": "Redo",
            "allcheck": "AllCheck",
            "alluncheck": "AllUncheck",
            "allpatriallycheck": "AllPatriallyCheck",
            "defaultvalues": "DefaultValues"
            }

        # Arguments passés
        FunctionArgs = {}
        for Arg in kwargs.keys():
            FunctionArgs[Arg.lower()] = Arg

        # Boucle sur les arguments valides
        for IconName in ArgumentsOK.keys():
            # Si l'argument OK existe dans la liste de ceux rentrés
            if IconName in FunctionArgs.keys():
                Icon = kwargs.get(FunctionArgs[IconName])

                if Icon:
                    self.MenuIcons[ArgumentsOK[IconName]] = self.iconCreation(Icon)


    #========================================================================
    def iconCreation(self, Icon):
        """Fonction renvoyant une QIcon depuis une QIcon ou un texte."""
        if Icon is None:
            return QIcon()

        # Si la valeur est déjà une QIcon, on la renvoie directement
        if isinstance(Icon, QIcon):
            return Icon

        # Si c'est un texte, on la transforme en QIcon avant de le renvoyer
        elif isinstance(Icon, str):
            File = QFileInfo(Icon)
            MimeBase = QMimeDatabase()
            MimeType = MimeBase.mimeTypeForFile(Icon).name().split("/")[0].lower()

            # Si l'image existe
            if File.exists() and MimeType == "image":
                return QIcon(Icon)

            # Si le texte n'a pas d'extension ni de path
            if not File.completeSuffix() and File.filePath() == Icon:
                return QIcon.fromTheme(Icon)

            # Si ce n'est pas une image on renvoie un QIcon vide
            if MimeType != "image":
                return QIcon()


    #========================================================================
    def setTristateMode(self, TristateMode):
        """Fonction permettant d'activer ou non le mode 3états des cases à cocher."""
        # Si le type de valeur reçue n'est pas celle attendue, on stoppe
        if not isinstance(TristateMode, bool) and TristateMode not in [0, 1, "0", "1", "True", "False"]:
            return

        # Force le bool
        self.TristateMode = bool(TristateMode)

        # (Dés)active le mode 3 états des cases à cocher
        for i in range(self.model().rowCount()):
            if self.model().item(i) is not None:
                self.model().item(i).setUserTristate(TristateMode)
                self.model().item(i).setAutoTristate(TristateMode)

        # Mise à jour du menu
        self.updateLang()


    #========================================================================
    def newCheckState(self, ActualState):
        """Fonction indiquant le nouvel état d'une case à cocher."""
        if ActualState == Qt.Checked:
            NewState = Qt.Unchecked

        elif ActualState == Qt.Unchecked:
            # Mode 3 états
            if self.TristateMode:
                NewState = Qt.PartiallyChecked

            # Mode 2 états
            else:
                NewState = Qt.Checked

        elif ActualState == Qt.PartiallyChecked:
            NewState = Qt.Checked

        return NewState


    #========================================================================
    def updateLang(self):
        """Fonction permettant de mettre à jour les textes lors des changements de langue."""
        # Création d'un menu vide
        self.contextMenu = QMenu()
        self.contextMenu.installEventFilter(self)

        # Création et ajout de l'action de copie du texte
        CopyAction = QAction(self.MenuIcons["Copy"], QCoreApplication.translate("QCheckComboBox", "Copy values choosen"), self.contextMenu)
        CopyAction.setShortcut(QKeySequence("Ctrl+C"))
        CopyAction.setShortcutContext(Qt.ApplicationShortcut)
        CopyAction.triggered.connect(self.copyText)
        self.contextMenu.addAction(CopyAction)

        # Création et ajout de l'action d'annulation d'action
        self.UndoAction = QAction(self.MenuIcons["Undo"], QCoreApplication.translate("QCheckComboBox", "Undo Action"), self.contextMenu)
        self.UndoAction.setShortcut(QKeySequence("Ctrl+Z"))
        self.UndoAction.triggered.connect(lambda: self.setReUndoAction("Undo"))
        self.UndoAction.setEnabled(False)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.UndoAction)

        # Création et ajout de l'action d'annulation d'action
        self.RedoAction = QAction(self.MenuIcons["Redo"], QCoreApplication.translate("QCheckComboBox", "Redo Action"), self.contextMenu)
        self.RedoAction.setShortcut(QKeySequence("Ctrl+Y"))
        self.RedoAction.triggered.connect(lambda: self.setReUndoAction("Redo"))
        self.RedoAction.setEnabled(False)
        self.contextMenu.addAction(self.RedoAction)

        # Création et ajout de l'action de cochage
        AllCheck = QAction(self.MenuIcons["AllCheck"], QCoreApplication.translate("QCheckComboBox", "Check All Items"), self.contextMenu)
        AllCheck.triggered.connect(lambda: self.setStateAll(Qt.Checked))
        AllCheck.setShortcut(QKeySequence("Ctrl+A"))
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(AllCheck)

        # Création et ajout de l'action de semi cochage
        if self.TristateMode:
            AllSemiCheck = QAction(self.MenuIcons["AllPatriallyCheck"], QCoreApplication.translate("QCheckComboBox", "Partially Check All Items"), self.contextMenu)
            AllSemiCheck.triggered.connect(lambda: self.setStateAll(Qt.PartiallyChecked))
            AllSemiCheck.setShortcut(QKeySequence("Ctrl+P"))
            self.contextMenu.addAction(AllSemiCheck)

        # Création et ajout de l'action de décochage
        AllUncheck = QAction(self.MenuIcons["AllUncheck"], QCoreApplication.translate("QCheckComboBox", "Uncheck All Items"), self.contextMenu)
        AllUncheck.triggered.connect(lambda: self.setStateAll(Qt.Unchecked))
        AllUncheck.setShortcut(QKeySequence("Ctrl+U"))
        self.contextMenu.addAction(AllUncheck)

        # Création de l'action de restauration des données par défaut
        if self.DefaultValues[Qt.Checked] or self.DefaultValues[Qt.PartiallyChecked]:
            self.contextMenu.addSeparator()
            ResetDefaultValues = QAction(self.MenuIcons["DefaultValues"], QCoreApplication.translate("QCheckComboBox", "Restore the default values"), self.contextMenu)
            ResetDefaultValues.triggered.connect(self.resetDefaultValues)
            ResetDefaultValues.setShortcut(QKeySequence("Ctrl+R"))
            self.contextMenu.addAction(ResetDefaultValues)


    #========================================================================
    def comboHighlighted(self, Index):
        """Fonction conservant l'item actuellement surligné, utile lors de l'utilisation du clavier."""
        self.ItemHighlighted = Index


    #========================================================================
    def resizeEvent(self, Event):
        # Recompute text to elide as needed
        self.updateText()
        super().resizeEvent(Event)


    #========================================================================
    def eventFilter(self, Object, Event):
        """Fonction surveillant toutes les évènements des widgets mis sur écoute."""
        # Cas de la combobox
        if Object == self:
            # Si on utilise les touches des flèches pour naviguer, ça inverse l'état des cases
            # 1 clic sur la combobox, un 2e pour fermer la fenêtre puis utilisation des flèches pour une navigation invisible

            # Les touches affichent le menu ou ne font rien pour ne pas cocher des cases sans le voir
            if Event.type() == QEvent.KeyPress:
                # Prise en compte des raccourcis claviers, mieux géré ainsi qu'avec QShortcut
                if self.shortcutEvent(Event):
                    return True

                elif Event.key() in [Qt.Key_Down, Qt.Key_Space, Qt.Key_Return, Qt.Key_Enter, Qt.Key_Tab]:
                    self.popupEvent()

                return True

            # Si c'est un clic droit sur la petite flèche, on affiche un menu modifié
            elif Event.type() == QEvent.ContextMenu:
                self.menuEvent()

                # Bloque l'événement
                return True


        # Cas du lineEdit
        elif Object == self.lineEdit():
            # Si l'événement est le relâchement d'un clic (Event.button() pour savoir lequel)
            if Event.type() == QEvent.MouseButtonRelease:
                self.popupEvent()

                # Bloque l'événement
                return True

            # Si c'est un clic droit, on affiche un menu modifié
            elif Event.type() == QEvent.ContextMenu:
                self.menuEvent()

                # Bloque l'événement
                return True


        # Cas du viewport
        elif Object == self.view().viewport():
            # Si l'événement est le relâchement d'un clic (Event.button() si besoin pour savoir lequel)
            if Event.type() == QEvent.MouseButtonRelease:
                # Si c'est un clic gauche, on modifie l'état de la case à cocher
                if Event.button() == Qt.MouseButton.LeftButton:
                    # Récupération de la case à cocher concernée
                    Index = self.view().indexAt(Event.pos())
                    Row = Index.row()
                    Item = self.model().item(Row)

                    # Bloque les actions de la 1ere ligne s'il y a un titre
                    if Row == 0 and self.TitleExists:
                        return True

                    # Nouvel état à donner à la case à cocher
                    State = self.newCheckState(Item.checkState())

                    # Mise à jour de l'item
                    self.setStateItem(State, Row)

                # Si c'est un clic droit, on affiche le menu d'action
                elif Event.button() == Qt.MouseButton.RightButton:
                    self.menuEvent()

                # Bloque l'événement
                return True


        # Cas du view
        elif Object == self.view():
            if Event.type() == QEvent.KeyPress:
                # Prise en compte des raccourcis claviers, mieux géré ainsi qu'avec QShortcut
                if self.shortcutEvent(Event):
                    return True

                # Lors de l'utilisation des touches espace, entrée x 2
                elif Event.key() in [Qt.Key_Space, Qt.Key_Enter, Qt.Key_Return]:
                    # Bloque les actions de la 1ere ligne s'il y a un titre
                    if self.ItemHighlighted == 0 and self.TitleExists:
                        return True

                    # Nouvel état à donner à la case à cocher
                    State = self.newCheckState(self.model().item(self.ItemHighlighted).checkState())

                    # Si les touches entrées ont été utilisées et qu'il y a un titre, on remet le titre pour conserver son icône
                    if Event.key() in [Qt.Key_Enter, Qt.Key_Return] and self.TitleExists:
                        self.setCurrentIndex(0)

                    # Mise à jour de l'item
                    self.setStateItem(State, self.ItemHighlighted)

                    # Bloque l'événement
                    return True


        # Dans le cas du QMenu
        elif Object == self.contextMenu:
            if Event.type() == QEvent.KeyPress:
                # Prise en compte des raccourcis claviers, mieux géré ainsi qu'avec QShortcut
                if self.shortcutEvent(Event):
                    # Fermeture du menu
                    self.contextMenu.close()

                    # Bloque l'événement
                    return True


        ### Autorise l'événement
        return False


    #========================================================================
    def shortcutEvent(self, Event):
        """Fonction de gestion des raccourcis clavier."""
        # S'il y a combinaison de ctrl + une des touches suivantes, on exécute la commande associée
        if Event.modifiers() == Qt.ControlModifier and Event.key() in [Qt.Key_C, Qt.Key_Z, Qt.Key_Y, Qt.Key_A, Qt.Key_P, Qt.Key_U, Qt.Key_R]:
            if Event.key() == Qt.Key_C:
                self.copyText()

            elif Event.key() == Qt.Key_Z:
                self.setReUndoAction("Undo")

            elif Event.key() == Qt.Key_Y:
                self.setReUndoAction("Redo")

            elif Event.key() == Qt.Key_A:
                self.setStateAll(Qt.Checked)

            elif Event.key() == Qt.Key_P and self.TristateMode:
                self.setStateAll(Qt.PartiallyChecked)

            elif Event.key() == Qt.Key_U:
                self.setStateAll(Qt.Unchecked)

            elif Event.key() == Qt.Key_R and (self.DefaultValues[Qt.Checked] or self.DefaultValues[Qt.PartiallyChecked]):
                self.resetDefaultValues()

            return True

        return False


    #========================================================================
    def popupEvent(self):
        """Fonction gérant l'affichage ou son contraire de la liste des propositions."""
        # Si la popup est visible, on la case sinon on l'affiche
        if self.closeOnLineEditClick:
            self.hidePopup()

        else:
            self.showPopup()


    #========================================================================
    def menuEvent(self):
        """Fonction gérant l'affichage de la liste des actions."""
        if PySideVersion == 6:
            self.contextMenu.exec(QCursor.pos())

        else:
            self.contextMenu.exec_(QCursor.pos())


    #========================================================================
    def showPopup(self):
        """Fonction affichant la liste des propositions."""
        super().showPopup()

        # Item survolé à l'affichage de la liste
        self.ItemHighlighted = 0

        # Variable permettant à l’évènement de savoir s'il doit afficher ou cacher la popup
        self.closeOnLineEditClick = True


    #========================================================================
    def hidePopup(self):
        """Fonction cachant la liste des propositions."""
        super().hidePopup()

        # Permet d'éviter la réouverture immédiate lors d'un clic sur le lineEdit
        self.startTimer(100)

        # Met à jour le texte visible du lineEdit
        self.updateText()


    #========================================================================
    def timerEvent(self, Event):
        # Après le timeout, kill le timer, et réactive le clic sur le lineEdit
        self.killTimer(Event.timerId())

        self.closeOnLineEditClick = False


    #========================================================================
    def updateText(self):
        """Fonction d'affichage des data cochés."""
        # Récupération du texte
        text = self.currentText()

        # Gestion de l'ajout du ... en fonction de la place dispo
        metrics = QFontMetrics(self.lineEdit().font())
        elidedText = metrics.elidedText(text, Qt.ElideRight, self.lineEdit().width())
        self.lineEdit().setText(elidedText)


    #========================================================================
    def addItem(self, text, data=None, state=None, icon=None, default=True):
        """Fonction de création de l'item."""
        # Création de l'item de base avec son texte et ses flags
        item = QStandardItem()
        item.setEditable(False)
        item.setText(text)
        item.setData(Qt.Unchecked, Qt.CheckStateRole)

        if self.TristateMode:
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsUserTristate)

        else:
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)

        # Utilisation de la data indiquée ou du texte
        if data is None:
            data = text

        item.setData(data, Qt.UserRole)

        # Si utilisation d'une icône valide, plante avec PySide2 et PyQt5
        if PySideVersion == 6 and icon is not None and not icon.isNull():
            item.setIcon(icon)

        # Si l'état de la case à cocher est précisée
        if state is not None:
            item.setCheckState(state)

        # Ajout de l'item
        self.model().appendRow(item)

        # Met à jour les valeurs par défaut, en utilisant le dictionnaire comme arguments
        if self.DefaultValuesSave and default:
            self.setDefaultValues(**self.DefaultValuesSave)


    #========================================================================
    def addItems(self, Items):
        """Fonction de chargement d'item depuis une liste de dictionnaire.
        Les items sont de type : {text, data, state, icon}"""
        # Traite les dictionnaires un à un
        for Item in Items:
            # Si ni data ni texte, on le saute
            if "data" not in Item.keys() and "text" not in Item.keys():
                continue

            # Si une donnée est manquante, on met une valeur de base
            if "text" not in Item.keys():
                Item["text"] = Item["data"]

            if "data" not in Item.keys():
                Item["data"] = None

            if "state" not in Item.keys():
                Item["state"] = None

            if "icon" not in Item.keys():
                Item["icon"] = None

            if Item != Items[-1]:
                Item["default"] = False
            else:
                Item["default"] = True

            # Création de la ligne
            self.addItem(Item["text"], Item["data"], Item["state"], Item["icon"], Item["default"])


    #========================================================================
    def setStateItem(self, State, Indexes):
        """Fonction de modification de l'état de la case à cocher.
        Cette fonction est appelée par les fonctions de modifications
        de l'état des cases à cocher mais aussi lors du clic sur une case."""

        # Blocage de l'utilisation de la touche espace
        self.spaceKeyBlock = True

        # Si Indexes n'est pas une liste, on la change
        if not isinstance(Indexes, list):
            if isinstance(Indexes, (str, int)):
                Indexes = [Indexes]

        # Permet de regrouper les actions quand elles ont lieu en même temps
        History = []

        for Index in Indexes:
            # Ne met à jour l'item que si besoin, ne prend pas en compte le titre
            if self.model().item(Index).checkState() != State and self.model().item(Index).data(Qt.UserRole):
                # Valeur actuelle de la case
                ActualState = self.model().item(Index).checkState()

                # Mise à jour de l'état de la case à cocher
                self.model().item(Index).setCheckState(State)

                # Ajout de l'action à l'historique temporaire
                History.append([Index, ActualState, State])

        # Gestion de la variable de l'historique
        if History:
            self.updateHistoryActions(History)

        # Mise à jour du texte de la QLineEdit
        self.updateText()

        # Déblocage de l'utilisation de la touche espace
        self.spaceKeyBlock = False


    #========================================================================
    def setStateItems(self, State, Values, CaseSensitive=False):
        """Fonction de modification de l'état de la case à cocher en se basant sur sa data."""
        Indexes = []

        # Utilisation d'une liste obligatoire
        if not isinstance(Values, list):
            if isinstance(Values, (str, int)):
                Values = [Values]

        # Traitement des valeurs
        for Value in Values:
            # Si la valeur est un  nombre, on le considère comme un index
            if isinstance(Value, int):
                if self.TitleExists:
                    Indexes.append(Value + 1)

                else:
                    Indexes.append(Value)

            # Si c'est un texte, on le recherche dans les data et les textes
            elif isinstance(Value, str):
                for Index in range(self.model().rowCount()):
                    Item = self.model().item(Index)

                    # Mode avec prise en compte de la casse
                    if CaseSensitive:
                        if Value in (Item.data(Qt.UserRole), Item.text()):
                            Indexes.append(Index)
                            break

                    # Mode sans prise en compte de la casse
                    else:
                        if Value.lower() in (Item.data(Qt.UserRole).lower(), Item.text().lower()):
                            Indexes.append(Index)
                            break


        # Traite les indexes retournés
        if Indexes:
            self.setStateItem(State, Indexes)


    #========================================================================
    def setStateAll(self, State):
        """Fonction de modification de l'état de la case à cocher de tous les items."""
        Indexes = []

        # Traite tous les items un à un
        for Index in range(self.model().rowCount()):
            Indexes.append(Index)

        # Traite les cases retournées
        if Indexes:
            self.setStateItem(State, Indexes)


    #========================================================================
    def setTitle(self, Text, Icon=None):
        """Fonction créant un item en début de liste afin d'utiliser son icône dans le QLineEdit."""
        # Création et configuration de l'item
        FirstItem = QStandardItem()
        FirstItem.setText(Text)
        FirstItem.setFlags(Qt.NoItemFlags)
        FirstItem.setData("", Qt.UserRole)
        FirstItem.setTextAlignment(Qt.AlignHCenter)

        if isinstance(Icon, QIcon):
            FirstItem.setIcon(Icon)

        elif isinstance(Icon, str):
            FirstItem.setIcon(Icon)

        # S'il y a déjà un titre, on l'efface
        if self.TitleExists:
            self.model().removeRow(0)

        # Insertion du titre
        self.model().insertRow(0, FirstItem)

        # Utilisation du titre pour utiliser l'icône
        if Icon is not None:
            self.setCurrentIndex(0)

        # Mise à jour de la variable indiquant qu'il y a un titre
        self.TitleExists = True


    #========================================================================
    def setDefaultValues(self, State, Values, CaseSensitive=False):
        """Fonction prenant les valeurs par défaut."""
        # Bloque la fonction s'il n'y a pas encore de choix, elle sera rappelée plus tard
        if self.model().rowCount() == 0 or (self.model().rowCount() == 1 and self.TitleExists):
            self.DefaultValuesSave = {
                "State": State,
                "Values": Values,
                "MatchFlag": MatchFlag
                }
            return

        # Si l'état n'existe pas, on arrête là
        if State not in [Qt.Checked, Qt.PartiallyChecked]:
            return

        # Si Textes n'est pas une liste de data, on le change en liste
        if not isinstance(Values, list):
            if isinstance(Values, (str, int)):
                Values = [Values]

        # Traitement des valeurs
        for Value in Values:
            # Si la valeur est un  nombre, on le considère comme un index
            if isinstance(Value, int):
                if self.TitleExists:
                    Item = self.model().item(Value + 1)

                else:
                    Item = self.model().item(Value)

                if Item:
                    self.DefaultValues[State].append(Item)

            # Si c'est un texte, on le recherche dans les data et les textes
            elif isinstance(Value, str):
                for Index in range(self.model().rowCount()):
                    Item = self.model().item(Index)

                    # Mode avec prise en compte de la casse
                    if CaseSensitive:
                        if Value in (Item.data(Qt.UserRole), Item.text()):
                            self.DefaultValues[State].append(Item)
                            break

                    # Mode sans prise en compte de la casse
                    else:
                        if Value.lower() in (Item.data(Qt.UserRole).lower(), Item.text().lower()):
                            self.DefaultValues[State].append(Item)
                            break


        # Déblocage de l'action
        if self.DefaultValues[Qt.Checked] or self.DefaultValues[Qt.PartiallyChecked]:
            print("ici", self.DefaultValues)
            self.updateLang()


    #========================================================================
    def resetDefaultValues(self):
        """Fonction de remise en état des valeurs par défaut."""
        if self.DefaultValues[Qt.Checked] or self.DefaultValues[Qt.PartiallyChecked]:
            # Décoche tout
            self.setStateAll(Qt.Unchecked)
            print("putain :", self.DefaultValues)
            # Coche les différentes cases
            for State, Items in self.DefaultValues.items():
                Indexes = []

                for Item in Items:
                    print(State, Item.text())
                    if Item:
                        Indexes.append(Item.index().row())

                self.setStateItem(State, Indexes)


    #========================================================================
    def updateHistoryActions(self, Action):
        # S'il y a eu des retours en arrière
        if self.historyIndex != -1:
            # Suppression de toutes les actions suivantes
            self.historyActions = self.historyActions[0:self.historyIndex]

        # Ajout de la nouvelle action
        self.historyActions.append(Action)

        # Réinitialisation des valeurs
        self.historyIndex = -1
        self.historyLastAction = None

        # Mise à jour des items de retour en arrière et en avant
        self.UndoAction.setEnabled(True)
        self.RedoAction.setEnabled(False)


    #========================================================================
    def setReUndoAction(self, Action):
        """Fonction de retour en arrière ou en avant dans les actions."""
        # Si l'historique est vide, on arrête là
        if not len(self.historyActions):
            return

        # Blocage de l'utilisation de la touche espace
        self.spaceKeyBlock = True

        # Nouvel index, si c'est une nouvelle action, on reste sur l'élément actuel
        if Action == "Undo":
            # Recule dans la liste dans l'historique des actions si la précédente action était déjà un retour en arrière
            if self.historyLastAction == "Undo":
                self.historyIndex -= 1

            if self.historyIndex * -1 > len(self.historyActions):
                self.historyIndex = len(self.historyActions) * -1

            # Gestion de l'état des items de déplacement dans l'historique
            if self.historyIndex == len(self.historyActions) * -1:
                self.UndoAction.setEnabled(False)
                self.RedoAction.setEnabled(True)

            else:
                self.UndoAction.setEnabled(True)
                self.RedoAction.setEnabled(True)


        elif Action == "Redo":
            # Avance dans la liste dans l'historique des actions si la précédente action était déjà un retour en avant
            if self.historyLastAction == "Redo":
                self.historyIndex += 1

            # Si on remonte trop haut, on retourne à -1
            if self.historyIndex > -1:
                self.historyIndex = -1

            # Gestion de l'état des items de déplacement dans l'historique
            if self.historyIndex == -1:
                self.UndoAction.setEnabled(True)
                self.RedoAction.setEnabled(False)

            else:
                self.UndoAction.setEnabled(True)
                self.RedoAction.setEnabled(True)


        # Gestion par groupe d'actions
        for Index, OldState, NewState in self.historyActions[self.historyIndex]:
            # Retour en arrière
            if Action == "Undo":
                self.model().item(Index).setCheckState(OldState)

            # Retour en avant
            else:
                self.model().item(Index).setCheckState(NewState)


        # Mise de la dernière action
        self.historyLastAction = Action

        # Mise à jour du texte du QLineEdit
        self.updateText()

        # Déblocage de l'utilisation de la touche espace
        self.spaceKeyBlock = False


    #========================================================================
    def copyText(self):
        """Fonction renvoyant le texte affiché sur le QLineEdit dans le presse papier."""
        QApplication.clipboard().setText(self.currentText())


    #========================================================================
    def currentText(self, Separator=', '):
        """Fonction renvoyant le texte affiché sur le QLineEdit."""
        return Separator.join(self.currentData())


    #========================================================================
    def currentData(self):
        """Fonction renvoyant les data des cases cochées."""
        # Data des cases à cocher
        CheckOK = []

        # Tourne sur toutes les cases à cocher
        for i in range(self.model().rowCount()):
            # Saute les éléments vides
            if self.model().item(i) is None:
                continue

            data = self.model().item(i).data(Qt.UserRole)

            # Ne traite que les cases cochées
            if self.model().item(i).checkState() == Qt.Checked:
                # Ajoute sa data à la liste
                CheckOK.append(data)

            elif self.model().item(i).checkState() == Qt.PartiallyChecked:
                # Ajoute sa data à la liste
                CheckOK.append('[' + data + ']')

        # Envoi de la liste des cases cochées
        return CheckOK

