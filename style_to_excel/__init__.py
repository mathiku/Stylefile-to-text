# -*- coding: utf-8 -*-
"""
/***************************************************************************
 styletoexcel
                                 A QGIS plugin
 Should export a stylefile (QML) to excel
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2023-11-29
        copyright            : (C) 2023 by Mathias Kusk
        email                : Mathias.kusk@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load styletoexcel class from file styletoexcel.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .style_to_excel import styletoexcel
    return styletoexcel(iface)
