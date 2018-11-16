# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui.resources\ui_DownloadDialog.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DialogDownload(object):
    def setupUi(self, DialogDownload):
        DialogDownload.setObjectName("DialogDownload")
        DialogDownload.resize(405, 236)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/imgBase/images/istac_c.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        DialogDownload.setWindowIcon(icon)
        self.labelDownloading = QtWidgets.QLabel(DialogDownload)
        self.labelDownloading.setGeometry(QtCore.QRect(20, 130, 321, 16))
        self.labelDownloading.setObjectName("labelDownloading")
        self.pbDownload = QtWidgets.QProgressBar(DialogDownload)
        self.pbDownload.setGeometry(QtCore.QRect(20, 150, 361, 23))
        self.pbDownload.setInputMethodHints(QtCore.Qt.ImhNone)
        self.pbDownload.setProperty("value", 0)
        self.pbDownload.setTextVisible(True)
        self.pbDownload.setInvertedAppearance(False)
        self.pbDownload.setObjectName("pbDownload")
        self.labelTitle = QtWidgets.QLabel(DialogDownload)
        self.labelTitle.setGeometry(QtCore.QRect(20, 0, 371, 61))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelTitle.sizePolicy().hasHeightForWidth())
        self.labelTitle.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.labelTitle.setFont(font)
        self.labelTitle.setAutoFillBackground(False)
        self.labelTitle.setTextFormat(QtCore.Qt.AutoText)
        self.labelTitle.setWordWrap(True)
        self.labelTitle.setObjectName("labelTitle")
        self.labelDescription = QtWidgets.QLabel(DialogDownload)
        self.labelDescription.setGeometry(QtCore.QRect(20, 60, 351, 41))
        self.labelDescription.setWordWrap(True)
        self.labelDescription.setObjectName("labelDescription")
        self.button = QtWidgets.QPushButton(DialogDownload)
        self.button.setGeometry(QtCore.QRect(20, 200, 361, 23))
        self.button.setObjectName("button")

        self.retranslateUi(DialogDownload)
        self.button.clicked['bool'].connect(DialogDownload.btn_continue)
        QtCore.QMetaObject.connectSlotsByName(DialogDownload)

    def retranslateUi(self, DialogDownload):
        _translate = QtCore.QCoreApplication.translate
        DialogDownload.setWindowTitle(_translate("DialogDownload", "Comprobar actualizaciones"))
        self.labelDownloading.setText(_translate("DialogDownload", "Actualizando cartografías ..."))
        self.labelTitle.setText(_translate("DialogDownload", "Existen nuevas cartografías disponibles que deben de ser actualizadas antes de ejecutar el plugin"))
        self.labelDescription.setText(_translate("DialogDownload", "Este proceso sólo se ejecuta la primera vez que inicias el plugin o cuando se actualizan datos cartográficos en la API"))
        self.button.setText(_translate("DialogDownload", "Actualizar"))

from istacqgis.gui.generated import resources_rc
