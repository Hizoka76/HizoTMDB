#!/usr/bin/python3
# -*- coding: utf-8 -*-

################################
## Importation des modules Qt ##
################################
# Réaliser des imports complets est plus rapide, plus simple et compatible pour tous les modules.

# Version de Qt
QtVersion = 6

# PySide 6
try:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *

except:
    # PyQt6
    try:
        from PyQt6.QtCore import *
        from PyQt6.QtGui import *
        from PyQt6.QtWidgets import *

        # Ajout du lien pyqtSignal => Signal
        globals()["Signal"] = pyqtSignal

    except:
        QtVersion = 2

        # PyQt5
        try:
            from PyQt5.QtCore import *
            from PyQt5.QtGui import *
            from PyQt5.QtWidgets import *

            # Ajout du lien pyqtSignal => Signal
            globals()["Signal"] = pyqtSignal

        except:
            # PySide2
            try:
                from PySide2.QtCore import *
                from PySide2.QtGui import *
                from PySide2.QtWidgets import *

            except:
                raise ImportError("Impossible to load Qt.")
                exit()

# Ajout du lien QCoreApplication.translate => translate pour plus de simplicité
globals()["translate"] = QCoreApplication.translate
