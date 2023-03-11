#!/usr/bin/python3
# -*- coding: utf-8 -*-


################################
## Importation des modules Qt ##
################################
from ModulesQt import *


#############################################################################
class QScrollAreaCustom(QScrollArea):
    """Sous classement d'un QScrollAreaCustom pour y modifier capturer la molette de la souris."""

    ### Création du signal de changement de taille qui sera capté par les QScrollAreaCustom
    signalButtonsResize = Signal(int)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, Parent=None):
        super().__init__(Parent)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def wheelEvent(self, Event):
        # Si le combo ctrl + molette est utilisé
        if Event.modifiers() == Qt.ControlModifier and Event.angleDelta().y():
            # Si la molette monte, on ajoute +10px à la taille des boutons
            if Event.angleDelta().y() > 0:
                self.signalButtonsResize.emit(10)

            # Si la molette monte, on diminue de 10px la taille des boutons
            else:
                self.signalButtonsResize.emit(-10)

        # Si le combo shift + molette est utilisé
        elif Event.modifiers() == Qt.ShiftModifier and Event.angleDelta().y():
            ScrollBar = self.verticalScrollBar()

            # Si la molette monte, on monte tout en haut
            if Event.angleDelta().y() > 0:
                ScrollBar.setValue(ScrollBar.minimum())

            # Si la molette monte, on descend tout en bas
            else:
                ScrollBar.setValue(ScrollBar.maximum())

        # Si pas de combo ctrl + molette, on laisse passer l'événement
        else:
            super().wheelEvent(Event)

