from PyQt5 import uic, QtCore, QtGui, QtWidgets, QtMultimedia, QtMultimediaWidgets
import RPi.GPIO as GPIO
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
        self.modeloListaDeVideos = QtGui.QStandardItemModel(self.videoListView)

        self.bAgregarVideo.clicked.connect(self.bAgregarVideoClicked)
        self.bPlay.clicked.connect(self.bPlayPressed)
        self.bPausa.clicked.connect(self.bPausaPressed)
        self.bStop.clicked.connect(self.bStopPressed)
        self.bIniciarPrograma.clicked.connect(self.bIniciarProgramaPressed)
        self.inicializarListaDeVideos()
    
    def inicializarListaDeVideos(self):
        entradaSerial = open('listaDeReproduccion.pkl','rb')
        self.listaDeVideos = pickle.load(entradaSerial)
        print(self.listaDeVideos)

    def bAgregarVideoClicked(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self,"Agregar Videos", "","All Files (*)", options=options)
        for i in range(0,len(files)):
            self.listaDeVideos.append(files[i])
            item = QtGui.QStandardItem(files[i])
            self.modeloListaDeVideos.appendRow(item)
        self.videoListView.setModel(self.modeloListaDeVideos)
        salidaSerial = open('listaDeReproduccion.pkl','wb')
        pickle.dump(self.listaDeVideos, salidaSerial)
        salidaSerial.close()

    def bPlayPressed(self):
        indiceVideo = self.videoListView.currentIndex()
        direccionVideo = indiceVideo.data(QtCore.Qt.DisplayRole)
        print(direccionVideo)
        media = self.instanciaDeVideo.media_new(direccionVideo)
        self.mediaPlayer.set_media(media)
        media.parse()
        self.mediaPlayer.set_xwindow(self.videoFrame.winId())
        #self.mediaPlayer.setMedia(QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(direccionVideo)))
        self.mediaPlayer.play()

    def bStopPressed(self):
        self.mediaPlayer.stop()

    def bPausaPressed(self):
        self.mediaPlayer.pause()

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
