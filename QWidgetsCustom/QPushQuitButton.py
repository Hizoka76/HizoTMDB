#!/usr/bin/python3
# -*- coding: utf-8 -*-


################################
## Importation des modules Qt ##
################################
from ModulesQt import *


##############################
## QPushButton personnalisé ##
##############################
class QPushQuitButton(QPushButton):
    """QPushButton prenant en compte un clic droit et renvoyant un signal."""
    rebootSignal = Signal()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, Parent=None):
        super().__init__(Parent)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def mouseReleaseEvent(self, event):
        """Fonction de récup des clics souris utilisées."""
        # Envoi du signal si c'est un clic droit qui a été relâché
        if event.button() == Qt.RightButton:
            self.rebootSignal.emit()

        # Acceptation de l'événement
        super().mouseReleaseEvent(event)
