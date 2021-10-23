#!/bin/python3

# Basé sur : https://gis.stackexchange.com/questions/350148/qcombobox-multiple-selection-pyqt5


try:
    # Modules PySide6
    from PySide6.QtGui import QPalette, QFontMetrics, QStandardItem, QAction, QIcon, QCursor
    from PySide6.QtWidgets import QComboBox, QStyledItemDelegate, QLineEdit, QListView, QMenu, QApplication
    from PySide6.QtCore import QEvent, Qt, QCoreApplication, QSize, QItemSelection

    PySideVersion = 6

except:
    PySideVersion = 2

    try:
        # Modules PySide2
        from PySide2.QtGui import QPalette, QFontMetrics, QStandardItem, QIcon, QCursor
        from PySide2.QtWidgets import QComboBox, QStyledItemDelegate, QLineEdit, QListView, QMenu, QApplication, QAction
        from PySide2.QtCore import QEvent, Qt, QCoreApplication, QSize, QItemSelection

    except:
        try:
            # Modules PyQt5
            from PyQt5.QtGui import QPalette, QFontMetrics, QStandardItem, QIcon, QCursor
            from PyQt5.QtWidgets import QComboBox, QStyledItemDelegate, QLineEdit, QListView, QMenu, QApplication, QAction
            from PyQt5.QtCore import QEvent, Qt, QCoreApplication, QSize, QItemSelection

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
        super().__init__(*args, **kwargs)

        # Infos :
        # self : QComboBox
        # self.lineEdit() : QLineEdit
        # self.model() : QStandardItemModel
        # self.view() : QListView
        # self.view().viewport() : QWidget

        # La QComboBox est éditable pour afficher un texte mais est en lecture seule pour l'utilisateur
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)

        # Prise en compte de la touche entrée
        self.activated.connect(self.entryKeyUsed)

        # Donne la même apparence au QLineEdit qu'un QPushButton
        #palette = qApp.palette()
        #palette.setBrush(QPalette.Base, palette.button())
        #self.lineEdit().setPalette(palette)

        # Mode 3 états des cases à cocher
        self.TristateMode = False

        # Indicateur de la présence d'un titre pour ne pas prendre en compte le 1er élément
        self.TitleExists = False

        # Use custom delegate
        self.setItemDelegate(QCheckComboBox.Delegate())

        # Mise à jour du texte du lineEdit lors d'un changement d'état d'une case à cochée
        # utilisation de itemChanged et no dataChanged qui ne précise pas l'item modifié
        self.model().itemChanged.connect(self.dataItemChanged)

        # Mise en place de la surveillance des événements du lineEdit
        self.lineEdit().installEventFilter(self)
        self.closeOnLineEditClick = False

        # Mise en place de la surveillance des événements du QWidget
        self.view().viewport().installEventFilter(self)

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
        self.CopyIcon = QIcon.fromTheme("edit-select-text")
        self.UndoIcon = QIcon.fromTheme("edit-undo")
        self.RedoIcon = QIcon.fromTheme("edit-redo")
        self.AllCheckIcon = QIcon.fromTheme("edit-select-all")
        self.AllPatriallyCheckIcon = QIcon.fromTheme("select-rectangular")
        self.AllUncheckIcon = QIcon.fromTheme("edit-select-none")

        Action = QAction()
        Action.setIcon(QIcon.fromTheme("select-rectangular"))
        self.lineEdit().addAction(Action, QLineEdit.TrailingPosition)

        # Chargement des textes de base
        self.updateLang()


    #========================================================================
    def setIcons(self, CopyIcon=None, UndoIcon=None, RedoIcon=None, AllCheckIcon=None, AllUncheckIcon=None, AllPatriallyCheckIcon=None):
        """Fonction permettant de changer les icônes par défaut."""
        if CopyIcon: self.CopyIcon = CopyIcon
        if UndoIcon: self.UndoIcon = UndoIcon
        if RedoIcon: self.RedoIcon = RedoIcon
        if AllCheckIcon: self.AllCheckIcon = AllCheckIcon
        if AllPatriallyCheckIcon: self.AllPatriallyCheckIcon = AllPatriallyCheckIcon
        if AllUncheckIcon: self.AllUncheckIcon = AllUncheckIcon


    #========================================================================
    def setTristateMode(self, TristateMode):
        """Fonction permettant d'activer ou non le mode 3états des cases à cocher."""
        self.TristateMode = TristateMode

        for i in range(self.model().rowCount()):
            if self.model().item(i) is None: continue

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

        # Création et ajout de l'action d'annulation d'action (icône, nom, raccourci non fonctionnel) deep-history backup download-later
        CopyAction = QAction(self.CopyIcon, QCoreApplication.translate("QCheckComboBox", "Copy languages choosen"), self.contextMenu)
        CopyAction.triggered.connect(self.copyText)
        self.contextMenu.addAction(CopyAction)

        # Création et ajout de l'action d'annulation d'action
        UndoAction = QAction(self.UndoIcon, QCoreApplication.translate("QCheckComboBox", "Undo Action"), self.contextMenu)
        UndoAction.triggered.connect(lambda: self.setReUndoAction("Undo"))
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(UndoAction)

        # Création et ajout de l'action d'annulation d'action
        RedoAction = QAction(self.RedoIcon, QCoreApplication.translate("QCheckComboBox", "Redo Action"), self.contextMenu)
        RedoAction.triggered.connect(lambda: self.setReUndoAction("Redo"))
        self.contextMenu.addAction(RedoAction)

        # Création et ajout de l'action de cochage
        AllCheck = QAction(self.AllCheckIcon, QCoreApplication.translate("QCheckComboBox", "Check All Items"), self.contextMenu)
        AllCheck.triggered.connect(lambda: self.setStateAll(Qt.Checked))
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(AllCheck)

        # Création et ajout de l'action de semi cochage
        if self.TristateMode:
            AllSemiCheck = QAction(self.AllPatriallyCheckIcon, QCoreApplication.translate("QCheckComboBox", "Partially Check All Items"), self.contextMenu)
            AllSemiCheck.triggered.connect(lambda: self.setStateAll(Qt.PartiallyChecked))
            self.contextMenu.addAction(AllSemiCheck)

        # Création et ajout de l'action de décochage
        AllUncheck = QAction(self.AllUncheckIcon, QCoreApplication.translate("QCheckComboBox", "Uncheck All Items"), self.contextMenu)
        AllUncheck.triggered.connect(lambda: self.setStateAll(Qt.Unchecked))
        self.contextMenu.addAction(AllUncheck)


    #========================================================================
    def dataItemChanged(self, Item):
        """Fonction appelée lors d'une modification d'une case à cocher.
        Elle ne travaille que si la case a été modifiée via la touche espace."""

        # Si la case a été cochée via la touche espace
        if not self.spaceKeyBlock:
            # Infos
            State = Item.checkState()
            Index = self.model().indexFromItem(Item).row()

            # Mise à jour de l'historique
            self.updateHistoryActions([State, Index])

            # Mise à jour du texte du QLineEdit
            self.updateText()


    #========================================================================
    def resizeEvent(self, event):
        # Recompute text to elide as needed
        self.updateText()
        super().resizeEvent(event)


    #========================================================================
    def entryKeyUsed(self, Index):
        """Fonction de prise en compte de la validation d'un choix avec la touche entrée."""
        # Nouvel état à donner à la case à cocher
        State = self.newCheckState(self.model().item(Index).checkState())

        # Pour empêcher de changer l'icône
        if self.TitleExists:
            self.setCurrentIndex(0)

        # Mise à jour de l'item
        self.setStateItem(State, Index)


    #========================================================================
    def eventFilter(self, object, event):
        ### Si l'objet concerné est la combobox
        if object == self:
            # Si on utilise les touches des flèches pour naviguer, ça inverse l'état des cases
            # 1 clic sur la combobox, un 2e pour fermer la fenêtre puis utilisation des flèches pour une navigation invisible
            if event.type() == QEvent.KeyPress:
                # Bloque l'événement
                return True

            # Si c'est un clic droit sur la petite flèche, on affiche un menu modifié
            elif event.type() == QEvent.ContextMenu:
                # Affichage du menu là où se trouve la souris
                if PySideVersion == 6:
                    # PySide6
                    self.contextMenu.exec(QCursor.pos())

                else:
                    # PySide2
                    self.contextMenu.exec_(QCursor.pos())


                # Bloque l'événement
                return True


        ### Si l'objet concerné est le lineEdit
        elif object == self.lineEdit():
            # Si l'événement est le relâchement d'un clic (event.button() pour savoir lequel)
            if event.type() == QEvent.MouseButtonRelease:
                # Si la popup est visible, on la case sinon on l'affiche
                if self.closeOnLineEditClick: self.hidePopup()
                else: self.showPopup()

                # Bloque l'événement
                return True

            # Si c'est un clic droit, on affiche un menu modifié
            elif event.type() == QEvent.ContextMenu:
                # Affichage du menu là où se trouve la souris
                if PySideVersion == 6:
                    # PySide6
                    self.contextMenu.exec(QCursor.pos())

                else:
                    # PySide2
                    self.contextMenu.exec_(QCursor.pos())

                # Bloque l'événement
                return True


        ### Si l'objet concerné est le viewport
        elif object == self.view().viewport():
            # Si l'événement est le relâchement d'un clic (event.button() pour savoir lequel)
            if event.type() == QEvent.MouseButtonRelease:
                # Récupération de la case à cocher concernée
                Index = self.view().indexAt(event.pos())
                Row = Index.row()
                Item = self.model().item(Row)

                # Bloque les actions de la 1ere ligne s'il y a un titre
                if Row == 0 and self.TitleExists:
                    return True

                # Nouvel état à donner à la case à cocher
                State = self.newCheckState(Item.checkState())

                # Mise à jour de l'item
                self.setStateItem(State, Row)

                # Bloque l'événement
                return True


        ### Autorise l'événement
        return False


    #========================================================================
    def showPopup(self):
        super().showPopup()

        # Variable permettant à l’évènement de savoir s'il doit afficher ou cacher la popup
        self.closeOnLineEditClick = True


    #========================================================================
    def hidePopup(self):
        super().hidePopup()

        # Permet d'éviter la réouverture immédiate lors d'un clic sur le lineEdit
        self.startTimer(100)

        # Met à jour le texte visible du lineEdit
        self.updateText()


    #========================================================================
    def timerEvent(self, event):
        # Après le timeout, kill le timer, et réactive le clic sur le lineEdit
        self.killTimer(event.timerId())
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
    def addItem(self, text, data=None, state=None, icon=None):
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
        if data is None: data = text
        item.setData(data, Qt.UserRole)

        # Si utilisation d'une icône valide, plante avec PySide2 et PyQt5
        if PySideVersion == 6 and icon is not None and not icon.isNull(): item.setIcon(icon)

        # Si l'état de la case à cocher est précisée
        if state is not None: item.setCheckState(state)

        # Ajout de l'item
        self.model().appendRow(item)


    #========================================================================
    def addItems(self, Items):
        """Fonction de chargement d'item depuis une liste de dictionnaire.
        Les items sont de type : {text, data, state, icon}"""
        # Traite les dictionnaires un à un
        for Item in Items:
            # Si ni data ni texte, on le saute
            if "data" not in Item.keys() and "text" not in Item.keys(): continue

            # Si une donnée est manquante, on met une valeur de base
            if "text" not in Item.keys(): Item["text"] = Item["data"]
            if "data" not in Item.keys(): Item["data"] = None
            if "state" not in Item.keys(): Item["state"] = None
            if "icon" not in Item.keys(): Item["icon"] = None

            # Création de la ligne
            self.addItem(Item["text"], Item["data"], Item["state"], Item["icon"])


    #========================================================================
    def setStateItem(self, State, Indexes):
        """Fonction de modification de l'état de la case à cocher.
        Cette fonction est appelée par les fonctions de modifications
        de l'état des cases à cocher mais aussi lors du clic sur une case."""

        # Blocage de l'utilisation de la touche espace
        self.spaceKeyBlock = True

        # Si Indexes n'est pas une liste, on la change
        if not isinstance(Indexes, list): Indexes = [Indexes]

        # Permet de regrouper les actions quand elles ont lieu en même temps
        History = []

        for Index in Indexes:
            # Ne met à jour l'item que si besoin et pas la barre de titre
            if self.model().item(Index).checkState() != State and self.model().item(Index).data(Qt.UserRole):
                # Ajoute sa data à la liste
                self.model().item(Index).setCheckState(State)

                History.append([Index, State])

        # Gestion de la variable de l'historique
        if History: self.updateHistoryActions(History)

        # Mise à jour du texte de la QLineEdit
        self.updateText()

        # Déblocage de l'utilisation de la touche espace
        self.spaceKeyBlock = False


    #========================================================================
    def setStateItems(self, State, Items):
        """Fonction de modification de l'état de la case à cocher en se basant sur sa data."""
        Indexes = []

        # Ajoute les indexes des cases correspondantes
        for Item in range(self.model().rowCount()):
            if self.model().item(Item).data(Qt.UserRole) in Items:
                Indexes.append(Item)

        # Traite les cases retournées
        if Indexes: self.setStateItem(State, Indexes)


    #========================================================================
    def setStateAll(self, State):
        """Fonction de modification de l'état de la case à cocher de tous les items."""
        Indexes = []

        # Traite tous les items un à un
        for Item in range(self.model().rowCount()): Indexes.append(Item)

        # Traite les cases retournées
        if Indexes: self.setStateItem(State, Indexes)


    #========================================================================
    def setTitle(self, Text, Icon):
        """Fonction créant un item en début de liste afin d'utiliser son icône dans le QLineEdit."""
        self.TitleExists = True

        FirstItem = QStandardItem()
        FirstItem.setText(Text)
        FirstItem.setFlags(Qt.NoItemFlags)
        FirstItem.setData("", Qt.UserRole)
        FirstItem.setTextAlignment(Qt.AlignHCenter)
        FirstItem.setIcon(Icon)

        # S'il y a déjà des lignes, on les récupérer, les supprime et les réinjecte après
        Items = self.model().findItems(".*", Qt.MatchRegularExpression)

        # Nettoyage
        if Items: self.model().clear()

        # Ajout de l'item, l'insert ne suffit pas pour reprendre l'icône
        self.model().appendRow(FirstItem)

        # Remise en place des lignes
        if Items:
            for Item in Items:
                # Ne reprend pas le titre
                if Item.data(Qt.UserRole):
                    self.model().appendRow(Item)


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


    #========================================================================
    def setReUndoAction(self, Action):
        """Fonction de retour en arrière ou en avant dans les actions."""
        # Blocage de l'utilisation de la touche espace
        self.spaceKeyBlock = True

        ### Nouvel index
        if Action == "Undo":
            # Recule dans la liste dans l'historique des actions
            if self.historyLastAction == "Undo": self.historyIndex -= 1

            if self.historyIndex * -1 > len(self.historyActions):
                self.historyIndex = len(self.historyActions) * -1

        elif Action == "Redo":
            # Avance dans la liste dans l'historique des actions
            if self.historyLastAction == "Redo": self.historyIndex += 1
            if self.historyIndex > -1: self.historyIndex = -1


        ### Gestion par groupe d'actions
        for Index, State in self.historyActions[self.historyIndex]:
            # Inversion de l'action
            if Action == "Undo":
                State = Qt.Unchecked if State == Qt.Checked else Qt.Checked

            # Lancement de l'action
            self.model().item(Index).setCheckState(State)


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
            if self.model().item(i) is None: continue

            # Ne traite que les cases cochées
            if self.model().item(i).checkState() == Qt.Checked:
                # Ajoute sa data à la liste
                CheckOK.append(self.model().item(i).data(Qt.UserRole))

            elif self.model().item(i).checkState() == Qt.PartiallyChecked:
                # Ajoute sa data à la liste
                if self.model().item(i).data(Qt.UserRole):
                    CheckOK.append('[' + self.model().item(i).data(Qt.UserRole) + ']')

                else:
                    CheckOK.append('[' + self.model().item(i).text() + ']')

        # Envoi de la liste des cases cochées
        return CheckOK

