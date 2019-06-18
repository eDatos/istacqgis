# coding: utf-8

from PyQt5.QtWidgets import QDialog
from qgis.gui import QgsManageConnectionsDialog
import time

def connect_wms(self):
    
    file_path = self.plugin_dir + "/data/export.xml"
        
    manage_connections_dialog_import = QgsManageConnectionsDialog(
        mode = QgsManageConnectionsDialog.Import,
        type = QgsManageConnectionsDialog.WMS,
        fileName = file_path
    )
    
    manage_connections_dialog_import.clearSelection()
    manage_connections_dialog_import.selectAll()
    manage_connections_dialog_import.doExportImport()
    manage_connections_dialog_import.selectionChanged()
    
    # Update GUI
    self.iface.reloadConnections()
    