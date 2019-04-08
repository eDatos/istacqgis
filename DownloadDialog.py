# -*- coding: utf-8 -*-
"""
/***************************************************************************
 **Nombre del plugin
                                 ISTAC plugin
 **Descripcion
                             -------------------
        begin                : **01/08/2018
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
from qgis.core import *
from qgis.gui import *

from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from istacqgis.gui.generated.ui_download_dialog import Ui_DialogDownload
from istacqgis.controllers import cache
import os.path

try:
    import sys
    from pydevd import *
except:
    None
 
class DownloadDialog(QDialog, Ui_DialogDownload):
    
    def __init__(self, iface, geographical):
        QDialog.__init__(self)
        self.geographical = geographical
        self.setupUi(self)
        self.iface = iface
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))
        # VARIABLES 
        self.url_to_check = "http://www.gobiernodecanarias.org/istac/QGIS/"
        self.url_to_download = "http://www.gobiernodecanarias.org/istac/descargas/QGIS/data/"
        self.buttonText = ''
        self.change_label_text("Presione el botón descargar ...")
        # INITIAL ACTIONS
        self.change_btn_text("Descargar")
        self.labelTitle.setText("Es necesario descargar la cartografía " + self.geographical)
        self.labelTitle.repaint()
        
    def download(self):
        
        # Compare files in URL and /data folder
        files_in_url = cache.get_cache_files_from_url(self, self.url_to_check)
        files_in_cache = cache.get_all_files_in_directory(self)
        file = self.geographical
        
        self.setProgress(1)
        if file not in files_in_cache:
            cache.download_file_from_url(self, self.url_to_download, file)
            self.setProgress(50)
        self.setProgress(100)
        
    def setProgress(self, progress):
        self.pbDownload.setValue(progress)
    
    def btn_continue(self, clicked):
        if self.buttonText == "Descargar":
            self.change_label_text("Actualizando cartografías ...")
            self.download()
            self.change_label_text("Actualización finalizada.")
            self.change_btn_text("Continuar")
            self.button.setStyleSheet('QPushButton {background-color: #A3C1DA; color: red;}')
        else:
            self.accept()
        
    def change_btn_text(self, text):
        self.button.setText(text)
        self.buttonText = text
    
    def change_label_text(self, text):
        self.labelDownloading.setText(text)
        self.labelDownloading.repaint()
