# -*- coding: utf-8 -*-
from __future__ import unicode_literals


# - License: AGPLv3
# this add-on offers two enhancements:
# - in the Fields Dialog there are Up/Down buttons as an
#   alternative to the reposition button so that you don't
#   have to enter the new number of the field.
# - batch change fonts for 
#     - all fields for current note (from fields window)
#     - all fields for all notes (from main window)
#     - all cards in the browser (from main window)



import aqt
from aqt import mw
from aqt.qt import *
from aqt.fields import FieldDialog
from PyQt4 import QtCore, QtGui
from aqt.utils import tooltip, askUser


#from qtdesigner
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



class Batch_Fonts_Dialog_Designer(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(525, 85)
        self.verticalLayoutWidget = QtGui.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 521, 80))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.fontComboBox = QtGui.QFontComboBox(self.verticalLayoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fontComboBox.sizePolicy().hasHeightForWidth())
        self.fontComboBox.setSizePolicy(sizePolicy)
        self.fontComboBox.setObjectName(_fromUtf8("fontComboBox"))
        self.horizontalLayout.addWidget(self.fontComboBox)
        self.spinBox = QtGui.QSpinBox(self.verticalLayoutWidget)
        self.spinBox.setMinimum(5)
        self.spinBox.setSingleStep(1)
        self.spinBox.setProperty("value", 20)
        self.spinBox.setObjectName(_fromUtf8("spinBox"))
        self.horizontalLayout.addWidget(self.spinBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtGui.QDialogButtonBox(self.verticalLayoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        self.label.setText(_translate("Dialog", "Editing Font:", None))





class Batch_Fonts_Dialog(QDialog):
    def __init__(self):
        parent = aqt.mw.app.activeWindow()
        QDialog.__init__(self, parent=parent)
        self.setWindowModality(Qt.WindowModal)
        self.bfonts = Batch_Fonts_Dialog_Designer()  
        self.bfonts.setupUi(self)


#change all fonts of current note type from editor window
def onAllFonts(self):
    m=Batch_Fonts_Dialog()
    m.setWindowTitle("Anki Set Fonts For All Fields Of This Note")
    #load current values into window
    fld = self.model['flds'][self.currentIdx]
    m.bfonts.fontComboBox.setCurrentFont(QFont(fld['font']))
    m.bfonts.spinBox.setValue(fld['size'])
    if m.exec_():  # this is True if dialog is 'accepted, False otherwise  https://stackoverflow.com/a/11553456
        font = m.bfonts.fontComboBox.currentFont().family()
        size = m.bfonts.spinBox.value()
        for i in range(len(self.model['flds'])):
            fld = self.model['flds'][i]
            fld['font'] = font
            fld['size'] = size
        #reload for current value, adjusted from loadField
        fld = self.model['flds'][self.currentIdx]
        f = self.form
        f.fontFamily.setCurrentFont(QFont(fld['font']))
        f.fontSize.setValue(fld['size'])
    else:
        tooltip('declined')
FieldDialog.onAllFonts = onAllFonts


#minimal modification of onPosition(self, delta=-1):
def onMove(self, direction):
    idx = self.currentIdx
    try: 
        pos = idx + direction    #check if idx is None
    except:
        return
    else:
        l = len(self.model['flds'])
        if not 0 <= pos <= l-1:
            return
        self.saveField()
        f = self.model['flds'][self.currentIdx]
        self.mw.progress.start()
        self.mm.moveField(self.model, f, pos)
        self.mw.progress.finish()
        self.fillFields()
        self.form.fieldList.setCurrentRow(pos)
FieldDialog.onMove = onMove


#overwrite/monkey patch function from aqt/fields.py
def __init__(self, mw, note, ord=0, parent=None):
    QDialog.__init__(self, parent or mw) #, Qt.Window)
    self.mw = mw
    self.parent = parent or mw
    self.note = note
    self.col = self.mw.col
    self.mm = self.mw.col.models
    self.model = note.model()
    self.mw.checkpoint(_("Fields"))
    self.form = aqt.forms.fields.Ui_Dialog()
    self.form.setupUi(self)

    ####start of my mod
    #up/down
    self.form.udbox = QtGui.QHBoxLayout()
    layout = self.form.udbox

    bu = QtGui.QToolButton()
    bu.setArrowType(Qt.UpArrow)
    bu.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    bu.clicked.connect(lambda _: self.onMove(-1))
    layout.addWidget(bu)

    bd = QtGui.QToolButton()
    bd.setArrowType(Qt.DownArrow)
    bd.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    bd.clicked.connect(lambda _: self.onMove(1))
    layout.addWidget(bd)

    self.form.verticalLayout_3.addLayout(self.form.udbox)


    #self.form.setupUi(self) muss davor sein, sonst sind ja attribute noch nicht vergeben
    self.form.allfonts = QtGui.QPushButton(self)
    self.form.allfonts.setText("AllFonts")
    self.form.allfonts.clicked.connect(self.onAllFonts)
    self.form.verticalLayout_3.addWidget(self.form.allfonts)
 
    ####end of my mod
    self.setWindowTitle(_("Fields for %s") % self.model['name'])
    self.form.buttonBox.button(QDialogButtonBox.Help).setAutoDefault(False)
    self.form.buttonBox.button(QDialogButtonBox.Close).setAutoDefault(False)
    self.currentIdx = None
    self.oldSortField = self.model['sortf']
    self.fillFields()
    self.setupSignals()
    self.form.fieldList.setCurrentRow(0)
    self.exec_()
FieldDialog.__init__ = __init__


#change for all note types from menu
def batch_change_fonts_all_fields_all_notes():
    m=Batch_Fonts_Dialog()
    m.setWindowTitle("Anki Set Fonts For All Fields Of ALL Notes")
    #load current values into window
    try:
        m.bfonts.fontComboBox.setCurrentFont("Arial")
        m.bfonts.spinBox.setValue(fld['size'])
    except:
        pass
    if m.exec_():  # this is True if dialog is 'accepted, False otherwise  https://stackoverflow.com/a/11553456
        font = m.bfonts.fontComboBox.currentFont().family()
        size = m.bfonts.spinBox.value()
        if askUser("Do you really want to set the fonts for \n" \
                    "ALL fields of ALL notes to the font: \n" \
                    + '    ' + str(font) + '\n' \
                    + 'and this size: \n' \
                    + '    ' + str(size)):
            for m in mw.col.models.all():
                for f in m['flds']:
                    f['font'] = font
                for f in m['flds']:
                    f['size'] = size
            mw.col.models.save(m)
            tooltip('Done')
batch_font_action = QAction("Batch change fonts on all fields all notes", mw)
batch_font_action.triggered.connect(batch_change_fonts_all_fields_all_notes)
mw.form.menuTools.addAction(batch_font_action)




#change for all note types from menu
def batch_browser_change_fonts_all_fields_all_notes():
    m=Batch_Fonts_Dialog()
    m.setWindowTitle("Anki Set Fonts for all cards in BROWSER")
    #load current values into window
    try:
        m.bfonts.fontComboBox.setCurrentFont("Arial")
        m.bfonts.spinBox.setValue(fld['size'])
    except:
        pass
    if m.exec_():  # this is True if dialog is 'accepted, False otherwise  https://stackoverflow.com/a/11553456
        font = m.bfonts.fontComboBox.currentFont().family()
        size = m.bfonts.spinBox.value()
        if askUser("Do you really want to set the fonts for \n" \
                    "for all cards in BROWSER to the font: \n" \
                    + '    ' + str(font) + '\n' \
                    + 'and this size: \n' \
                    + '    ' + str(size)):
            for m in mw.col.models.all():
                for c in m['tmpls']:
                    c['bfont'] = font
                    c['bsize'] = size
            mw.col.models.save(m)
            tooltip('Done')
batch_browser_font_action = QAction("Batch change fonts for all cards in BROWSER", mw)
batch_browser_font_action.triggered.connect(batch_browser_change_fonts_all_fields_all_notes)
mw.form.menuTools.addAction(batch_browser_font_action)
