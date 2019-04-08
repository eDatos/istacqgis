# -*- coding: utf-8 -*-
"""
/***************************************************************************
 **Nombre del plugin
                                 A QGIS plugin
 **Descripcion
                             -------------------
        begin                : **Fecha
        copyright            : **COPYRIGHT
        email                : **Mail de contacto
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 #   any later version.                                                    *
 *                                                                         *
 ***************************************************************************/
"""
import os.path
from qgis.core import *

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QAction

from istacqgis.BaseDialog import BaseDialog
import istacqgis.gui.generated.resources_rc

try:
    import sys
    from pydevd import *
except:
    None

class Base:
    
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))
        self.url_to_check = "http://www.gobiernodecanarias.org/istac/QGIS/"
        self.url_to_download = "http://www.gobiernodecanarias.org/istac/descargas/QGIS/data/"


    def initGui(self):
        self.action = QAction(QIcon(":/imgBase/images/istac_c.png"), u"Instituto Canario de Estadística (ISTAC)", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&Instituto Canario de Estadística (ISTAC)", self.action)


    def unload(self):
        self.iface.removePluginMenu(u"&Instituto Canario de Estadística (ISTAC)", self.action)
        self.iface.removeToolBarIcon(self.action)
 

    def run(self):
        
        # Dialog
        self.dlg_base = BaseDialog(self.iface)
        
        # Base Dialog
        self.dlg_base.setWindowFlags(Qt.WindowSystemMenuHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        code = self.dlg_base.exec_()
        