# -*- coding: utf-8 -*-
"""
/***************************************************************************
 styletotext
                                 A QGIS plugin
 Converts stylefiles to csv-files
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-11-29
        git sha              : $Format:%H$
        copyright            : (C) 2023 by Mathias Kusk
        email                : Mathias.kusk@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .style_to_excel_dialog import styletoexcelDialog
import os.path
import re
import xml.etree.ElementTree as ET
import csv


from qgis.core import QgsMapLayer, QgsProject, QgsMessageLog

class styletoexcel:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'styletoexcel_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&QML-style to Excel')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('styletoexcel', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/style_to_excel/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'QML-style to excel'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&QML-style to Excel'),
                action)
            self.iface.removeToolBarIcon(action)

    def select_style_file(self):
        filename, _filter = QFileDialog.getOpenFileName(
            self.dlg, "Select input stylefile ","", '*.qml')
        self.dlg.lineEdit_stylefile.setText(filename)
        self.stylefile = filename
        QgsMessageLog.logMessage(f"The filename is: {self.stylefile}")

    def select_csv_file(self):
        csvfilename, _filter = QFileDialog.getSaveFileName(
            self.dlg, "Select output csvfile ","", '*.csv')
        self.dlg.lineEdit_csvfile.setText(csvfilename)
        self.outputfile = csvfilename

    def extract_color_from_qml(self):
        with open(self.stylefile, 'r') as file:
            data = file.read()
        pattern = r'<Option name="color" value="(.*?)" type="QString"/>'
        matches = re.findall(pattern, data)
        QgsMessageLog.logMessage(f"The match is: {matches}")
        if matches:
            for match in matches:
                QgsMessageLog.logMessage(f"The colors are: {match}")
            return matches
        else:
            return None

    def extract_cats_from_qml(self):
        with open(self.stylefile, 'r') as file:
            data = file.read()
        pattern = r'<category symbol="(.*?)" label="(.*?)" value="(.*?)"'
        matches = re.findall(pattern, data)
        QgsMessageLog.logMessage(f"The match is: {matches}")
        if matches:
            for match in matches:
                QgsMessageLog.logMessage(f"The categories are: {match}")
            return matches
        else:
            return None

    def get_graduated_from_xml(self):
        with open(self.stylefile, 'r') as file:
            xml_data = file.read()        
        # Replace escape characters
        regexp = re.compile(r'&lt;|&gt;|&amp;|&quot;|&apos;')  # regex to catch the characters '&lt;', '&gt;', '&amp;', '&quot;', '&apos;'
        replacement_map = {'&lt;': 'less than', '&gt;': 'greater than', '&amp;': 'and', '&quot;': 'quote', '&apos;': 'apostrophe'}  # map a character to the replacement value.
        fixed_xml = regexp.sub(lambda match: replacement_map[match.group(0)], xml_data)  # do the replacement
        # Parse the fixed XML data
        root = ET.fromstring(fixed_xml)
        ranges = root.findall('./renderer-v2/ranges/range')
        symbols = root.findall('./renderer-v2/symbols/symbol/layer/Option/Option')
        upper = [range.get('upper') for range in ranges]
        labels = [range.get('label') for range in ranges]
        lower = [range.get('lower') for range in ranges]
        colorfill = [symbol.get('value') for symbol in symbols if symbol.get('name')=="color"]
        outline_color = [symbol.get('value') for symbol in symbols if symbol.get('name')=="outline_color"]
        outline_style = [symbol.get('value') for symbol in symbols if symbol.get('name')=="outline_style"]
        outline_width = [symbol.get('value') for symbol in symbols if symbol.get('name')=="outline_width"]
        dict_to_print = {'Label': labels, 
            'Lower val.': lower, 
            'Upper val.': upper, 
            'Fill color': colorfill,
            'Outline color': outline_color,
            'Outline style': outline_style,
            'Outline width': outline_width
            }
        #QgsMessageLog.logMessage(f"Dictionary for ranges: {dict_to_print} at value {i}")
        self.dict_forcsv = dict_to_print

    def get_categories_from_xml(self):
        with open(self.stylefile, 'r') as file:
            xml_data = file.read()        
        # Replace escape characters
        regexp = re.compile(r'&lt;|&gt;|&amp;|&quot;|&apos;')  # regex to catch the characters '&lt;', '&gt;', '&amp;', '&quot;', '&apos;'
        replacement_map = {'&lt;': 'less than', '&gt;': 'greater than', '&amp;': 'and', '&quot;': 'quote', '&apos;': 'apostrophe'}  # map a character to the replacement value.
        fixed_xml = regexp.sub(lambda match: replacement_map[match.group(0)], xml_data)  # do the replacement
        # Parse the fixed XML data
        root = ET.fromstring(fixed_xml)
        categories = root.findall('./renderer-v2/categories/category')
        symbols = root.findall('./renderer-v2/symbols/symbol/layer/Option/Option')
        #setup the lists
        cat_symbols = [category.get('symbol') for category in categories]
        labels = [category.get('label') for category in categories]
        values = [category.get('value') for category in categories]
        colorfill = [symbol.get('value') for symbol in symbols if symbol.get('name')=="color"]
        outline_color = [symbol.get('value') for symbol in symbols if symbol.get('name')=="outline_color"]
        outline_style = [symbol.get('value') for symbol in symbols if symbol.get('name')=="outline_style"]
        outline_width = [symbol.get('value') for symbol in symbols if symbol.get('name')=="outline_width"]
        dict_to_print = {'Symbol': cat_symbols, 
                    'Label': labels, 
                    'Value': values, 
                    'Fill color': colorfill,
                    'Outline Color': outline_color,
                    'Outline style': outline_style,
                    'Outline width': outline_width
                    }
        #QgsMessageLog.logMessage(f"Dictionary for categories: {dict_to_print} at value {i}")
        self.dict_forcsv = dict_to_print
    
    def get_rasterrenderer_from_xml(self):
        with open(self.stylefile, 'r') as file:
            xml_data = file.read()        
        # Replace escape characters
        regexp = re.compile(r'&lt;|&gt;|&amp;|&quot;|&apos;')  # regex to catch the characters '&lt;', '&gt;', '&amp;', '&quot;', '&apos;'
        replacement_map = {'&lt;': 'less than', '&gt;': 'greater than', '&amp;': 'and', '&quot;': 'quote', '&apos;': 'apostrophe'}  # map a character to the replacement value.
        fixed_xml = regexp.sub(lambda match: replacement_map[match.group(0)], xml_data)  # do the replacement
        # Parse the fixed XML data
        root = ET.fromstring(fixed_xml)
        categories = root.findall('./pipe/rasterrenderer')
        symbols = root.findall('./pipe/rasterrenderer/rastershader/colorrampshader/item')
        #setup the lists
        rasterr_type = [category.get('type') for category in categories]
        cMax = [category.get('classificationMax') for category in categories]
        cMin = [category.get('classificationMin') for category in categories]
        label = [symbol.attrib['label'] for symbol in symbols]
        color = [symbol.attrib['color'] for symbol in symbols]
        value = [symbol.attrib['value'] for symbol in symbols]
        #lists to dicts
        dict_to_print = {'Rasterrenderer type': rasterr_type, 
                    'Classification Max.': cMax, 
                    'Classification Min.': cMin, 
                    'Label': label,
                    'Colorcode': color,
                    'Value': value}
        QgsMessageLog.logMessage(f"Dictionary for categories: {dict_to_print}")
        self.dict_forcsv = dict_to_print

    def write_file(self):
        self.determine_style_type()
        #QgsMessageLog.logMessage(f"Outputfile: {self.outputfile}")
        # Check if self.dict_forcsv is not None
        if self.dict_forcsv is not None:
            try:
                #QgsMessageLog.logMessage(str(self.dict_forcsv))
                with open(self.outputfile,'w') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=self.dict_forcsv[0].keys())
                    writer.writeheader()
                    for row in self.dict_forcsv:
                        writer.writerow(row)
            except Exception as e:
                QgsMessageLog.logMessage(f"Writing failed: {str(e)}")
        else:
            QgsMessageLog.logMessage("self.dict_forcsv is None. Please make sure get_categories_from_xml is executed correctly.")

    def write_file2(self):
        self.determine_style_type()
        if self.dict_forcsv is not None:
            try:
                # Get the maximum length of the lists in the dictionary
                max_len = max(len(lst) for lst in self.dict_forcsv.values())
                # Write the dictionary to a CSV file
                with open(self.outputfile, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(self.dict_forcsv.keys())
                    for i in range(max_len):
                        writer.writerow([self.dict_forcsv[key][i] if i < len(self.dict_forcsv[key]) else '' for key in self.dict_forcsv])
            except Exception as e:
                QgsMessageLog.logMessage(f"Writing failed: {str(e)}")
        else:
            QgsMessageLog.logMessage("self.dict_forcsv is None. Please make sure get_categories_from_xml is executed correctly.")
        
    def determine_style_type(self):
        #QgsMessageLog.logMessage("Determine style triggered")
        #Styletype is found by XML-lookups
        tree = ET.parse(self.stylefile)
        root = tree.getroot()
        try:
            renderer_v2 = root.find('renderer-v2')
        except:
            pass
        try:
            rasterrenderer = root.find('pipe')
        except:
            pass
        if renderer_v2 is not None:
            first_child = list(renderer_v2)[0]
        elif rasterrenderer is not None:
            first_child = list(rasterrenderer)[0]
        else:
            QgsMessageLog.logMessage(f"Sorry. This type of stylefile will only be supported in a future release.\n--------------------------------------------------\n")
            return
        #QgsMessageLog.logMessage(first_child.tag)
        if first_child.tag == 'ranges':
            self.get_graduated_from_xml()
            return
        if first_child.tag == 'categories':
            self.get_categories_from_xml()
            return
        if first_child.tag == 'rasterrenderer':
            self.get_rasterrenderer_from_xml()
            return
        else:
            QgsMessageLog.logMessage(f"Sorry - you tried parsing {first_child.tag}. \nThis version only supports categories and graduated/ranges.\n The update is in the making. \n If you wanna contribute please reach out.")
            return

    def run(self):

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = styletoexcelDialog()
            self.dlg.filebrowser_stylefile.clicked.connect(self.select_style_file)
            self.dlg.filebrowser_csvfile.clicked.connect(self.select_csv_file)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            self.write_file2()
