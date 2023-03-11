#!/usr/bin/python3
# -*- coding: utf-8 -*-


################################
## Importation des modules Qt ##
################################
from ModulesQt import *


#############################################################################
class QTabWidgetCustom(QTabWidget):
    """Création d'un QTabWidget personnalisé permettant l'ajout d'un widget avec auto hide."""
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setCornerWidget(self, *args, **kwargs):
        """Surclassement de la fonction avec auto hide du widget ajouté."""
        super().setCornerWidget(*args, **kwargs)

        # Simulation de la suppression d'un onglet imaginaire
        self.tabRemoved(999)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def tabRemoved(self, Index):
        """Cache le widget s'il n'y a plus d'onglet. Appelé après la suppression d'un onglet."""
        # S'il y a des onglets
        if not self.count():
            # Boucle chez les 4 emplacements possibles des widgets
            for Corner in [Qt.TopLeftCorner, Qt.TopRightCorner, Qt.BottomLeftCorner, Qt.BottomRightCorner]:
                # Si le widget existe, on le cache
                if self.cornerWidget(Corner):
                    self.cornerWidget(Corner).setVisible(False)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def tabInserted(self, Index):
        """Affiche le widget. Appelé après la création d'un onglet."""
        # Boucle chez les 4 emplacements possibles des widgets
        for Corner in [Qt.TopLeftCorner, Qt.TopRightCorner, Qt.BottomLeftCorner, Qt.BottomRightCorner]:
            # Si le widget existe, on l'affiche
            if self.cornerWidget(Corner):
                self.cornerWidget(Corner).setVisible(True)
