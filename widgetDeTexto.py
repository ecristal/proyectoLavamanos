from PyQt5 import uic, QtCore, QtGui, QtWidgets, QtMultimedia, QtMultimediaWidgets
import vlc
import RPi.GPIO as GPIO

widget_ui_ = uic.loadUiType("UI/widgetDeTexto.ui")[0]

class widgetDeTexto(QtWidgets.QDialog, widget_ui_):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        #self.mediaPlayer = QtMultimedia.QMediaPlayer(None,QtMultimedia.QMediaPlayer.VideoSurface)
        #self.videoWidget = QtMultimediaWidgets.QVideoWidget()
        #self.mediaPlayer.setVideoOutput(self.videoWidget)

        #self.playlist = QtMultimedia.QMediaPlaylist()

        self.videoWidget = QtWidgets.QFrame()
        self.instanciaDeVideo = vlc.Instance()
        self.mediaListPlayer = self.instanciaDeVideo.media_list_player_new()
        self.mediaPlayer = self.instanciaDeVideo.media_player_new()

        self.mediaPlayer.set_fullscreen(True)

        self.mediaListPlayer.set_media_player(self.mediaPlayer)

        self.playlist = self.instanciaDeVideo.media_list_new()
        self.listaDeReproduccion = []

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.videoWidget)
        self.setLayout(layout)

        #self.mediaPlayer.set_xwindow(self.videoWidget.winId())

        #GPIO.setmode(GPIO.BCM)
        #GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Canilla
        #GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Jabon

        #def gpio23_Interrupted(canal):
        #    print('Interrupcion en el pin 23')
        #    for i in reversed(range(self.layout().count())):
        #        self.layout().itemAt(i).widget().deleteLater()

        #def gpio24_Interrupted(canal):
        #    print('Interrupcion en el pin 24')
        #    self.mediaPlayer.stop()

        #GPIO.add_event_detect(23, GPIO.FALLING, callback=gpio23_Interrupted, bouncetime=300)
        #GPIO.add_event_detect(24, GPIO.FALLING, callback=gpio24_Interrupted, bouncetime=300)

    def setListaDeReproduccion(self,listaDeReproduccion):
        self.listaDeReproduccion = listaDeReproduccion
        for video in self.listaDeReproduccion:
            media = self.instanciaDeVideo.media_new(video)
            self.playlist.add_media(media)
            #self.playlist.addMedia(QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(video)))
        #self.playlist.setCurrentIndex(1)
        #self.mediaPlayer.setPlaylist(self.playlist)
        self.mediaListPlayer.set_media_list(self.playlist)
        self.mediaListPlayer.play()
