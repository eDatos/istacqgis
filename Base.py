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

from istacqgis.controllers import cache
from istacqgis.BaseDialog import BaseDialog
from istacqgis.DownloadDialog import DownloadDialog
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
        self.action = QAction(QIcon(":/imgBase/images/istac_c.png"), u"ISTAC Plugin", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&Instituto Canario de Estadística (ISTAC)", self.action)


    def unload(self):
        self.iface.removePluginMenu(u"&Instituto Canario de Estadística (ISTAC)", self.action)
        self.iface.removeToolBarIcon(self.action)
 

    def run(self):
        
        # Dialogs
        self.dlg_download = DownloadDialog(self.iface)
        self.dlg_base = BaseDialog(self.iface)
        
        # Check cache in /data folder
        updates_available = cache.cache_is_empty(self)
        
        # Compare files in URL and /data folder
        files_in_url = cache.get_cache_files_from_url(self, self.url_to_check)
        files_in_cache = cache.get_all_files_in_directory(self)
        need_to_update = False # flag
        
        for file in files_in_url:
            if file not in files_in_cache:
                need_to_update = True
        
        if updates_available or need_to_update:
            # Updates
            self.dlg_download.setWindowFlags(Qt.WindowSystemMenuHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            code = self.dlg_download.exec_()
            # If code is 0, dlg_download window has been closed by the user
            # If code is 1, dlg_download window has been closed pressing Continue button
            # Base Dialog
            self.dlg_base.setWindowFlags(Qt.WindowSystemMenuHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            self.dlg_base.exec_()
        else:
            # Base Dialog
            self.dlg_base.setWindowFlags(Qt.WindowSystemMenuHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
            code = self.dlg_base.exec_()
        