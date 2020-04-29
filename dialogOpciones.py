from PyQt5 import uic, QtCore, QtGui, QtWidgets

widget_ui_ = uic.loadUiType("/home/pi/proyectoLavamanos/UI/opciones.ui")[0]

class dialogOpciones(QtWidgets.QDialog, widget_ui_):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)

        self.setWindowTitle('Opciones')
        self.tfCanillaAbiertaInicial.setInputMask('000000')
        self.tfLavamanos.setInputMask('000000')
        self.tfCanillaAbiertaEnjuague.setInputMask('000000')
        self.tfSecadoDeManos.setInputMask('000000')
        self.tfMensajeFinal.setInputMask('000000')
        self.tfJabon.setInputMask('000000')

    def setTiempoCanillaAbiertaInicial(self, tiempo):
        self.tfCanillaAbiertaInicial.setText(str(tiempo))

    def setTiempoLavamanos(self, tiempo):
        self.tfLavamanos.setText(str(tiempo))

    def setTiempoCanillaAbiertaEnjuague(self, tiempo):
        self.tfCanillaAbiertaEnjuague.setText(str(tiempo))

    def setTiempoSecadoDeManos(self, tiempo):
        self.tfSecadoDeManos.setText(str(tiempo))

    def setTiempoMensajeFinal(self, tiempo):
        self.tfMensajeFinal.setText(str(tiempo))

    def setTiempoJabon(self, tiempo):
        self.tfJabon.setText(str(tiempo))

    def getTiempoCanillaAbiertaInicial(self):
        return int(self.tfCanillaAbiertaInicial.text())

    def getTiempoLavamanos(self):
        return int(self.tfLavamanos.text())

    def getTiempoCanillaAbiertaEnjuague(self):
        return int(self.tfCanillaAbiertaEnjuague.text())

    def getTiempoSecadoDeManos(self):
        return int(self.tfSecadoDeManos.text())

    def getTiempoMensajeFinal(self):
        return int(self.tfMensajeFinal.text())

    def getTiempoJabon(self):
        return int(self.tfJabon.text())
