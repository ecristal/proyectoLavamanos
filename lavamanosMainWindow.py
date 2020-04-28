from PyQt5 import uic, QtCore, QtGui, QtWidgets, QtMultimedia, QtMultimediaWidgets
import RPi.GPIO as GPIO
from os import path
from widgetDeTexto import widgetDeTexto
import vlc
import pickle

mainWindow = uic.loadUiType("/home/pi/proyectoLavamanos/UI/mainwindow.ui")[0]

class lavamanosMainWindow(QtWidgets.QMainWindow, mainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

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

        self.bAgregarVideo.clicked.connect(self.bAgregarVideoClicked)
        self.bEliminarVideo.clicked.connect(self.bEliminarVideoClicked)
        self.bPlay.clicked.connect(self.bPlayPressed)
        self.bStop.clicked.connect(self.bStopPressed)
        self.bIniciarPrograma.clicked.connect(self.bIniciarProgramaPressed)

        self.inicializarListaDeVideos()
        self.inicializarListViewDeVideos()
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

    def bAgregarVideoClicked(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self,"Agregar Videos", "","All Files (*)", options=options)
        for i in range(0,len(files)):
            self.listaDeVideos.append(files[i])
            item = QtGui.QStandardItem(files[i])
            item.setEditable(False)
            self.modeloListaDeVideos.appendRow(item)
        salidaSerial = open('/home/pi/proyectoLavamanos/datos/listaDeReproduccion.pkl','wb')
        pickle.dump(self.listaDeVideos, salidaSerial)
        salidaSerial.close()

    def bEliminarVideoClicked(self):
        if(self.modeloListaDeVideos.rowCount() == 1):
            self.bEliminarVideo.setEnabled(False)
        indice = self.videoListView.currentIndex()
        self.listaDeVideos.pop(indice.row())
        self.modeloListaDeVideos.removeRow(indice.row())
        salidaSerial = open('/home/pi/proyectoLavamanos/datos/listaDeReproduccion.pkl','wb')
        pickle.dump(self.listaDeVideos, salidaSerial)
        salidaSerial.close()

    def videoListViewClicked(self):
        indice = self.videoListView.currentIndex()
        if (indice.row()>-1):
            self.bEliminarVideo.setEnabled(True)

    def bPlayPressed(self):
        if(self.mediaPlayer.is_playing() and self.banderaMediaPlayerPlay):
            self.mediaPlayer.pause()
        else:
            indiceVideo = self.videoListView.currentIndex()
            direccionVideo = indiceVideo.data(QtCore.Qt.DisplayRole)
            print(direccionVideo)
            media = self.instanciaDeVideo.media_new(direccionVideo)
            self.mediaPlayer.set_media(media)
            media.parse()
            self.mediaPlayer.set_xwindow(self.videoFrame.winId())
            #self.mediaPlayer.setMedia(QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(direccionVideo)))
            self.mediaPlayer.play()
            self.banderaMediaPlayerPlay = True

    def bStopPressed(self):
        self.mediaPlayer.stop()

    def checkAutoInicioHabilitado(self):
        if(path.exists("/home/pi/proyectoLavamanos/datos/cbAutoInicio.pkl")):
            entradaSerial = open('/home/pi/proyectoLavamanos/datos/cbAutoInicio.pkl','rb')
            self.cbAutoInicio.setChecked(pickle.load(entradaSerial))
        if(self.cbAutoInicio.isChecked()):
            print('autoinicio')
            self.bIniciarProgramaPressed()

    def cbAutoInicioStateChanged(self):
        salidaSerial = open('/home/pi/proyectoLavamanos/datos/cbAutoInicio.pkl','wb')
        pickle.dump(self.cbAutoInicio.isChecked(), salidaSerial)
        salidaSerial.close()

    def bIniciarProgramaPressed(self):
        print('bIniciarProgramaPressed')
        self.mediaPlayer.stop()
        dialogDeMensajes = widgetDeTexto(self)
        dialogDeMensajes.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowType_Mask)
        #dialogDeMensajes.showMinimized()
        #dialogDeMensajes.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        dialogDeMensajes.setListaDeReproduccion(self.listaDeVideos)
        dialogDeMensajes.showMinimized()
        dialogDeMensajes.exec_()
        GPIO.cleanup()
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
