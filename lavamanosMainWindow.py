from PyQt5 import uic, QtCore, QtGui, QtWidgets, QtMultimedia, QtMultimediaWidgets
import RPi.GPIO as GPIO
from os import path
from widgetDeTexto import widgetDeTexto
from dialogOpciones import dialogOpciones
import vlc
import pickle

mainWindow = uic.loadUiType("/home/pi/proyectoLavamanos/UI/mainwindow.ui")[0]

class lavamanosMainWindow(QtWidgets.QMainWindow, mainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.setWindowTitle('Programa de Lavamanos Automatico')
        self.directorioDeAplicacion = '/home/pi/proyectoLavamanos'

        #self.mediaPlayer = QtMultimedia.QMediaPlayer(None,QtMultimedia.QMediaPlayer.VideoSurface)
        self.videoWidget = QtWidgets.QFrame()
        #self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.instanciaDeVideo = vlc.Instance()
        self.mediaPlayer = self.instanciaDeVideo.media_player_new()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.videoWidget)
        self.videoFrame.setLayout(layout)

        self.listaDeVideos = []
        self.modeloListaDeVideos = QtGui.QStandardItemModel()
        self.videoListView.setModel(self.modeloListaDeVideos)
        self.videoListView.clicked.connect(self.videoListViewClicked)

        self.cbAutoInicio.stateChanged.connect(self.cbAutoInicioStateChanged)
        self.cbIniciarSinPublicidad.stateChanged.connect(self.cbIniciarSinPublicidadStateChanged)

        self.bAgregarVideo.clicked.connect(self.bAgregarVideoClicked)
        self.bEliminarVideo.clicked.connect(self.bEliminarVideoClicked)
        self.bPlay.clicked.connect(self.bPlayPressed)
        self.bStop.clicked.connect(self.bStopPressed)
        self.bIniciarPrograma.clicked.connect(self.bIniciarProgramaPressed)

        self.timerInicioAutomatico = QtCore.QTimer()
        self.timerInicioAutomatico.timeout.connect(self.timeoutTimerInicioAutomatico)

        self.banderaMediaPlayerPlay = False
        self.banderaMediaPlayerPause = False

        self.bPlay.setText('')
        self.bStop.setText('')

        self.playIcon = QtGui.QIcon(QtGui.QPixmap(self.directorioDeAplicacion + '/recursos/play_icono.png'))
        self.pausaIcon = QtGui.QIcon(QtGui.QPixmap(self.directorioDeAplicacion + '/recursos/pausa_icono.png'))
        self.stopIcon = QtGui.QIcon(QtGui.QPixmap(self.directorioDeAplicacion + '/recursos/stop_icono.png'))

        self.bPlay.setIcon(self.playIcon)
        self.bStop.setIcon(self.stopIcon)

        self.bPlay.setEnabled(False)
        self.bStop.setEnabled(False)

        self.tiempoCanillaAbiertaInicial = 0
        self.tiempoLavamanos = 0
        self.tiempoCanillaAbiertaEnjuague = 0
        self.tiempoSecadoDeManos = 0
        self.tiempoMensajeFinal = 0
        self.tiempoJabon = 0

        self.mediaPlayer.set_xwindow(self.videoFrame.winId())

        self.configurarBarraDeMenu()
        self.configurarTiempoInicialesDefault()
        self.inicializarListaDeVideos()
        self.inicializarListViewDeVideos()
        self.checkIniciarSinPublicidadHabilitado()
        self.checkAutoInicioHabilitado()

    def inicializarListaDeVideos(self):
        if(path.exists("/home/pi/proyectoLavamanos/datos/listaDeReproduccion.pkl")):
            entradaSerial = open('/home/pi/proyectoLavamanos/datos/listaDeReproduccion.pkl','rb')
            self.listaDeVideos = pickle.load(entradaSerial)

    def inicializarListViewDeVideos(self):
        self.bEliminarVideo.setEnabled(False)
        for video in self.listaDeVideos:
            item = QtGui.QStandardItem(video)
            item.setEditable(False)
            self.modeloListaDeVideos.appendRow(item)
        if(self.modeloListaDeVideos.rowCount() == 0):
            self.bIniciarPrograma.setEnabled(False)
            self.cbIniciarSinPublicidad.setEnabled(False)
        if(self.modeloListaDeVideos.rowCount() == 1):
            self.bIniciarPrograma.setEnabled(True)
            self.cbIniciarSinPublicidad.setEnabled(False)

    def bAgregarVideoClicked(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self,"Agregar Videos", "","All Files (*)", options=options)
        for i in range(0,len(files)):
            self.listaDeVideos.append(files[i])
            item = QtGui.QStandardItem(files[i])
            item.setEditable(False)
            self.modeloListaDeVideos.appendRow(item)
        if(self.modeloListaDeVideos.rowCount() >= 2):
            self.cbIniciarSinPublicidad.setEnabled(True)
            self.bIniciarPrograma.setEnabled(True)
            self.cbIniciarSinPublicidad.setChecked(False)
        salidaSerial = open('/home/pi/proyectoLavamanos/datos/listaDeReproduccion.pkl','wb')
        pickle.dump(self.listaDeVideos, salidaSerial)
        salidaSerial.close()

    def bEliminarVideoClicked(self):
        self.mediaPlayer.stop()
        self.bPlay.setIcon(self.playIcon)
        self.banderaMediaPlayerPlay = False
        if(self.modeloListaDeVideos.rowCount() == 1):
            self.bEliminarVideo.setEnabled(False)
            self.bIniciarPrograma.setEnabled(False)
            self.bPlay.setEnabled(False)
            self.bStop.setEnabled(False)
        if(self.modeloListaDeVideos.rowCount() == 2):
            self.cbIniciarSinPublicidad.setEnabled(False)
            self.cbIniciarSinPublicidad.setChecked(True)
        indice = self.videoListView.currentIndex()
        self.listaDeVideos.pop(indice.row())
        self.modeloListaDeVideos.removeRow(indice.row())
        salidaSerial = open('/home/pi/proyectoLavamanos/datos/listaDeReproduccion.pkl','wb')
        pickle.dump(self.listaDeVideos, salidaSerial)
        salidaSerial.close()

    def videoListViewClicked(self):
        indice = self.videoListView.currentIndex()
        if (indice.row()>-1):
            self.mediaPlayer.stop()
            self.bEliminarVideo.setEnabled(True)
            self.bPlay.setEnabled(True)
            self.bStop.setEnabled(True)
            self.bPlay.setIcon(self.playIcon)
            self.banderaMediaPlayerPlay = False

    def bPlayPressed(self):
        indice = self.videoListView.currentIndex()
        if(not self.banderaMediaPlayerPlay):
            direccionVideo = indice.data(QtCore.Qt.DisplayRole)
            print(direccionVideo)
            media = self.instanciaDeVideo.media_new(direccionVideo)
            self.mediaPlayer.set_media(media)
            self.mediaPlayer.play()
            self.banderaMediaPlayerPlay = True
            self.banderaMediaPlayerPause = True
            self.bPlay.setIcon(self.pausaIcon)
        else:
            self.mediaPlayer.pause()
            if(not self.banderaMediaPlayerPause):
                self.bPlay.setIcon(self.pausaIcon)
            else:
                self.bPlay.setIcon(self.playIcon)
            self.banderaMediaPlayerPause = not self.banderaMediaPlayerPause

    def bStopPressed(self):
        self.mediaPlayer.stop()
        self.bPlay.setIcon(self.playIcon)
        self.banderaMediaPlayerPlay = False
        self.banderaMediaPlayerPause = False

    def checkAutoInicioHabilitado(self):
        if(path.exists("/home/pi/proyectoLavamanos/datos/cbAutoInicio.pkl")):
            entradaSerial = open('/home/pi/proyectoLavamanos/datos/cbAutoInicio.pkl','rb')
            self.cbAutoInicio.setChecked(pickle.load(entradaSerial))
        if(self.cbAutoInicio.isChecked() and self.modeloListaDeVideos.rowCount() >= 1):
            print('autoinicio')
            self.timerInicioAutomatico.start(5000)

    def cbAutoInicioStateChanged(self):
        salidaSerial = open('/home/pi/proyectoLavamanos/datos/cbAutoInicio.pkl','wb')
        pickle.dump(self.cbAutoInicio.isChecked(), salidaSerial)
        salidaSerial.close()

    def checkIniciarSinPublicidadHabilitado(self):
        if(path.exists("/home/pi/proyectoLavamanos/datos/cbIniciarSinPublicidad.pkl")):
            entradaSerial = open('/home/pi/proyectoLavamanos/datos/cbIniciarSinPublicidad.pkl','rb')
            self.cbIniciarSinPublicidad.setChecked(pickle.load(entradaSerial))

    def cbIniciarSinPublicidadStateChanged(self):
        print(self.cbIniciarSinPublicidad.isChecked())
        salidaSerial = open('/home/pi/proyectoLavamanos/datos/cbIniciarSinPublicidad.pkl','wb')
        pickle.dump(self.cbIniciarSinPublicidad.isChecked(), salidaSerial)
        salidaSerial.close()

    def bIniciarProgramaPressed(self):
        print('bIniciarProgramaPressed')
        self.mediaPlayer.stop()
        dialogDeMensajes = widgetDeTexto(self)
        dialogDeMensajes.setTiemposDeCiclo(self.tiempoCanillaAbiertaInicial, self.tiempoLavamanos, self.tiempoCanillaAbiertaEnjuague, self.tiempoSecadoDeManos, self.tiempoMensajeFinal, self.tiempoJabon)
        dialogDeMensajes.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowType_Mask)
        #dialogDeMensajes.showMinimized()
        #dialogDeMensajes.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        dialogDeMensajes.setEjecutarSinPublicidad(self.cbIniciarSinPublicidad.isChecked())
        dialogDeMensajes.setListaDeReproduccion(self.listaDeVideos)
        #dialogDeMensajes.showMinimized()
        QtGui.QGuiApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))
        dialogDeMensajes.exec_()
        QtGui.QGuiApplication.restoreOverrideCursor()
        GPIO.cleanup()

    def configurarBarraDeMenu(self):
        menuHerramientas = self.menuBar().addMenu('&Herramientas')
        accionAbrirOpciones = QtWidgets.QAction('Configuracion',self)
        accionAbrirOpciones.triggered.connect(self.menuAbrirOpcionesTriggered)
        menuHerramientas.addAction(accionAbrirOpciones)

    def configurarTiempoInicialesDefault(self):
        self.tiempoCanillaAbiertaInicial = 6000
        self.tiempoLavamanos = 35000
        self.tiempoCanillaAbiertaEnjuague = 10000
        self.tiempoSecadoDeManos = 5000
        self.tiempoMensajeFinal = 3000
        self.tiempoJabon = 2000

    def menuAbrirOpcionesTriggered(self):
        dialogDeOpciones = dialogOpciones(self)
        dialogDeOpciones.setTiempoCanillaAbiertaInicial(self.tiempoCanillaAbiertaInicial)
        dialogDeOpciones.setTiempoLavamanos(self.tiempoLavamanos)
        dialogDeOpciones.setTiempoCanillaAbiertaEnjuague(self.tiempoCanillaAbiertaEnjuague)
        dialogDeOpciones.setTiempoSecadoDeManos(self.tiempoSecadoDeManos)
        dialogDeOpciones.setTiempoMensajeFinal(self.tiempoMensajeFinal)
        dialogDeOpciones.setTiempoJabon(self.tiempoJabon)
        caso = dialogDeOpciones.exec_()
        if (caso):
            self.tiempoCanillaAbiertaInicial = dialogDeOpciones.getTiempoCanillaAbiertaInicial()
            print(self.tiempoCanillaAbiertaInicial)
            self.tiempoLavamanos = dialogDeOpciones.getTiempoLavamanos()
            print(self.tiempoLavamanos)
            self.tiempoCanillaAbiertaEnjuague = dialogDeOpciones.getTiempoCanillaAbiertaEnjuague()
            print(self.tiempoCanillaAbiertaEnjuague)
            self.tiempoSecadoDeManos = dialogDeOpciones.getTiempoSecadoDeManos()
            print(self.tiempoSecadoDeManos)
            self.tiempoMensajeFinal = dialogDeOpciones.getTiempoMensajeFinal()
            print(self.tiempoMensajeFinal)
            self.tiempoJabon = dialogDeOpciones.getTiempoJabon()
            print(self.tiempoJabon)
        else:
            print('continue')

    def timeoutTimerInicioAutomatico(self):
        self.timerInicioAutomatico.stop()
        self.bIniciarProgramaPressed()

    #def keyPressEvent(self, event):
    #    if (event.key() == QtCore.Qt.Key_Escape) and (self.videoWidget.isFullScreen() == False):
    #        print('HOLA')
    #        self.videoWidget.setFullScreen(False)
    #        event.accept()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = lavamanosMainWindow()
    MainWindow.show()
    sys.exit(app.exec_())
