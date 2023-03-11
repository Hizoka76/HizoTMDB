#!/usr/bin/python3
# -*- coding: utf-8 -*-


################################
## Importation des modules Qt ##
################################
from ModulesQt import *


#############################################################################
class QSliderCustom(QSlider):
    """Slider personnalisé avec gestion de nouveaux signaux et des touches Maj, Ctrl et Alt."""
    ### Création des signaux maison
    # Envoi de la valeur comme valueChanged mais aussi lors du déplacement de la souris,
    # bien mieux que mouseMoved.
    continueValueChanged = Signal(int)

    # Lors de l'entrée dans le widget sans clic actif
    sliderEntered = Signal()

    # Lors de la sortie du widget sans clic actif
    sliderLeaved = Signal()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, parent=None):
        super(QSliderCustom, self).__init__(parent)

        # Surveillance de la souris pour mouseMoveEvent
        self.setMouseTracking(True)

        # Variable indiquant qu'un bouton est actuellement pressé
        self.ButtonCurrentlyPressed = False

        # Variable indiquant si le survol du widget est actuel
        self.HoveringWidget = False

        # Connexion des signaux par défaut vers les fonctions permettant les nouveaux signaux
        self.valueChanged.connect(self.change)
        self.sliderPressed.connect(self.pressButon)
        self.sliderReleased.connect(self.releaseButton)

        # Valeurs des différents incréments de la souris
        self.Steps = { "StepPage": 5, "StepShift": 10, "StepControl": 20, "StepAlt": 50, "Step": 2 }


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setSteps(self, Steps):
        """Fonction de mise à jour des valeurs d'incrémentations. Steps doit être un dictionnaire."""
        for Key, Value in Steps.items():
            self.Steps[Key] = Value


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def isHover(self):
        """Fonction retournant si le widget est actuellement survolé."""
        return self.HoveringWidget


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def pressButon(self):
        """Fonction activant la variable bouton actuellement pressé."""
        self.ButtonCurrentlyPressed = True


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def releaseButton(self):
        """Fonction désactivant la variable bouton actuellement pressé."""
        self.ButtonCurrentlyPressed = False


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def enterEvent(self, Event):
        """Fonction activant la variable survol du widget."""
        # Si le bouton n'est pas actuellement pressé
        if not self.ButtonCurrentlyPressed:
            # Émission du signal entrée
            self.sliderEntered.emit()
            self.HoveringWidget = True

        super().enterEvent(Event)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def leaveEvent(self, Event):
        """Fonction désactivant la variable survol du widget."""
        # Si le bouton n'est pas actuellement pressé
        if not self.ButtonCurrentlyPressed:
            # Émission du signal sortie
            self.sliderLeaved.emit()
            self.HoveringWidget = False

        super().leaveEvent(Event)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def mouseMoveEvent(self, Event):
        """Fonction appelée lors du déplacement de la souris dans le widget ou hors si bouton pressé."""
        # Ne travailler que si le bouton est actuellement pressé
        if self.ButtonCurrentlyPressed:
            # Calcul de la valeur actuel en fonction de son emplacement dans le widget avec prise en compte de l'inversion d'apparence
            if self.invertedAppearance():
                Value = int(self.maximum() - ((self.maximum() - self.minimum()) * Event.x()) / self.width())

            else:
                Value = int(self.minimum() + ((self.maximum() - self.minimum()) * Event.x()) / self.width())

            # La valeur ne doit pas être inférieure à la minimale
            if Value < self.minimum():
                Value = self.minimum()

            # La valeur ne doit pas être supérieure à la maximale
            elif Value > self.maximum():
                Value = self.maximum()

            # Émission du signal de la nouvelle valeur
            self.continueValueChanged.emit(Value)

        super().mouseMoveEvent(Event)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def keyPressEvent(self, Event):
        """Surveillance des touches spéciales pour gérer les incréments spécifiques."""
        # Blocage si le bouton est pressé, peu probable...
        if self.ButtonCurrentlyPressed:
            return

        # Touche pressée
        Key = Event.key()

        # Liste des touches concernées
        if Key in [Qt.Key_Home, Qt.Key_End, Qt.Key_Left, Qt.Key_Up, Qt.Key_Right, Qt.Key_Down, Qt.Key_PageUp, Qt.Key_PageDown, Qt.Key_Plus, Qt.Key_Minus]:
            # Valeur actuelle
            Value = self.value()

            # Dictionnaire simplifiant le code d'après, évitant de multiple IF ELSE
            # 1er True / False : invertedControls
            # 2e True False : invertedAppearance
            AllValues = {
                True: {
                    "Min": self.maximum(),
                    "Max": self.minimum(),
                    "Plus": { True: 1, False: -1 },
                    "Minus": { True: -1, False: 1 },
                    "PageUp": self.Steps['StepPage'] * -1,
                    "PageDown": self.Steps['StepPage']
                },
                False: {
                    "Min": self.minimum(),
                    "Max": self.maximum(),
                    "Plus": { True: -1, False: 1 },
                    "Minus": { True: 1, False: -1 },
                    "PageUp": self.Steps['StepPage'],
                    "PageDown": self.Steps['StepPage'] * -1
                }
            }

            # Simplification du nom pour la suite
            Values = AllValues[self.invertedControls()]

            # Touche début
            if Key == Qt.Key_Home:
                self.setValue(Values["Min"])

            # Touche fin
            elif Key == Qt.Key_End:
                self.setValue(Values["Max"])

            # Touche flèche droite, uniquement si le Slider est horizontal
            elif Key == Qt.Key_Right and self.orientation() == Qt.Horizontal:
                self.stepBy(Values['Plus'][self.invertedAppearance()])

            # Touche flèche haut, uniquement si le Slider est vertical
            elif Key == Qt.Key_Up and self.orientation() == Qt.Vertical:
                self.stepBy(Values['Plus'][self.invertedAppearance()])

            # Touche plus
            elif Key == Qt.Key_Plus:
                self.stepBy(Values['Plus'][False])

            # Touche flèche gauche si le Slider est horizontal
            elif Key == Qt.Key_Left and self.orientation() == Qt.Horizontal:
                self.stepBy(Values['Minus'][self.invertedAppearance()])

            # Touche flèche bas si le Slider est vertical
            elif Key == Qt.Key_Down and self.orientation() == Qt.Vertical:
                self.stepBy(Values['Minus'][self.invertedAppearance()])

            # Touche moins
            elif Key == Qt.Key_Minus:
                self.stepBy(Values['Minus'][False])

            # Touche page précédente
            elif Key == Qt.Key_PageUp:
                self.stepBy(Values['PageUp'])

            # Touche page suivante
            elif Key == Qt.Key_PageDown:
                self.stepBy(Values['PageDown'])

            return

        # Ne pas utiliser si on bloque toutes les autres actions ?!
        # super().keyPressEvent(Event)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def wheelEvent(self, Event):
        """Surveille l'utilisation de la molette de la souris pour gérer les incréments."""
        # Blocage si le bouton est pressé, peu probable...
        if self.ButtonCurrentlyPressed:
            return

        # Dictionnaire simplifiant le code d'après, évitant de multiple IF ELSE
        # 1er True / False : invertedControls
        AllValues = {
            True: { "Plus": -1, "Minus": 1 },
            False: { "Plus": 1, "Minus": -1 }
        }

        # Si la molette va vers le haut
        if Event.angleDelta().y() > 0 or Event.angleDelta().x() > 0 :
            self.stepBy(AllValues[self.invertedControls()]['Plus'])

        # Si la molette va vers le bas
        else:
            self.stepBy(AllValues[self.invertedControls()]['Minus'])

        # Ne pas utiliser si on bloque toutes les autres actions ?!
        # super().wheelEvent(Event)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def stepBy(self, Step):
        """Bloque l'ajout via les boutons +/- pour personnaliser l'incrément."""
        # Valeur actuelle
        Value = self.value()

        # Recherche une touche pressée
        KeyPressed = QGuiApplication.queryKeyboardModifiers()

        # Dictionnaire simplifiant les commandes suivantes en évitant des IF ELIF ELSE
        Values = {
            Qt.ShiftModifier: self.Steps['StepShift'],
            Qt.ControlModifier: self.Steps['StepControl'],
            Qt.AltModifier: self.Steps['StepAlt'],
            Qt.NoModifier: self.Steps['Step']
        }

        # Incrément négatif plus ou moins important en fonction de la touche pressée simultanément
        if Step < 0:
            self.setValue(Value - Values[KeyPressed])

        # Incrément positif plus ou moins important en fonction de la touche pressée simultanément
        else:
            self.setValue(Value + Values[KeyPressed])


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def change(self, value):
        """Lorsque la valeur a changé hors déplacement à la souris."""
        # Ne rien faire faire si le bouton est enfoncé
        if self.ButtonCurrentlyPressed:
            return

        # Émission du nouveau signal imitant valueChanged
        self.continueValueChanged.emit(value)
