# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widget.ui'
#
# Created: Mon Aug 04 14:45:24 2014
#      by: PyQt4 UI code generator 4.11.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Widget(object):
    def setupUi(self, Widget):
        Widget.setObjectName(_fromUtf8("Widget"))
        Widget.resize(600, 900)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Widget.sizePolicy().hasHeightForWidth())
        Widget.setSizePolicy(sizePolicy)
        Widget.setMinimumSize(QtCore.QSize(600, 900))
        Widget.setMaximumSize(QtCore.QSize(600, 1200))
        Widget.setStyleSheet(_fromUtf8("/*Custom settings reference\n"
"\n"
"Colors:\n"
"litegrey:QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #c8ced2,\n"
"        stop:0.5 #a1a6aa,\n"
"        stop:1 #7f8387\n"
"    );\n"
"grey:QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #585e62,\n"
"        stop:0.5 #474c50,\n"
"        stop:1 #393e41\n"
"    );\n"
"midgrey:QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #1a1d1e,\n"
"        stop:0.2 #2a2d30,\n"
"        stop:1 #2d3033\n"
"    );\n"
"darkgrey:QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #171a1b,\n"
"        stop:0.2 #272a2c,\n"
"        stop:1 #232528\n"
"    );\n"
"blue: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #4d93dd,\n"
"        stop:0.5 #326fae,\n"
"        stop:1 #225a89\n"
"    );\n"
"green: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #6d9b5d,\n"
"        stop:0.5 #5e8a4f,\n"
"        stop:1 #588449\n"
"    );\n"
"red: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #c05556,\n"
"        stop:0.5 #aa4344,\n"
"        stop:1 #993839\n"
"    );\n"
"*/\n"
"\n"
"/*User Custom*/\n"
"#Form{\n"
"    background-image: url(images/background.png);\n"
"}\n"
"\n"
"/*System Custom*/\n"
"*[mandatoryField=\"true\"] { \n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #171a1b,\n"
"        stop:0.2 #272a2c,\n"
"        stop:1 #232528\n"
"    );\n"
"}\n"
"\n"
"/*QWidget*/\n"
"QWidget {\n"
"   background-color: #313538;\n"
"    color: #ffffff;\n"
"    font-family: Arial;\n"
"    font-size: 12px;\n"
"    font-weight:bold;\n"
"}\n"
"\n"
"QWidget:disabled {\n"
"    color: #585e62;\n"
"    font-family: Arial;\n"
"    font-size: 12px;\n"
"    font-weight:bold;\n"
"}\n"
"\n"
"/*QPushButton*/\n"
"QPushButton {\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #4d93dd,\n"
"        stop:0.5 #326fae,\n"
"        stop:1 #225a89\n"
"    );\n"
"    border: 1px outset #282b2e;\n"
"    border-radius: 8px;\n"
"    padding: 5px;\n"
"}\n"
"QPushButton:pressed {\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #1a1d1e,\n"
"        stop:0.15 #2a2d30,\n"
"        stop:1 #2d3033\n"
"    );\n"
" }\n"
"QPushButton:disabled {\n"
"    color: #888888;\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #585e62,\n"
"        stop:0.5 #474c50,\n"
"        stop:1 #393e41\n"
"    );\n"
" }\n"
"\n"
"/*QToolButton*/\n"
"QToolButton {\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #4d93dd,\n"
"        stop:0.5 #326fae,\n"
"        stop:1 #225a89\n"
"    );\n"
"    border: 1px outset #282b2e;\n"
"    border-radius: 8px;\n"
"    padding: 5px;\n"
"}\n"
"QToolButton:pressed {\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #1a1d1e,\n"
"        stop:0.15 #2a2d30,\n"
"        stop:1 #2d3033\n"
"    );\n"
" }\n"
"\n"
"/*QListWidget*/\n"
" QListWidget::item{ \n"
"    padding-right:5px;\n"
"}\n"
" QListWidget::item:selected { \n"
"    border-radius: 4px;\n"
"    border: 1px outset #282b2e;\n"
"    color: #ffffff;\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #4d93dd,\n"
"        stop:0.5 #326fae,\n"
"        stop:1 #225a89\n"
" );\n"
"}\n"
" QListWidget::item:disabled { \n"
"    border: 0px;\n"
"    color: #585e62;\n"
"    background-color: #313538;\n"
"}\n"
" QListWidget::indicator {\n"
"    width: 16px;\n"
"    height: 16px;\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #585e62,\n"
"        stop:0.5 #474c50,\n"
"        stop:1 #393e41\n"
"    );\n"
"    border: none;\n"
"    border-radius: 5px;\n"
" }\n"
"QListWidget::indicator:unchecked:hover {\n"
" background-color:QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #171a1b,\n"
"        stop:0.2 #272a2c,\n"
"        stop:1 #2a2c20\n"
"    );\n"
" }\n"
"QListWidget::indicator:unchecked:pressed {\n"
" background-color:QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #171a1b,\n"
"        stop:0.2 #272a2c,\n"
"        stop:1 #2a2c20\n"
"    );\n"
" }\n"
"QListWidget::indicator:checked {\n"
"     image: url(images/checkbox_checked.png);\n"
" }\n"
"QListWidget::indicator:checked:disabled {\n"
"     image: url(images/checkbox_checked_disabled.png);\n"
" }\n"
"QListWidget::indicator:checked:hover {\n"
" background-color:QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #171a1b,\n"
"        stop:0.2 #272a2c,\n"
"        stop:1 #2a2c20\n"
"    );\n"
" }\n"
"QListWidget::indicator:checked:pressed {\n"
" background-color:QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #171a1b,\n"
"        stop:0.2 #272a2c,\n"
"        stop:1 #2a2c20\n"
"    );\n"
" }\n"
"\n"
"\n"
"/*QCheckBox*/\n"
"QCheckBox {\n"
"    spacing: 5px;\n"
" }\n"
" QCheckBox::indicator {\n"
"    width: 18px;\n"
"    height: 18px;\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #585e62,\n"
"        stop:0.5 #474c50,\n"
"        stop:1 #393e41\n"
"    );\n"
"    border: none;\n"
"    border-radius: 5px;\n"
" }\n"
"QCheckBox::indicator:unchecked:hover {\n"
" background-color:QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #171a1b,\n"
"        stop:0.2 #272a2c,\n"
"        stop:1 #2a2c20\n"
"    );\n"
" }\n"
"QCheckBox::indicator:unchecked:pressed {\n"
" background-color:QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #171a1b,\n"
"        stop:0.2 #272a2c,\n"
"        stop:1 #2a2c20\n"
"    );\n"
" }\n"
"QCheckBox::indicator:checked {\n"
"     image: url(images/checkbox_checked.png);\n"
" }\n"
"QCheckBox::indicator:checked:disabled {\n"
"     image: url(images/checkbox_checked_disabled.png);\n"
" }\n"
"QCheckBox::indicator:checked:hover {\n"
" background-color:QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #171a1b,\n"
"        stop:0.2 #272a2c,\n"
"        stop:1 #2a2c20\n"
"    );\n"
" }\n"
"QCheckBox::indicator:checked:pressed {\n"
" background-color:QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #171a1b,\n"
"        stop:0.2 #272a2c,\n"
"        stop:1 #2a2c20\n"
"    );\n"
" }\n"
"\n"
"/*QCheckBox*/\n"
"QRadioButton {\n"
"    spacing: 5px;\n"
" }\n"
" QRadioButton::indicator {\n"
"    width: 18px;\n"
"    height: 18px;\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #1a1d1e,\n"
"        stop:0.15 #2a2d30,\n"
"        stop:1 #2d3033\n"
"    );\n"
"    border: none;\n"
"    border-radius: 8px;\n"
" }\n"
"QRadioButton::indicator:unchecked:hover {\n"
" background-color:QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #171a1b,\n"
"        stop:0.2 #272a2c,\n"
"        stop:1 #2a2c20\n"
"    );\n"
" }\n"
"QRadioButton::indicator:unchecked:pressed {\n"
" background-color:QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #171a1b,\n"
"        stop:0.2 #272a2c,\n"
"        stop:1 #2a2c20\n"
"    );\n"
" }\n"
"QRadioButton::indicator:checked {\n"
"     image: url(images/radiobutton_checked.png);\n"
" }\n"
"QRadioButton::indicator:checked:hover {\n"
" background-color:QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #171a1b,\n"
"        stop:0.2 #272a2c,\n"
"        stop:1 #2a2c20\n"
"    );\n"
" }\n"
"QRadioButton::indicator:checked:pressed {\n"
" background-color:QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #171a1b,\n"
"        stop:0.2 #272a2c,\n"
"        stop:1 #2a2c20\n"
"    );\n"
" }\n"
"\n"
"/*QLineEdit*/\n"
"QLineEdit {\n"
"    border: 1px solid #282b2e;\n"
"    border-radius: 8px;\n"
"    padding: 5px;\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #1a1d1e,\n"
"        stop:0.15 #2a2d30,\n"
"        stop:1 #2d3033\n"
"    );\n"
"    selection-background-color: black;\n"
" }\n"
"QLineEdit:read-only {\n"
"     background: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #2d3033,\n"
"        stop:1 #2d3033\n"
"    );\n"
"}\n"
"\n"
"/*QAbstractScrollArea*/\n"
"QAbstractScrollArea {\n"
"    min-height: 25px;\n"
"    border: 1px solid #282b2e;\n"
"    padding: 5px;\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #585e62,\n"
"        stop:0.5 #474c50,\n"
"        stop:1 #393e41\n"
"    );\n"
"    selection-background-color: rgba(50, 112, 175,50);\n"
" }\n"
"\n"
" QListView {\n"
"    min-height: 25px;\n"
"    border: 1px solid #282b2e;\n"
"    padding: 5px;\n"
"    alternate-background-color: #393e41;\n"
"    background-color: #474c50;\n"
"    selection-background-color: rgba(50, 112, 175,50);\n"
" }\n"
" \n"
" QListView:Disabled {\n"
"    min-height: 25px;\n"
"    border: 1px solid #282b2e;\n"
"    padding: 5px;\n"
"    background-color: #313538;\n"
"    selection-background-color: rgba(50, 112, 175,50);\n"
" }\n"
" \n"
"/*QTextEdit, QPlainTextEdit*/\n"
"QTextEdit, QPlainTextEdit {\n"
"    background-image: url(:images/images/sizegrip.png);\n"
"    background-repeat:no-repeat;\n"
"    background-position: bottom right;\n"
"    background-attachment: scroll;\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #1a1d1e,\n"
"        stop:0.05 #2a2d30,\n"
"        stop:1 #2d3033\n"
"    );\n"
"    selection-background-color: black;\n"
" }\n"
"\n"
"/*QScrollBar*/\n"
"QScrollBar:horizontal {\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #171a1b,\n"
"        stop:0.2 #272a2c,\n"
"        stop:1 #232528\n"
"    );\n"
"    max-height: 8px;\n"
"}\n"
"QScrollBar::handle:horizontal {\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #c8ced2,\n"
"        stop:0.5 #a1a6aa,\n"
"        stop:1 #7f8387\n"
"    );\n"
"}\n"
"QScrollBar::handle:horizontal:hover, QScrollBar::handle:horizontal:pressed {\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #c8ced2,\n"
"        stop:1 #a1a6aa\n"
"    );\n"
"}\n"
"QScrollBar::add-line:horizontal {\n"
"      background: none;\n"
"}\n"
"QScrollBar::sub-line:horizontal {\n"
"      background: none;\n"
"}\n"
"QScrollBar::add-line:horizontal:hover, QScrollBar::add-line:horizontal:pressed , QScrollBar::sub-line:horizontal:hover, QScrollBar::sub-line:horizontal:pressed {\n"
"      background: none;\n"
"}\n"
"QScrollBar::left-arrow:horizontal {\n"
"      background: none;\n"
"}\n"
"QScrollBar::right-arrow:horizontal{\n"
"      background: none;\n"
"}\n"
"QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {\n"
"    background: none;\n"
"}\n"
"\n"
"\n"
"QScrollBar:vertical {\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #171a1b,\n"
"        stop:0.2 #272a2c,\n"
"        stop:1 #232528\n"
"    );\n"
"    max-width: 8px;\n"
"}\n"
"QScrollBar:vertical:disabled {\n"
"    background-color: #313538;\n"
"    max-width: 8px;\n"
"}\n"
"QScrollBar::handle:vertical {\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #c8ced2,\n"
"        stop:0.5 #a1a6aa,\n"
"        stop:1 #7f8387\n"
"    );\n"
"}\n"
"QScrollBar::handle:vertical:disabled {\n"
"    background-color: #313538;\n"
"}\n"
"QScrollBar::handle:vertical:hover, QScrollBar::handle:vertical:pressed {\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #c8ced2,\n"
"        stop:1 #a1a6aa\n"
"    );\n"
"}\n"
"QScrollBar::add-line:vertical {\n"
"      background: none;\n"
"}\n"
"QScrollBar::sub-line:vertical {\n"
"      background: none;\n"
"}\n"
"QScrollBar::add-line:vertical:hover, QScrollBar::add-line:vertical:pressed , QScrollBar::sub-line:vertical:hover, QScrollBar::sub-line:vertical:pressed {\n"
"      background: none;\n"
"}\n"
"QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {    \n"
"      background: none;\n"
"}\n"
"QScrollBar::down-arrow:vertical {    \n"
"      background: none;\n"
"}\n"
"QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
"      background: none;\n"
"}\n"
"\n"
"/*QSlider*/\n"
"QSlider:groove:horizontal  {\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #171a1b,\n"
"        stop:0.2 #272a2c,\n"
"        stop:1 #232528\n"
"    );\n"
"    border-radius: 8px;\n"
"}\n"
"QSlider::handle:horizontal {\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #c8ced2,\n"
"        stop:0.5 #a1a6aa,\n"
"        stop:1 #7f8387\n"
"    );\n"
"    border-radius: 8px;\n"
"    width: 30px;\n"
"}\n"
"QSlider::handle:horizontal:hover, QSlider::handle:horizontal:pressed {\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #c8ced2,\n"
"        stop:1 #a1a6aa\n"
"    );\n"
"    border-radius: 8px;\n"
"}\n"
"\n"
"QSlider:groove:vertical  {\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #171a1b,\n"
"        stop:0.2 #272a2c,\n"
"        stop:1 #232528\n"
"    );\n"
"    border-radius: 8px;\n"
"}\n"
"QSlider::handle:vertical {\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #c8ced2,\n"
"        stop:0.5 #a1a6aa,\n"
"        stop:1 #7f8387\n"
"    );\n"
"    border-radius: 8px;\n"
"    height: 30px;\n"
"}\n"
"QSlider::handle:vertical:hover, QSlider::handle:vertical:pressed {\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #c8ced2,\n"
"        stop:1 #a1a6aa\n"
"    );\n"
"    border-radius: 8px;\n"
"}\n"
"\n"
"/*QGroupBox*/\n"
"QGroupBox {\n"
"     background-color: #313538;\n"
"     border: 1px inset #282b2e;\n"
"     margin-top: 8px;\n"
" }\n"
" QGroupBox::title {\n"
"     subcontrol-origin: margin;\n"
"     subcontrol-position: top center;\n"
"     padding: 0 3px;\n"
" }\n"
" QGroupBox::indicator {\n"
"    width: 18px;\n"
"    height: 18px;\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #585e62,\n"
"        stop:0.5 #474c50,\n"
"        stop:1 #393e41\n"
"    );\n"
"    border: none;\n"
"    border-radius: 5px;\n"
" }\n"
"QGroupBox::indicator:unchecked:hover {\n"
" background-color:QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #171a1b,\n"
"        stop:0.2 #272a2c,\n"
"        stop:1 #2a2c20\n"
"    );\n"
" }\n"
"QGroupBox::indicator:unchecked:pressed {\n"
" background-color:QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #171a1b,\n"
"        stop:0.2 #272a2c,\n"
"        stop:1 #2a2c20\n"
"    );\n"
" }\n"
"QGroupBox::indicator:checked {\n"
"     image: url(images/checkbox_checked.png);\n"
" }\n"
"QGroupBox::indicator:checked:disabled {\n"
"     image: url(images/checkbox_checked_disabled.png);\n"
" }\n"
"QGroupBox::indicator:checked:hover {\n"
" background-color:QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #171a1b,\n"
"        stop:0.2 #272a2c,\n"
"        stop:1 #2a2c20\n"
"    );\n"
" }\n"
"QGroupBox::indicator:checked:pressed {\n"
" background-color:QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #171a1b,\n"
"        stop:0.2 #272a2c,\n"
"        stop:1 #2a2c20\n"
"    );\n"
" }\n"
"\n"
"/*QProgressBar*/\n"
"QProgressBar {\n"
"     text-align: center;\n"
"     border: 1px outset #282b2e;\n"
"     border-radius: 8px;\n"
"     background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #171a1b,\n"
"        stop:0.2 #272a2c,\n"
"        stop:1 #232528\n"
"    );\n"
" }\n"
" QProgressBar::chunk {\n"
"    border-radius: 8px;\n"
"     background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #4d93dd,\n"
"        stop:0.5 #326fae,\n"
"        stop:1 #225a89\n"
"    );\n"
" }\n"
"\n"
"/*QLabel*/\n"
"QLabel {\n"
"     border: 0px #282b2e;\n"
"     padding: 5px;\n"
" }\n"
"\n"
"/*QStatusBar*/\n"
"QStatusBar {\n"
"     font-size: 11px;\n"
"     border: 1px outset #282b2e;\n"
"     border-radius: 6px;\n"
"     margin: 2px;\n"
"     padding: 3px;\n"
"     background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #585e62,\n"
"        stop:0.1 #474c50,\n"
"        stop:0.9 #474c50,\n"
"        stop:1 #393e41\n"
"    );\n"
" }\n"
"\n"
"/*QMenuBar*/\n"
"QMenuBar {\n"
"     font-size: 11px;\n"
"     border: 1px outset #282b2e;\n"
"     border-radius: 6px;\n"
"     margin: 2px;\n"
"     background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #585e62,\n"
"        stop:0.1 #474c50,\n"
"        stop:0.9 #474c50,\n"
"        stop:1 #393e41\n"
"    );\n"
" }\n"
" QMenuBar::item {\n"
"     spacing: 10px;\n"
"     padding: 5px;\n"
"     background: transparent;\n"
"     border-radius: 4px;\n"
" }\n"
" QMenuBar::item:selected { \n"
"    border-radius: 6px;\n"
"    border: 1px outset #282b2e;\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #c8ced2,\n"
"        stop:0.5 #a1a6aa,\n"
"        stop:1 #7f8387\n"
"    );\n"
" }\n"
" QMenuBar::item:pressed {\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #c8ced2,\n"
"        stop:1 #a1a6aa\n"
"    );\n"
" }\n"
"\n"
"/*QMenu*/\n"
"QMenu {\n"
"    font-size: 11px;\n"
"    border: 1px outset #282b2e;\n"
"    border-radius: 6px;\n"
"    margin: 2px;\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #585e62,\n"
"        stop:0.1 #474c50,\n"
"        stop:0.9 #474c50,\n"
"        stop:1 #393e41\n"
"    );\n"
" }\n"
" QMenu::item {\n"
"    border-radius: 6px;\n"
"    padding: 5px;\n"
"    border: 1px solid transparent;\n"
"    background-color: transparent;\n"
" }\n"
" QMenu::item:selected {\n"
"    border-radius: 6px;\n"
"    border: 1px outset #282b2e;\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #c8ced2,\n"
"        stop:0.5 #a1a6aa,\n"
"        stop:1 #7f8387\n"
"    );\n"
" }\n"
" QMenu::icon:checked {\n"
"     background: gray;\n"
"     border: 1px inset gray;\n"
"     position: absolute;\n"
"     top: 1px;\n"
"     right: 1px;\n"
"     bottom: 1px;\n"
"     left: 1px;\n"
" }\n"
" QMenu::separator {\n"
"     height: 1px;\n"
"     background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #171a1b,\n"
"        stop:0.2 #272a2c,\n"
"        stop:1 #232528\n"
"    );\n"
"     margin-left: 5px;\n"
"     margin-right: 5px;\n"
" }\n"
" QMenu::indicator {\n"
"     width: 13px;\n"
"     height: 13px;\n"
" }\n"
"\n"
"/*QHeaderView*/\n"
"QHeaderView::section {\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #585e62,\n"
"        stop:0.5 #474c50,\n"
"        stop:1 #393e41\n"
"    );\n"
"    border: 1px outset #282b2e;\n"
"    border-radius: 8px;\n"
"    padding: 0px 5px 0 5px;\n"
"}\n"
"QHeaderView::section {\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #585e62,\n"
"        stop:0.5 #474c50,\n"
"        stop:1 #393e41\n"
"    );\n"
"    border: 1px outset #282b2e;\n"
"    border-radius: 8px;\n"
"    padding: 0px 5px 0 5px;\n"
"}\n"
"QHeaderView::section:hover {\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #171a1b,\n"
"        stop:0.2 #272a2c,\n"
"        stop:1 #232528\n"
"    );\n"
"}\n"
" QHeaderView::section:checked{\n"
"    background-color: #232528;\n"
"}\n"
"QHeaderView::down-arrow {\n"
"    image: url(:images/images/down_arrow.png);\n"
" }\n"
"QHeaderView::up-arrow {\n"
"    image: url(:images/images/up_arrow.png);\n"
"}\n"
"\n"
"/*QTreeView*/\n"
"QTreeView QAbstractScrollArea {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    padding: 0px;\n"
"}\n"
"QTreeView QHeaderView::section {\n"
"    font-size: 11px;\n"
"    text-align: center;\n"
"    margin-bottom:5px;\n"
"}\n"
"QTreeView::branch:has-siblings:!adjoins-item {\n"
"     border-image: url(:images/images/vline.png) 0;\n"
"}\n"
" QTreeView::branch:has-siblings:adjoins-item {\n"
"     border-image: url(:images/images/branch-more.png) 0;\n"
"}\n"
" QTreeView::branch:!has-children:!has-siblings:adjoins-item {\n"
"     border-image: url(:images/images/branch-end.png) 0;\n"
"}\n"
"QTreeView::branch:has-children:!has-siblings:closed,\n"
"QTreeView::branch:closed:has-children:has-siblings {\n"
"         border-image: none;\n"
"         image: url(:images/images/branch-closed.png);\n"
"}\n"
"\n"
" QTreeView::branch:open:has-children:!has-siblings,\n"
" QTreeView::branch:open:has-children:has-siblings  {\n"
"         border-image: none;\n"
"         image: url(:images/images/branch-open.png);\n"
"}\n"
"\n"
"/*QTableView*/\n"
"QTableView QAbstractScrollArea {\n"
"    background-color: transparent;\n"
"    border: none;\n"
"    padding: 0px;\n"
"}\n"
"QTableView QHeaderView::section {\n"
"    font-size: 11px;\n"
"    margin-bottom:5px;\n"
"}\n"
"QTableView QTableCornerButton::section {\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #4d93dd,\n"
"        stop:0.5 #326fae,\n"
"        stop:1 #225a89\n"
"    );\n"
"    border: 1px outset #282b2e;\n"
"    border-radius: 8px;\n"
"    padding: 5px;\n"
" }\n"
"\n"
"/*QComboBox*/\n"
"QComboBox {\n"
"    border: 1px outset #282b2e;\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #585e62,\n"
"        stop:0.5 #474c50,\n"
"        stop:1 #393e41\n"
"    );\n"
"     border-radius: 8px;\n"
"     padding: 5px 18px 5px 5px;\n"
"     min-width: 30px;\n"
" }\n"
" QComboBox:editable {\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #585e62,\n"
"        stop:0.5 #474c50,\n"
"        stop:1 #393e41\n"
"    );\n"
" }\n"
" QComboBox:!editable, QComboBox::drop-down:editable {\n"
"      background: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #585e62,\n"
"        stop:0.5 #474c50,\n"
"        stop:1 #393e41\n"
"    );\n"
" }\n"
" QComboBox:!editable:on, QComboBox::drop-down:editable:on {\n"
"     background: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #1a1d1e,\n"
"        stop:0.2 #2a2d30,\n"
"        stop:1 #2d3033\n"
"    );\n"
" }\n"
" QComboBox::drop-down {\n"
"     subcontrol-origin: padding;\n"
"     subcontrol-position: top right;\n"
"     width: 30px;\n"
"\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #4d93dd,\n"
"        stop:0.5 #326fae,\n"
"        stop:1 #225a89\n"
"    );\n"
"\n"
"     border-left-width: 1px;\n"
"     border-left-color: #2d3033;\n"
"     border-left-style: solid;\n"
"     border-top-right-radius: 8px;\n"
"     border-bottom-right-radius: 8px;\n"
" }\n"
" QComboBox::drop-down:disabled{\n"
"     subcontrol-origin: padding;\n"
"     subcontrol-position: top right;\n"
"     width: 30px;\n"
"\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #585e62,\n"
"        stop:0.5 #474c50,\n"
"        stop:1 #393e41\n"
"    );\n"
"\n"
"     border-left-width: 1px;\n"
"     border-left-color: #2d3033;\n"
"     border-left-style: solid;\n"
"     border-top-right-radius: 8px;\n"
"     border-bottom-right-radius: 8px;\n"
" }\n"
" QComboBox::down-arrow {\n"
"    image: url(:images/images/down_arrow.png);\n"
" }\n"
" QComboBox::down-arrow:on {\n"
"    image: url(:images/images/up_arrow.png);\n"
" }\n"
"QPushButton {\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #4d93dd,\n"
"        stop:0.5 #326fae,\n"
"        stop:1 #225a89\n"
"    );\n"
"    border: 1px outset #282b2e;\n"
"    border-radius: 8px;\n"
"    padding: 5px;\n"
"}\n"
"QPushButton:pressed {\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #1a1d1e,\n"
"        stop:0.15 #2a2d30,\n"
"        stop:1 #2d3033\n"
"    );\n"
" }\n"
"QPushButton:disabled {\n"
"    color: #888888;\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #585e62,\n"
"        stop:0.5 #474c50,\n"
"        stop:1 #393e41\n"
"    );\n"
" }\n"
"/*QSpinBox*/\n"
"QSpinBox {\n"
"    border: 1px outset #282b2e;\n"
"    border-radius: 8px;\n"
"    padding:5px;\n"
"     padding-right: 20px;\n"
"     background: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #1a1d1e,\n"
"        stop:0.2 #2a2d30,\n"
"        stop:1 #2d3033\n"
"    );\n"
"    selection-background-color: black;\n"
" }\n"
" QSpinBox::up-button {\n"
"     subcontrol-position: top right;\n"
"     border-top-right-radius: 8px;\n"
"    top:1px;\n"
"    background-color:QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #c8ced2,\n"
"        stop:0.5 #a1a6aa,\n"
"        stop:1 #7f8387\n"
"    );\n"
" }\n"
" QSpinBox::up-arrow {\n"
"     image: url(images/up_arrow.png);\n"
" }\n"
" QSpinBox::up-button:hover QSpinBox::up-button:pressed {\n"
"     border-color: #a1a6aa;\n"
" }\n"
" QSpinBox::down-button {\n"
"     subcontrol-position: bottom right;\n"
"     border-bottom-right-radius: 8px;\n"
"    background-color:QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #c8ced2,\n"
"        stop:0.5 #a1a6aa,\n"
"        stop:1 #7f8387\n"
"    );\n"
" }\n"
" QSpinBox::down-arrow {\n"
"     image: url(images/down_arrow.png);\n"
" }\n"
" QSpinBox::down-button:hover QSpinBox::down-button:pressed {\n"
"     border-color: #a1a6aa;\n"
" }\n"
"\n"
"/*QDoubleSpinBox*/\n"
"QDoubleSpinBox {\n"
"    border: 1px outset #282b2e;\n"
"    border-radius: 8px;\n"
"    padding:5px;\n"
"     padding-right: 20px;\n"
"     background: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #1a1d1e,\n"
"        stop:0.2 #2a2d30,\n"
"        stop:1 #2d3033\n"
"    );\n"
"    selection-background-color: black;\n"
" }\n"
" QDoubleSpinBox::up-button {\n"
"     subcontrol-position: top right;\n"
"     border-top-right-radius: 8px;\n"
"    top:1px;\n"
"    background-color:QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #c8ced2,\n"
"        stop:0.5 #a1a6aa,\n"
"        stop:1 #7f8387\n"
"    );\n"
" }\n"
" QDoubleSpinBox::up-arrow {\n"
"     image: url(images/up_arrow.png);\n"
" }\n"
" QDoubleSpinBox::up-button:hover QDoubleSpinBox::up-button:pressed {\n"
"     border-color: #a1a6aa;\n"
" }\n"
" QDoubleSpinBox::down-button {\n"
"     subcontrol-position: bottom right;\n"
"     border-bottom-right-radius: 8px;\n"
"    background-color:QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #c8ced2,\n"
"        stop:0.5 #a1a6aa,\n"
"        stop:1 #7f8387\n"
"    );\n"
" }\n"
" QDoubleSpinBox::down-arrow {\n"
"     image: url(images/down_arrow.png);\n"
" }\n"
" QDoubleSpinBox::down-button:hover QDoubleSpinBox::down-button:pressed {\n"
"     border-color: #a1a6aa;\n"
" }\n"
"\n"
"/*QTimeEdit*/\n"
"QTimeEdit {\n"
"    border: 1px outset #282b2e;\n"
"    border-radius: 8px;\n"
"    padding:5px;\n"
"     padding-right: 20px;\n"
"     background: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #1a1d1e,\n"
"        stop:0.2 #2a2d30,\n"
"        stop:1 #2d3033\n"
"    );\n"
"    selection-background-color: black;\n"
" }\n"
" QTimeEdit::up-button {\n"
"     subcontrol-position: top right;\n"
"     border-top-right-radius: 8px;\n"
"    top:1px;\n"
"    background-color:QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #c8ced2,\n"
"        stop:0.5 #a1a6aa,\n"
"        stop:1 #7f8387\n"
"    );\n"
" }\n"
" QTimeEdit::up-arrow {\n"
"     image: url(images/up_arrow.png);\n"
" }\n"
" QTimeEdit::up-button:hover QTimeEdit::up-button:pressed {\n"
"     border-color: #a1a6aa;\n"
" }\n"
" QTimeEdit::down-button {\n"
"     subcontrol-position: bottom right;\n"
"     border-bottom-right-radius: 8px;\n"
"    background-color:QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #c8ced2,\n"
"        stop:0.5 #a1a6aa,\n"
"        stop:1 #7f8387\n"
"    );\n"
" }\n"
" QTimeEdit::down-arrow {\n"
"     image: url(images/down_arrow.png);\n"
" }\n"
" QTimeEdit::down-button:hover QTimeEdit::down-button:pressed {\n"
"     border-color: #a1a6aa;\n"
" }\n"
"\n"
"/*QDateTimeEdit*/\n"
"QDateTimeEdit {\n"
"    border: 1px outset #282b2e;\n"
"    border-radius: 8px;\n"
"    padding:5px;\n"
"     padding-right: 20px;\n"
"     background: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #1a1d1e,\n"
"        stop:0.2 #2a2d30,\n"
"        stop:1 #2d3033\n"
"    );\n"
"    selection-background-color: black;\n"
" }\n"
" QDateTimeEdit::up-button {\n"
"     subcontrol-position: top right;\n"
"     border-top-right-radius: 8px;\n"
"    top:1px;\n"
"    background-color:QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #c8ced2,\n"
"        stop:0.5 #a1a6aa,\n"
"        stop:1 #7f8387\n"
"    );\n"
" }\n"
" QDateTimeEdit::up-arrow {\n"
"     image: url(images/up_arrow.png);\n"
" }\n"
" QDateTimeEdit::up-button:hover QDateTimeEdit::up-button:pressed {\n"
"     border-color: #a1a6aa;\n"
" }\n"
" QDateTimeEdit::down-button {\n"
"     subcontrol-position: bottom right;\n"
"     border-bottom-right-radius: 8px;\n"
"    background-color:QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #c8ced2,\n"
"        stop:0.5 #a1a6aa,\n"
"        stop:1 #7f8387\n"
"    );\n"
" }\n"
" QDateTimeEdit::down-arrow {\n"
"     image: url(images/down_arrow.png);\n"
" }\n"
" QDateTimeEdit::down-button:hover QDateTimeEdit::down-button:pressed {\n"
"     border-color: #a1a6aa;\n"
" }\n"
"\n"
"/*QTabWidget*/\n"
"QTabWidget::pane { /* The tab widget frame */\n"
"     background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #171a1b,\n"
"        stop:0.2 #272a2c,\n"
"        stop:1 #232528\n"
"    );\n"
"     border: 2px solid #393e41;\n"
"     position: absolute;\n"
" }\n"
" QTabWidget::tab-bar {\n"
"     alignment: left;\n"
" }\n"
" QTabBar::tab {\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #585e62,\n"
"        stop:0.5 #474c50,\n"
"        stop:1 #393e41\n"
"    );\n"
"    color: #ffffff;\n"
"    font-family: Arial;\n"
"    font-size: 12px;\n"
"    font-weight:bold;\n"
"    border-top-left-radius: 8px;\n"
"    border-top-right-radius: 8px;\n"
"    min-width: 16ex;\n"
"    padding: 5px 20px 5px 20px;\n"
"    margin: 0px 2px 0px 2px;\n"
" }\n"
" QTabBar::tab:selected {\n"
"     border-color: #9B9B9B;\n"
"     border-bottom-color: #C2C7CB; \n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #4d93dd,\n"
"        stop:0.5 #326fae,\n"
"        stop:1 #225a89\n"
"    );\n"
" }\n"
"QTabBar::tab:pressed {\n"
"    background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #1a1d1e,\n"
"        stop:0.15 #2a2d30,\n"
"        stop:1 #2d3033\n"
"    );\n"
" }\n"
"\n"
"/*QToolBox*/\n"
"QToolBox::tab {\n"
"     background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #585e62,\n"
"        stop:0.5 #474c50,\n"
"        stop:1 #393e41\n"
"    );\n"
"     border-radius: 5px;\n"
"     color: darkgray;\n"
" }\n"
" QToolBox::tab:selected {\n"
"     color: white;\n"
" }\n"
" QToolBox::tab:hover {\n"
"     background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #171a1b,\n"
"        stop:0.2 #272a2c,\n"
"        stop:1 #232528\n"
"    );\n"
" }\n"
"\n"
"/*QDial*/\n"
"QDial {\n"
"     background-color: QLinearGradient(\n"
"        x1:0, y1:0,\n"
"        x2:0, y2:1,\n"
"        stop:0 #585e62,\n"
"        stop:0.5 #474c50,\n"
"        stop:1 #393e41\n"
"    );\n"
" }"))
        self.verticalLayout = QtGui.QVBoxLayout(Widget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox_2 = QtGui.QGroupBox(Widget)
        self.groupBox_2.setMinimumSize(QtCore.QSize(0, 251))
        self.groupBox_2.setStyleSheet(_fromUtf8("QGroupBox {\n"
"     font-size: 14px;\n"
" }"))
        self.groupBox_2.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.groupBox_2.setCheckable(True)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.groupBox_ClientProject = QtGui.QGroupBox(self.groupBox_2)
        self.groupBox_ClientProject.setGeometry(QtCore.QRect(300, 10, 271, 61))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_ClientProject.sizePolicy().hasHeightForWidth())
        self.groupBox_ClientProject.setSizePolicy(sizePolicy)
        self.groupBox_ClientProject.setTitle(_fromUtf8(""))
        self.groupBox_ClientProject.setCheckable(False)
        self.groupBox_ClientProject.setObjectName(_fromUtf8("groupBox_ClientProject"))
        self.comboBox_ClientProject = QtGui.QComboBox(self.groupBox_ClientProject)
        self.comboBox_ClientProject.setGeometry(QtCore.QRect(10, 20, 251, 31))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_ClientProject.sizePolicy().hasHeightForWidth())
        self.comboBox_ClientProject.setSizePolicy(sizePolicy)
        self.comboBox_ClientProject.setObjectName(_fromUtf8("comboBox_ClientProject"))
        self.comboBox_ClientProject.addItem(_fromUtf8(""))
        self.groupBox_CopyTools = QtGui.QGroupBox(self.groupBox_2)
        self.groupBox_CopyTools.setGeometry(QtCore.QRect(300, 80, 271, 161))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_CopyTools.sizePolicy().hasHeightForWidth())
        self.groupBox_CopyTools.setSizePolicy(sizePolicy)
        self.groupBox_CopyTools.setStyleSheet(_fromUtf8("QGroupBox {\n"
"     font-size: 12px;\n"
" }"))
        self.groupBox_CopyTools.setCheckable(True)
        self.groupBox_CopyTools.setObjectName(_fromUtf8("groupBox_CopyTools"))
        self.listWidget_CopyTools = QtGui.QListWidget(self.groupBox_CopyTools)
        self.listWidget_CopyTools.setGeometry(QtCore.QRect(10, 20, 251, 131))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget_CopyTools.sizePolicy().hasHeightForWidth())
        self.listWidget_CopyTools.setSizePolicy(sizePolicy)
        self.listWidget_CopyTools.setStyleSheet(_fromUtf8(""))
        self.listWidget_CopyTools.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.listWidget_CopyTools.setObjectName(_fromUtf8("listWidget_CopyTools"))
        item = QtGui.QListWidgetItem()
        self.listWidget_CopyTools.addItem(item)
        item = QtGui.QListWidgetItem()
        self.listWidget_CopyTools.addItem(item)
        item = QtGui.QListWidgetItem()
        self.listWidget_CopyTools.addItem(item)
        item = QtGui.QListWidgetItem()
        self.listWidget_CopyTools.addItem(item)
        self.groupBox_ClientConfig = QtGui.QGroupBox(self.groupBox_2)
        self.groupBox_ClientConfig.setGeometry(QtCore.QRect(10, 10, 281, 61))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_ClientConfig.sizePolicy().hasHeightForWidth())
        self.groupBox_ClientConfig.setSizePolicy(sizePolicy)
        self.groupBox_ClientConfig.setTitle(_fromUtf8(""))
        self.groupBox_ClientConfig.setCheckable(False)
        self.groupBox_ClientConfig.setObjectName(_fromUtf8("groupBox_ClientConfig"))
        self.comboBox_ClientConfig = QtGui.QComboBox(self.groupBox_ClientConfig)
        self.comboBox_ClientConfig.setGeometry(QtCore.QRect(10, 20, 251, 31))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_ClientConfig.sizePolicy().hasHeightForWidth())
        self.comboBox_ClientConfig.setSizePolicy(sizePolicy)
        self.comboBox_ClientConfig.setObjectName(_fromUtf8("comboBox_ClientConfig"))
        self.groupBox_CopyClient = QtGui.QGroupBox(self.groupBox_2)
        self.groupBox_CopyClient.setGeometry(QtCore.QRect(10, 80, 281, 161))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_CopyClient.sizePolicy().hasHeightForWidth())
        self.groupBox_CopyClient.setSizePolicy(sizePolicy)
        self.groupBox_CopyClient.setStyleSheet(_fromUtf8("QGroupBox {\n"
"     font-size: 12px;\n"
" }"))
        self.groupBox_CopyClient.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.groupBox_CopyClient.setFlat(False)
        self.groupBox_CopyClient.setCheckable(True)
        self.groupBox_CopyClient.setObjectName(_fromUtf8("groupBox_CopyClient"))
        self.listWidget_CopyClient = QtGui.QListWidget(self.groupBox_CopyClient)
        self.listWidget_CopyClient.setGeometry(QtCore.QRect(10, 20, 261, 131))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget_CopyClient.sizePolicy().hasHeightForWidth())
        self.listWidget_CopyClient.setSizePolicy(sizePolicy)
        self.listWidget_CopyClient.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.listWidget_CopyClient.setObjectName(_fromUtf8("listWidget_CopyClient"))
        item = QtGui.QListWidgetItem()
        self.listWidget_CopyClient.addItem(item)
        item = QtGui.QListWidgetItem()
        self.listWidget_CopyClient.addItem(item)
        item = QtGui.QListWidgetItem()
        self.listWidget_CopyClient.addItem(item)
        item = QtGui.QListWidgetItem()
        self.listWidget_CopyClient.addItem(item)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBox = QtGui.QGroupBox(Widget)
        self.groupBox.setMinimumSize(QtCore.QSize(0, 251))
        self.groupBox.setStyleSheet(_fromUtf8("QGroupBox {\n"
"     font-size: 14px;\n"
" }"))
        self.groupBox.setCheckable(True)
        self.groupBox.setChecked(False)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.groupBox_ServerProject = QtGui.QGroupBox(self.groupBox)
        self.groupBox_ServerProject.setGeometry(QtCore.QRect(300, 10, 271, 61))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_ServerProject.sizePolicy().hasHeightForWidth())
        self.groupBox_ServerProject.setSizePolicy(sizePolicy)
        self.groupBox_ServerProject.setTitle(_fromUtf8(""))
        self.groupBox_ServerProject.setCheckable(False)
        self.groupBox_ServerProject.setObjectName(_fromUtf8("groupBox_ServerProject"))
        self.comboBox_ServerProject = QtGui.QComboBox(self.groupBox_ServerProject)
        self.comboBox_ServerProject.setGeometry(QtCore.QRect(10, 20, 251, 31))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_ServerProject.sizePolicy().hasHeightForWidth())
        self.comboBox_ServerProject.setSizePolicy(sizePolicy)
        self.comboBox_ServerProject.setObjectName(_fromUtf8("comboBox_ServerProject"))
        self.comboBox_ServerProject.addItem(_fromUtf8(""))
        self.groupBox_ServerConfig = QtGui.QGroupBox(self.groupBox)
        self.groupBox_ServerConfig.setGeometry(QtCore.QRect(10, 10, 281, 61))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_ServerConfig.sizePolicy().hasHeightForWidth())
        self.groupBox_ServerConfig.setSizePolicy(sizePolicy)
        self.groupBox_ServerConfig.setTitle(_fromUtf8(""))
        self.groupBox_ServerConfig.setCheckable(False)
        self.groupBox_ServerConfig.setObjectName(_fromUtf8("groupBox_ServerConfig"))
        self.comboBox_ServerConfig = QtGui.QComboBox(self.groupBox_ServerConfig)
        self.comboBox_ServerConfig.setGeometry(QtCore.QRect(10, 20, 251, 31))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_ServerConfig.sizePolicy().hasHeightForWidth())
        self.comboBox_ServerConfig.setSizePolicy(sizePolicy)
        self.comboBox_ServerConfig.setObjectName(_fromUtf8("comboBox_ServerConfig"))
        self.groupBox_CopyServer = QtGui.QGroupBox(self.groupBox)
        self.groupBox_CopyServer.setGeometry(QtCore.QRect(10, 80, 561, 161))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_CopyServer.sizePolicy().hasHeightForWidth())
        self.groupBox_CopyServer.setSizePolicy(sizePolicy)
        self.groupBox_CopyServer.setStyleSheet(_fromUtf8("QGroupBox {\n"
"     font-size: 12px;\n"
" }"))
        self.groupBox_CopyServer.setCheckable(False)
        self.groupBox_CopyServer.setChecked(False)
        self.groupBox_CopyServer.setObjectName(_fromUtf8("groupBox_CopyServer"))
        self.listWidget_CopyServer = QtGui.QListWidget(self.groupBox_CopyServer)
        self.listWidget_CopyServer.setGeometry(QtCore.QRect(10, 20, 541, 131))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget_CopyServer.sizePolicy().hasHeightForWidth())
        self.listWidget_CopyServer.setSizePolicy(sizePolicy)
        self.listWidget_CopyServer.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.listWidget_CopyServer.setObjectName(_fromUtf8("listWidget_CopyServer"))
        item = QtGui.QListWidgetItem()
        self.listWidget_CopyServer.addItem(item)
        item = QtGui.QListWidgetItem()
        self.listWidget_CopyServer.addItem(item)
        item = QtGui.QListWidgetItem()
        self.listWidget_CopyServer.addItem(item)
        item = QtGui.QListWidgetItem()
        self.listWidget_CopyServer.addItem(item)
        self.verticalLayout.addWidget(self.groupBox)
        self.grpGenerate = QtGui.QGroupBox(Widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.grpGenerate.sizePolicy().hasHeightForWidth())
        self.grpGenerate.setSizePolicy(sizePolicy)
        self.grpGenerate.setMinimumSize(QtCore.QSize(0, 61))
        self.grpGenerate.setObjectName(_fromUtf8("grpGenerate"))
        self.splitter_2 = QtGui.QSplitter(self.grpGenerate)
        self.splitter_2.setGeometry(QtCore.QRect(12, 20, 561, 31))
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName(_fromUtf8("splitter_2"))
        self.checkBox_CopyDebug = QtGui.QCheckBox(self.splitter_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkBox_CopyDebug.sizePolicy().hasHeightForWidth())
        self.checkBox_CopyDebug.setSizePolicy(sizePolicy)
        self.checkBox_CopyDebug.setObjectName(_fromUtf8("checkBox_CopyDebug"))
        self.checkBox_CopyExporters = QtGui.QCheckBox(self.splitter_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkBox_CopyExporters.sizePolicy().hasHeightForWidth())
        self.checkBox_CopyExporters.setSizePolicy(sizePolicy)
        self.checkBox_CopyExporters.setObjectName(_fromUtf8("checkBox_CopyExporters"))
        self.checkBox_CopyPDB = QtGui.QCheckBox(self.splitter_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkBox_CopyPDB.sizePolicy().hasHeightForWidth())
        self.checkBox_CopyPDB.setSizePolicy(sizePolicy)
        self.checkBox_CopyPDB.setChecked(True)
        self.checkBox_CopyPDB.setObjectName(_fromUtf8("checkBox_CopyPDB"))
        self.pushButton_GenerateAction = QtGui.QPushButton(self.splitter_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_GenerateAction.sizePolicy().hasHeightForWidth())
        self.pushButton_GenerateAction.setSizePolicy(sizePolicy)
        self.pushButton_GenerateAction.setObjectName(_fromUtf8("pushButton_GenerateAction"))
        self.verticalLayout.addWidget(self.grpGenerate)
        self.groupBox_Actions = QtGui.QGroupBox(Widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_Actions.sizePolicy().hasHeightForWidth())
        self.groupBox_Actions.setSizePolicy(sizePolicy)
        self.groupBox_Actions.setMinimumSize(QtCore.QSize(0, 281))
        self.groupBox_Actions.setCheckable(False)
        self.groupBox_Actions.setObjectName(_fromUtf8("groupBox_Actions"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox_Actions)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.splitter_3 = QtGui.QSplitter(self.groupBox_Actions)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter_3.sizePolicy().hasHeightForWidth())
        self.splitter_3.setSizePolicy(sizePolicy)
        self.splitter_3.setOrientation(QtCore.Qt.Vertical)
        self.splitter_3.setObjectName(_fromUtf8("splitter_3"))
        self.listWidget_Actions = QtGui.QListWidget(self.splitter_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget_Actions.sizePolicy().hasHeightForWidth())
        self.listWidget_Actions.setSizePolicy(sizePolicy)
        self.listWidget_Actions.setMinimumSize(QtCore.QSize(0, 37))
        self.listWidget_Actions.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.listWidget_Actions.setObjectName(_fromUtf8("listWidget_Actions"))
        item = QtGui.QListWidgetItem()
        item.setCheckState(QtCore.Qt.Checked)
        self.listWidget_Actions.addItem(item)
        item = QtGui.QListWidgetItem()
        item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEditable|QtCore.Qt.ItemIsDragEnabled|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
        item.setCheckState(QtCore.Qt.Checked)
        self.listWidget_Actions.addItem(item)
        item = QtGui.QListWidgetItem()
        item.setCheckState(QtCore.Qt.Checked)
        self.listWidget_Actions.addItem(item)
        item = QtGui.QListWidgetItem()
        self.listWidget_Actions.addItem(item)
        self.splitter = QtGui.QSplitter(self.splitter_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.checkBox_SyncUser = QtGui.QCheckBox(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkBox_SyncUser.sizePolicy().hasHeightForWidth())
        self.checkBox_SyncUser.setSizePolicy(sizePolicy)
        self.checkBox_SyncUser.setObjectName(_fromUtf8("checkBox_SyncUser"))
        self.pushButton_BeginCopying = QtGui.QPushButton(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_BeginCopying.sizePolicy().hasHeightForWidth())
        self.pushButton_BeginCopying.setSizePolicy(sizePolicy)
        self.pushButton_BeginCopying.setMinimumSize(QtCore.QSize(162, 32))
        self.pushButton_BeginCopying.setObjectName(_fromUtf8("pushButton_BeginCopying"))
        self.verticalLayout_2.addWidget(self.splitter_3)
        self.verticalLayout.addWidget(self.groupBox_Actions)

        self.retranslateUi(Widget)
        self.listWidget_CopyTools.setCurrentRow(0)
        self.listWidget_CopyClient.setCurrentRow(0)
        self.listWidget_CopyServer.setCurrentRow(0)
        QtCore.QObject.connect(self.pushButton_GenerateAction, QtCore.SIGNAL(_fromUtf8("clicked()")), self.listWidget_Actions.clear)
        QtCore.QMetaObject.connectSlotsByName(Widget)

    def retranslateUi(self, Widget):
        Widget.setWindowTitle(_translate("Widget", "Widget", None))
        self.groupBox_2.setTitle(_translate("Widget", "Copy Client and Tools", None))
        self.comboBox_ClientProject.setItemText(0, _translate("Widget", "Project", None))
        self.groupBox_CopyTools.setTitle(_translate("Widget", "Copy Tools", None))
        __sortingEnabled = self.listWidget_CopyTools.isSortingEnabled()
        self.listWidget_CopyTools.setSortingEnabled(False)
        item = self.listWidget_CopyTools.item(0)
        item.setText(_translate("Widget", "Build 1", None))
        item = self.listWidget_CopyTools.item(1)
        item.setText(_translate("Widget", "Build 2", None))
        item = self.listWidget_CopyTools.item(2)
        item.setText(_translate("Widget", "Build 3", None))
        item = self.listWidget_CopyTools.item(3)
        item.setText(_translate("Widget", "etc.", None))
        self.listWidget_CopyTools.setSortingEnabled(__sortingEnabled)
        self.groupBox_CopyClient.setTitle(_translate("Widget", "Copy Client", None))
        __sortingEnabled = self.listWidget_CopyClient.isSortingEnabled()
        self.listWidget_CopyClient.setSortingEnabled(False)
        item = self.listWidget_CopyClient.item(0)
        item.setText(_translate("Widget", "Build 1", None))
        item = self.listWidget_CopyClient.item(1)
        item.setText(_translate("Widget", "Build 2", None))
        item = self.listWidget_CopyClient.item(2)
        item.setText(_translate("Widget", "Build 3", None))
        item = self.listWidget_CopyClient.item(3)
        item.setText(_translate("Widget", "etc.", None))
        self.listWidget_CopyClient.setSortingEnabled(__sortingEnabled)
        self.groupBox.setTitle(_translate("Widget", "Copy Server", None))
        self.comboBox_ServerProject.setItemText(0, _translate("Widget", "Project", None))
        self.groupBox_CopyServer.setTitle(_translate("Widget", "Copy Server", None))
        __sortingEnabled = self.listWidget_CopyServer.isSortingEnabled()
        self.listWidget_CopyServer.setSortingEnabled(False)
        item = self.listWidget_CopyServer.item(0)
        item.setText(_translate("Widget", "Build 1", None))
        item = self.listWidget_CopyServer.item(1)
        item.setText(_translate("Widget", "Build 2", None))
        item = self.listWidget_CopyServer.item(2)
        item.setText(_translate("Widget", "Build 3", None))
        item = self.listWidget_CopyServer.item(3)
        item.setText(_translate("Widget", "etc.", None))
        self.listWidget_CopyServer.setSortingEnabled(__sortingEnabled)
        self.grpGenerate.setTitle(_translate("Widget", "Generate Actions", None))
        self.checkBox_CopyDebug.setText(_translate("Widget", "Copy Debug", None))
        self.checkBox_CopyExporters.setText(_translate("Widget", "Copy Exporters", None))
        self.checkBox_CopyPDB.setText(_translate("Widget", "Copy .pdb files", None))
        self.pushButton_GenerateAction.setText(_translate("Widget", "Generate Action List", None))
        self.groupBox_Actions.setTitle(_translate("Widget", "Actions to be executed", None))
        __sortingEnabled = self.listWidget_Actions.isSortingEnabled()
        self.listWidget_Actions.setSortingEnabled(False)
        item = self.listWidget_Actions.item(0)
        item.setText(_translate("Widget", "Action 1", None))
        item = self.listWidget_Actions.item(1)
        item.setText(_translate("Widget", "Action 2", None))
        item = self.listWidget_Actions.item(2)
        item.setText(_translate("Widget", "Action 3", None))
        item = self.listWidget_Actions.item(3)
        item.setText(_translate("Widget", "etc.", None))
        self.listWidget_Actions.setSortingEnabled(__sortingEnabled)
        self.checkBox_SyncUser.setText(_translate("Widget", "Sync USER-PC OR OTHER REALLY LONG P4 FOLDER NAME", None))
        self.pushButton_BeginCopying.setText(_translate("Widget", "Begin Copying", None))

