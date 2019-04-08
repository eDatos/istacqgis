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

from istacqgis.gui.generated.ui_dialog import Ui_BaseDialog
from istacqgis.controllers.istacpy import istacpy
from istacqgis.controllers import data
from istacqgis.controllers import polygons
from istacqgis.controllers import cache
from istacqgis.controllers import resources

from operator import itemgetter # to sort a dictionary
import os.path
import time

try:
    import sys
    from pydevd import *
except:
    None
 
class BaseDialog(QDialog, Ui_BaseDialog):
    
    def __init__(self, iface):
        QDialog.__init__(self)
        self.setupUi(self)
        self.iface = iface
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))
        # VARIABLES
        self.error_flag = False
        self.subject = ""
        self.indicator = ""
        self.buttonText = "Obtener datos"
        self.geographic_list = []
        self.selected_section = ""
        self.selected_district = ""
        # CHECKBOX OPTIONS
        self.measures_as_columns = False
        self.date = False
        self.geographical_and_temporal_columns = False
        self.geographical_and_temporal_labels = False
        self.measures_units = False
        self.langs = False
        self.initialCbCheckin()
        # INITIAL ACTIONS
        self.setCbSubjects()
        self.checkBoxLangs.setEnabled(False)
        self.enableProgress(enable=False)
        self.labelDistricts.setVisible(False)
        self.cbDistricts.setVisible(False)
        self.labelSections.setVisible(False)
        self.cbSections.setVisible(False)
        self.enable_options(True, geographical=False)
        self.listGeographical.clear()
    
    # SUBJECTS
    def setCbSubjects(self):
        subjects = istacpy.get_subjects()
        subject_title_es = {subject["id"]: subject["title"]["es"] for subject in subjects['items']}
        # Sort dictionary
        subject_title_es_sorted_list = sorted(subject_title_es.items(), key=itemgetter(0))
        subject_title_es_sorted_dict = dict(subject_title_es_sorted_list)
        self.cbSubjects.clear()
        for key, value in subject_title_es_sorted_dict.items():
            self.cbSubjects.addItem(value, key)
    
    def getCbSubjects(self, subject):
        self.setCbIndicators(subject)
    
    # INDICATORS
    def setCbIndicators(self, subject):
        
        # Get combobox key
        subjectText = subject.split(" ")[1]
        self.subject = subjectText
        
        # Set values
        query = "subjectCode EQ " + subject
        indicators = istacpy.get_indicators(q=query, limit=999)
        indicators_title_es = {indicator["id"]: indicator["title"]["es"] for indicator in indicators['items']}
         # Sort dictionary
        indicators_title_es_sorted_list = sorted(indicators_title_es.items(), key=itemgetter(0))
        indicators_title_es_sorted_dict = dict(indicators_title_es_sorted_list)
        self.cbIndicators.clear()
        for key, value in indicators_title_es_sorted_dict.items():
            self.cbIndicators.addItem(value, key)

    def getCbIndicators(self, text):
        
        # Get combobox key
        itemID = self.cbIndicators.findText(text)
        indicatorID = self.cbIndicators.itemData(itemID)
        self.indicator = indicatorID
        
        if not self.rbData.isChecked():
            self.setlistGeographical(indicator=self.indicator)
    
    # GEOGRAPHICAL GRANULARITY
    def setlistGeographical(self, indicator=None):
        if indicator is None:
            self.listGeographical.clear()
            self.listGeographical.addItems(polygons.getGeographicalGranularities(self))
            # Nota: en https://www3.gobiernodecanarias.org/istac/api/indicators/v1.0/geographicGranularities aun no existe la definición de:
            #     - LARGE_COUNTIES
            #     - SECTIONS
            #     - DISTRICTS
            
        else:
            self.listGeographical.clear()
            self.listGeographical.addItems(polygons.getGeographicalGranularities(self, indicator=indicator))
        
    def drawPolygons(self, geographical_granularity):
        
        # Get current path
        file_path = self.plugin_dir + "/data/"
        
        # Progress bar
        self.setProgress(1)
        time.sleep(0.1)
        self.setProgress(10)
        self.setProgress(20)
        self.setProgress(30)
        time.sleep(0.1)
        self.setProgress(40)
        self.setProgress(50)
        time.sleep(0.1)
        self.setProgress(75)
        
        # Layer declaration
        if geographical_granularity == "DISTRICTS":
            polygonLayer = QgsVectorLayer(file_path + geographical_granularity + "_" + str(self.selected_district) + ".geojson", geographical_granularity + "_" + str(self.selected_district), "ogr")
        elif geographical_granularity == "SECTIONS":
            polygonLayer = QgsVectorLayer(file_path + geographical_granularity + "_" + str(self.selected_section) + ".geojson", geographical_granularity + "_" + str(self.selected_section), "ogr")
        else:
            polygonLayer = QgsVectorLayer(file_path + geographical_granularity + ".geojson", geographical_granularity, "ogr")
        
        variable = QgsProject.instance().addMapLayer(polygonLayer)
        if not variable:
            self.error_flag = True
            if geographical_granularity == "DISTRICTS":
                self.iface.messageBar().pushMessage("Ooops!", "No data found in ISTAC API for " + str(geographical_granularity) + "_" + str(self.selected_district), level=Qgis.Warning, duration=10)
            elif geographical_granularity == "SECTIONS":
                self.iface.messageBar().pushMessage("Ooops!", "No data found in ISTAC API for " + str(geographical_granularity) + "_" + str(self.selected_section), level=Qgis.Warning, duration=10)
            else:
                self.iface.messageBar().pushMessage("Ooops!", "No data found in ISTAC API for " + str(geographical_granularity), level=Qgis.Warning, duration=10)
        else:
            self.error_flag = False
            # Edit layer attributes
            polygonLayer.startEditing()
            # Set encoding to UTF-8
            polygonLayer.setProviderEncoding(u'latin9')
            # Set layer metadata
            m = polygonLayer.metadata()
            
            if geographical_granularity == "DISTRICTS":
                file_path_metadata = str(geographical_granularity) + "_" + str(self.selected_district)
            elif geographical_granularity == "SECTIONS":
                file_path_metadata = str(geographical_granularity) + "_" + str(self.selected_section)
            else:
                file_path_metadata = str(geographical_granularity)
            geographical_granularity_title = file_path_metadata
            
            m = self.getLayerMetadata(
                    m,
                    polygonLayer,
                    is_indicator = False,
                    identifier = "https://www.gobiernodecanarias.org/istac/api/structural-resources/v1.0/variables/VR_TERRITORIO/variableelements",
                    parent_identifier = "https://www.gobiernodecanarias.org/istac/api/structural-resources/v1.0/variables/VR_TERRITORIO",
                    title = geographical_granularity_title,
                    type = "dataset",
                    lang = "es-ES",
                    abstract = None,
                    category = "boundaries",
                    file_path = file_path_metadata,
                    file_extension = "geojson"
                )
            polygonLayer.setMetadata(m)
            polygonLayer.commitChanges()
            self.setProgress(100)
    
    def drawDataLayer(self):
        
        # Progress bar
        self.setProgress(1)
        time.sleep(0.25)
        self.setProgress(10)
        time.sleep(0.25)
        self.setProgress(20)
        time.sleep(0.25)
        self.setProgress(30)
        time.sleep(0.25)
        self.setProgress(40)
        
        # Build CSV file to load
        data.writeIndicatorData(self, self.indicator)
        self.setProgress(50)
        
        # Get current path
        file_path = self.plugin_dir + "/data/"
        uri = "file:///" + file_path + resources.getIndicatorFileName(self, self.indicator) + ".csv?encoding=%s&delimiter=%s&crs=%s" % ("UTF-8",",","epsg:32628")
        
        # Layer
        dataLayer = QgsVectorLayer(uri, self.indicator, "delimitedtext")
        
        if not dataLayer.isValid():
            self.iface.messageBar().pushMessage("Ooops!", "Layer could not be loaded", level=Qgis.Warning, duration=10)
        
        # Edit layer attributes
        dataLayer.startEditing()
        # Set encoding to UTF-8
        dataLayer.setProviderEncoding(u'UTF-8')
        # Set layer metadata
        m = dataLayer.metadata()
        m = self.getLayerMetadata(
                m,
                dataLayer,
                is_indicator = True,
                identifier = "https://www3.gobiernodecanarias.org/istac/api/indicators/v1.0/indicators/" + self.indicator,
                parent_identifier = "https://www3.gobiernodecanarias.org/istac/api/indicators/v1.0/indicators/" + self.indicator + "/data",
                title = self.indicator,
                type = "dataset",
                lang = "es-ES",
                abstract = None,
                category = self.subject,
                file_path = resources.getIndicatorFileName(self, self.indicator),
                file_extension = "csv"
            )
        dataLayer.setMetadata(m)
        dataLayer.commitChanges()        
        self.setProgress(75)
        time.sleep(0.25)

        # Add layer
        QgsProject.instance().addMapLayer(dataLayer)
        
        self.setProgress(100)
    
    def enable_options(self, enable=True, geographical=True):
        if enable:
            self.cbSubjects.setEnabled(True)
            self.cbIndicators.setEnabled(True)
            self.checkBoxMeasures.setEnabled(True)
            self.checkBoxDate.setEnabled(True)
            self.checkBoxGranularities.setEnabled(True)
            self.checkBoxLabels.setEnabled(True)
            self.setCbMeasures(True)
            if self.geographical_and_temporal_labels:
                self.checkBoxLangs.setEnabled(True)
            else:
                self.checkBoxLangs.setEnabled(False)
        else:
            self.cbSubjects.setEnabled(False)
            self.cbIndicators.setEnabled(False)
            self.checkBoxMeasures.setEnabled(False)
            self.checkBoxDate.setEnabled(False)
            self.checkBoxGranularities.setEnabled(False)
            self.checkBoxLabels.setEnabled(False)
            self.checkBoxMeasuresUnit.setEnabled(False)
            self.checkBoxLangs.setEnabled(False)
                
        if geographical:
            self.listGeographical.setEnabled(True)
            self.cbDistricts.setEnabled(True)
            self.cbSections.setEnabled(True)
        else:
            self.listGeographical.setEnabled(False)
            self.cbDistricts.setEnabled(False)
            self.cbSections.setEnabled(False)
        
    def getRadioOptions(self, clicked):
        
        self.btnGetDataPolygons.setEnabled(True)
        # Sólo indicadores
        if self.rbData.isChecked():
            self.change_btn_text("Obtener datos")
            self.enable_options(True, geographical=False)
            self.listGeographical.clear()
        
        # Indicadores y su cartografía asociada
        if self.rbDataCarto.isChecked():
            self.btnGetDataPolygons.setEnabled(False)
            self.change_btn_text("Obtener datos y cartografía")
            self.enable_options(True, geographical=True)
            self.setlistGeographical(indicator=self.indicator)
            self.getSelectionGeographic()
        
        # Cartografía disponible por capas
        if self.rbCarto.isChecked():
            self.btnGetDataPolygons.setEnabled(False)
            self.change_btn_text("Obtener cartografía")
            self.enable_options(False, geographical=True)
            self.setlistGeographical(indicator=None)

    # Geographical granularity list
    def getSelectionGeographic(self):
        # Clear comboBox
        self.cbDistricts.clear()
        self.cbSections.clear()
        
        # Get geographic selected list
        self.geographic_list = [item.text() for item in self.listGeographical.selectedItems()]
        
        # Enable or disable button
        if len(self.geographic_list) == 0 and self.buttonText == "Obtener datos y cartografía":
            self.btnGetDataPolygons.setEnabled(False)
        elif len(self.geographic_list) == 0 and self.buttonText == "Obtener cartografía":
            self.btnGetDataPolygons.setEnabled(False)
        else:
            self.btnGetDataPolygons.setEnabled(True)
        
        # Checkboxes
        if (self.rbCarto.isChecked()):
            self.enable_options(False)
        else:
            if len(self.geographic_list) == 0:
                self.enable_options(True)
            else:
                self.enable_options(True)
        # Comboboxes DISTRICTS and SECTIONS
        if "DISTRICTS" in self.geographic_list:
            self.labelDistricts.setVisible(True)
            self.cbDistricts.setVisible(True)
            districts_list = polygons.get_cb_date_by_variableelement(self, "DISTRICTS")
            districts_list_dict = {districts["variableelement"]: districts["date"] for districts in districts_list}
            # Sort dictionary
            districts_list_dict_sorted_list = reversed(sorted(districts_list_dict.items(), key=itemgetter(0)))
            districts_list_dict_sorted_list = dict(districts_list_dict_sorted_list)
            for key, value in districts_list_dict_sorted_list.items():
                self.cbDistricts.addItem(value, key)
        else:
            self.labelDistricts.setVisible(False)
            self.cbDistricts.setVisible(False)
            self.cbDistricts.clear()
            
        if "SECTIONS" in self.geographic_list:
            self.labelSections.setVisible(True)
            self.cbSections.setVisible(True)
            sections_list = polygons.get_cb_date_by_variableelement(self, "SECTIONS")
            sections_list_dict = {sections["variableelement"]: sections["date"] for sections in sections_list}
            # Sort dictionary
            sections_list_dict_sorted_list = reversed(sorted(sections_list_dict.items(), key=itemgetter(0)))
            sections_list_dict_sorted_list = dict(sections_list_dict_sorted_list)
            for key, value in sections_list_dict_sorted_list.items():
                self.cbSections.addItem(value, key)
        else:
            self.labelSections.setVisible(False)
            self.cbSections.setVisible(False)
            self.cbSections.clear()
    
    def getCbSections(self, section):
        # Get combobox key
        itemID = self.cbSections.findText(section)
        section_id = self.cbSections.itemData(itemID)
        self.selected_section = section_id
        #print(section_id)
    
    def getCbDistricts(self, district):
        # Get combobox key
        itemID = self.cbDistricts.findText(district)
        district_id = self.cbDistricts.itemData(itemID)
        self.selected_district = district_id
        #print(district_id)
            
        
    # CHECKBOX OPTIONS
    # Check initial checkbox options
    def initialCbCheckin(self):
        self.setCbMeasures(True)
        self.setCbDates(True)
        self.setCbGeoTempColumns(True)
        self.setCbGeoTempLabels(True)
        self.setCbMeasuresUnits(True)
        self.setCbLangs(True)
        
    # Show measures as columns
    def setCbMeasures(self, clicked):
        if self.checkBoxMeasures.isChecked():
            self.measures_as_columns = True
            self.checkBoxMeasuresUnit.setEnabled(False)
            self.checkBoxMeasuresUnit.setChecked(False)
        else:
            self.measures_as_columns = False
            self.checkBoxMeasuresUnit.setEnabled(True)
    
    # Show date columns
    def setCbDates(self, clicked):
        if self.checkBoxDate.isChecked() is True:
            self.date = True
        else:
            self.date = False
    
    # Show geographical and temporal granularity columns
    def setCbGeoTempColumns(self, clicked):
        if self.checkBoxGranularities.isChecked():
            self.geographical_and_temporal_columns = True
        else:
            self.geographical_and_temporal_columns = False
            
    # Show geographical and temporal granularity labels
    def setCbGeoTempLabels(self, clicked):
        if self.checkBoxLabels.isChecked():
            self.geographical_and_temporal_labels = True
            self.checkBoxLangs.setEnabled(True)
        else:
            self.geographical_and_temporal_labels = False
            self.checkBoxLangs.setEnabled(False)
            self.checkBoxLangs.setChecked(False)
            self.langs = False
        
    # Show measures units
    def setCbMeasuresUnits(self, clicked):
        if self.checkBoxMeasuresUnit.isChecked():
            self.measures_units = True
        else:
            self.measures_units = False
            
    # Show langs
    def setCbLangs(self, clicked):
        if self.checkBoxLangs.isChecked():
            self.langs = True
        else:
            self.langs = False

    # BUTTONS
    # Change button (btnGetDataPolygons) text
    def change_btn_text(self, text):
        self.buttonText = text
        self.btnGetDataPolygons.setText(self.buttonText)
    
    # Button get data
    def getBtnAction(self, clicked):
        
        # If code is 0, windows has been closed by user
        code = 1
        
        # POLYGONS
        if self.buttonText == "Obtener cartografía":
            
            for geographical_granularity in self.geographic_list:
                
                if geographical_granularity == "DISTRICTS":
                    code = cache.download_carto(self, geographical_granularity, self.selected_district)
                elif geographical_granularity == "SECTIONS":
                    code = cache.download_carto(self, geographical_granularity, self.selected_section)
                else:
                    code = cache.download_carto(self, geographical_granularity)
                    
                if code is not 0:
                    # Enable progress bar
                    self.enableProgress(enable=True)
                    self.labelLoading.setText("Cargando cartografía " + geographical_granularity + " ...")
                    self.labelLoading.repaint()
                    self.setProgress(1) 
                    self.drawPolygons(geographical_granularity)
                    self.setProgress(100)
            
        # DATA
        elif self.buttonText == "Obtener datos":
            # Enable progress bar
            self.enableProgress(enable=True)
            self.labelLoading.setText("Cargando datos del indicador " + self.indicator + " ...")
            self.labelLoading.repaint()
            self.setProgress(1)
            self.drawDataLayer()
            self.setProgress(100)
    
        # DATA AND POLYGONS
        else:
            # Enable progress bar
            self.enableProgress(enable=True)
            if len(self.geographic_list) == 0:
                self.iface.messageBar().pushMessage("Ooops!", "You have to select at least one geographical granularity", level=Qgis.Critical, duration=5)
                self.error_flag = True
                self.setProgress(0)
                self.enableProgress(enable=False)
            else:
                # Data
                self.labelLoading.setText("Cargando datos del indicador " + self.indicator + " ...")
                self.labelLoading.repaint()
                self.setProgress(1)
                self.drawDataLayer()
                self.setProgress(100)
                # Polygons 
                for geographical_granularity in self.geographic_list:
                
                    if geographical_granularity == "DISTRICTS":
                        code = cache.download_carto(self, geographical_granularity, self.selected_district)
                    elif geographical_granularity == "SECTIONS":
                        code = cache.download_carto(self, geographical_granularity, self.selected_section)
                    else:
                        code = cache.download_carto(self, geographical_granularity)
                        
                    if code is not 0:
                        # Enable progress bar
                        self.enableProgress(enable=True)
                        self.labelLoading.setText("Cargando cartografía " + geographical_granularity + " ...")
                        self.labelLoading.repaint()
                        self.setProgress(1) 
                        self.drawPolygons(geographical_granularity)
                        self.setProgress(100)
        
        if not self.error_flag and code is 1:
            self.close()
    
    def enableProgress(self, enable=True):
        if enable:
            self.labelLoading.setVisible(True)
            self.pBar.setVisible(True)
        else:
            self.labelLoading.setVisible(False)
            self.pBar.setVisible(False)
            
    def setProgress(self, progress):
        self.pBar.setValue(progress)
        

    def getLayerMetadata(self, m, layer=None, is_indicator=None, identifier=None, parent_identifier=None, title=None, type=None, lang='es-ES', abstract=None, category=None, file_path=None, file_extension=None):

        # Source: https://github.com/qgis/QGIS/blob/master/tests/src/python/test_qgsmetadatawidget.py 
        """
        Create a fully populated QgsLayerMetadata object, then set it to the widget and re-read back
        the generated metadata to ensure that no content is lost.
        """
        
        # IDENTIFICATION
        m.setIdentifier(identifier)
        m.setParentIdentifier(parent_identifier)
        m.setTitle(title)
        m.setType(type)
        m.setLanguage(lang)
        m.setAbstract(abstract)
        m.setKeywords({
            'gmd:topicCategory': [category]
            #'GEMET': ['kw1', 'kw2']
        })

        # EXTENT
        m.setCrs(QgsCoordinateReferenceSystem.fromOgcWmsCrs('EPSG:4326'))

        e = QgsLayerMetadata.Extent()
        se = QgsLayerMetadata.SpatialExtent()
        se.extentCrs = QgsCoordinateReferenceSystem.fromOgcWmsCrs('EPSG:4326')
        
        # Get layer extent
        ext = layer.extent()
        xmin = ext.xMinimum()
        xmax = ext.xMaximum()
        ymin = ext.yMinimum()
        ymax = ext.yMaximum()
        se.bounds = QgsBox3d(xmin, ymin, 0, xmax, ymax, 0)
        e.setSpatialExtents([se])
        
        # Date extension
        if is_indicator is False:
            if "DISTRICTS" in self.geographic_list:
                date_districts = self.selected_district
                year = int(date_districts[:4])
                month = int(date_districts[4:-2])
                day = int(date_districts[-2:])
                dates = [
                    QgsDateTimeRange(
                        QDateTime(QDate(year, month, day), QTime(0, 0, 0)),
                        QDateTime(QDate(year, month, day), QTime(0, 0, 0)))
                ]
                
            elif "SECTIONS" in self.geographic_list:
                date_sections = self.selected_section
                year = int(date_sections[:4])
                month = int(date_sections[4:-2])
                day = int(date_sections[-2:])
                dates = [
                    QgsDateTimeRange(
                        QDateTime(QDate(year, month, day), QTime(0, 0, 0)),
                        QDateTime(QDate(year, month, day), QTime(0, 0, 0)))
                ]
            else:
                dates = [
                QgsDateTimeRange(
                    QDateTime(QDate(0, 0, 0), QTime(0, 0, 0)),
                    QDateTime(QDate(0, 0, 0), QTime(0, 0, 0)))
            ]
        else:
            # Get min and max temporal codes
            temporal_code_ranges = cache.get_temporal_code_from_csv(self, self.indicator)
            max_date = temporal_code_ranges['max'].split("/")
            min_date = temporal_code_ranges['min'].split("/")
            
            dates = [
                QgsDateTimeRange(
                    QDateTime(QDate(int(min_date[2]), int(min_date[1]), int(min_date[0])), QTime(0, 0, 0)),
                    QDateTime(QDate(int(max_date[2]), int(max_date[1]), int(max_date[0])), QTime(0, 0, 0))
                    
                )
            ]
        
        e.setTemporalExtents(dates)
        m.setExtent(e)
        
        # ACCESS
        m.setFees('None')
        m.setLicenses(['http://www.gobiernodecanarias.org/istac/aviso_legal.html'])
        m.setRights(['Instituto Canario de Estadística (ISTAC)'])
        m.setConstraints([QgsLayerMetadata.Constraint('Instituto Canario de Estadística (ISTAC)', 'by')])

        # CONTACT
        c = QgsLayerMetadata.Contact()
        c.name = 'Instituto Canario de Estadística (ISTAC)'
        c.position = 'Atención ciudadana'
        c.organization = 'ISTAC'
        c.role = 'pointOfContact'
        c.email = 'consultas.istac@gobiernodecanarias.org'
        c.voice = '+34 928290104'
        c.fax = '+34 928243354'
        address = QgsLayerMetadata.Address()
        #address.type = 'postal'
        address.address = 'C/ Luis Doreste Silva, 101, Planta 7'
        address.city = 'Las Palmas de Gran Canaria'
        #address.administrativeArea = 'Santa Cruz de Tenerife'
        address.postalCode = '35004'
        address.country = 'Spain'
        c.addresses = [address]
        m.setContacts([c])
        
        # LINKS
        file_size = cache.get_file_size(self, file_path, file_extension)
        
        if is_indicator is False:
            
            link_list = []
            link_carto_var_elements = polygons.get_geojson_data(self, title)
            
            for element in link_carto_var_elements:
                l = QgsLayerMetadata.Link()
                l.name = element
                l.type = 'WWW:LINK'
                l.description = None
                l.url = 'https://www3.gobiernodecanarias.org/istac/api/structural-resources/v1.0/variables/VR_TERRITORIO/variableelements/' + element + '/geoinfo'
                l.format = 'OGR/GeoJSON'
                l.mimeType = 'application/json'
                l.size = str(int(file_size/len(link_carto_var_elements)))
                link_list.append(l)
                
            m.setLinks(link_list)
            
        else:
    
            l = QgsLayerMetadata.Link()
            l.name = title
            l.type = 'WWW:LINK'
            l.description = None
            l.url = 'https://www3.gobiernodecanarias.org/istac/api/indicators/v1.0/indicators/' + title + '/data'
            l.format = 'JSON'
            l.mimeType = 'application/json'
            l.size = str(file_size)
            
            m.setLinks([l])
        
        # HISTORY
        # m.setHistory(['history a', 'history b'])
        
        return m
