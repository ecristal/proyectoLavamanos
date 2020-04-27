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

        self.texto = QtWidgets.QLabel()
        self.texto.setFixedHeight(300)
        self.texto.setFixedWidth(2000)
        self.texto.setText('HOLA MUNDO')
        font = QtGui.QFont('Arial',200)
        self.texto.setFont(font)
        self.videoFrame = QtWidgets.QFrame()
        self.instanciaDeVideo = vlc.Instance()
        self.mediaListPlayer = self.instanciaDeVideo.media_list_player_new()
        self.mediaPlayer = self.instanciaDeVideo.media_player_new()
        self.mediaPlayerLavamanos = self.instanciaDeVideo.media_player_new()

        self.mediaPlayer.set_fullscreen(True)

        self.mediaListPlayer.set_media_player(self.mediaPlayer)

        self.playlist = self.instanciaDeVideo.media_list_new()
        self.listaDeReproduccion = []

        layoutH = QtWidgets.QHBoxLayout()
        layoutH.addWidget(self.texto)

        layoutH2 = QtWidgets.QHBoxLayout()
        layoutH2.addWidget(self.videoFrame)

        layoutV = QtWidgets.QVBoxLayout()
        layoutV.addLayout(layoutH2)
        layoutV.addLayout(layoutH)

        self.media = ""

        #layoutV.setAlignment(QtCore.Qt.AlignBottom)

        self.setLayout(layoutV)

        self.mediaPlayerLavamanos.set_xwindow(self.videoFrame.winId())

        self.timerInicioDeSecuenciaLavado = QtCore.QTimer()
        self.timerInicioDeSecuenciaLavado.timeout.connect(self.timeoutTimerInicioDeSecuencia)

        self.timerUnSegundoLavado = QtCore.QTimer()
        self.timerUnSegundoLavado.timeout.connect(self.timeoutTimerUnSegundoLavado)
        self.contadorUnSegundoLavado = 0


        self.timerInicioDeEnjuague = QtCore.QTimer() # esto crea el timer llamano timeriniciodenjuague
        self.timerInicioDeEnjuague.timeout.connect(self.timeoutTimerInicioDeEnjuague) ## conecta la senha .timeout a timerenjuague

        self.timerMensajeFinal = QtCore.QTimer()
        self.timerMensajeFinal.timeout.connect(self.timeoutTimerMensajeFinal)

        self.timerCheckSensorJabon = QtCore.QTimer()
        self.timerCheckSensorJabon.timeout.connect(self.timeoutTimerCheckSensorJabon)
        self.timerCheckSensorJabon.start(250)

        self.timerCheckSensorAgua = QtCore.QTimer()
        self.timerCheckSensorAgua.timeout.connect(self.timeoutTimerCheckSensorAgua)
        self.timerCheckSensorAgua.start(250)

        self.banderaEjecucionSecuenciaLavado = 0
        self.banderaEjecucionSecuenciaDispensarJabon = 0

        self.timerDispensandoJabon = QtCore.QTimer()
        self.timerDispensandoJabon.timeout.connect(self.timeoutTimerDispensandoJabon)



        GPIO.setmode(GPIO.BCM)
        #GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Canilla
        GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP) # Jabon entrada
        GPIO.setup(8, GPIO.IN, pull_up_down = GPIO.PUD_UP) # Agua entrada
        GPIO.setup(24, GPIO.OUT) # Jabon salida
        GPIO.setup(25, GPIO.OUT) # salida de agua

        GPIO.output(24,GPIO.HIGH)
        GPIO.output(25,GPIO.HIGH)

        #def gpio23_Interrupted(canal):
        #    print('Interrupcion en el pin 23')
        #    for i in reversed(range(self.layout().count())):
        #        self.layout().itemAt(i).widget().deleteLater()

        #def gpio24_Interrupted(canal):
        #    print('Interrupcion en el pin 24')
        #    self.mediaPlayer.stop()

        #GPIO.add_event_detect(23, GPIO.FALLING, callback=gpio23_Interrupted, bouncetime=300)
        #GPIO.add_event_detect(24, GPIO.FALLING, callback=gpio24_Interrupted, bouncetime=300)
    def timeoutTimerCheckSensorJabon(self):
        if ((not GPIO.input(23)) and self.banderaEjecucionSecuenciaLavado == 0):
            self.banderaEjecucionSecuenciaLavado = 1
            self.inicioDeSecuenciaDeLavado()
        if ((not GPIO.input(23)) and self.banderaEjecucionSecuenciaDispensarJabon == 0):
             GPIO.output(24,GPIO.LOW)
             self.banderaEjecucionSecuenciaDispensarJabon = 1
             self.timerDispensandoJabon.start(2000)

    def timeoutTimerCheckSensorAgua(self):
        if ((not GPIO.input(8)) and self.banderaEjecucionSecuenciaLavado == 0):
            self.banderaEjecucionSecuenciaLavado = 1
            self.inicioDeSecuenciaDeLavado()

    def timeoutTimerDispensandoJabon(self):
        GPIO.output(24,GPIO.HIGH)
        self.timerDispensandoJabon.stop()
        self.banderaEjecucionSecuenciaDispensarJabon = 0

    def inicioDeSecuenciaDeLavado(self):
        self.texto.setText("La OMS recomienda un lavado especial de manos.\nSu duracion es de 35 segundos")
        font = QtGui.QFont("Arial",50)
        self.texto.setFont(font)
        self.texto.setAlignment(QtCore.Qt.AlignCenter)
        GPIO.output(25,GPIO.LOW)
        self.timerInicioDeSecuenciaLavado.start(6000)

    def timeoutTimerInicioDeSecuencia(self):
        GPIO.output(25,GPIO.HIGH)
        self.timerInicioDeSecuenciaLavado.stop()
        self.media = self.instanciaDeVideo.media_new(self.listaDeReproduccion[0])
        self.mediaPlayerLavamanos.set_media(self.media)
        self.mediaPlayerLavamanos.play()
        self.texto.setText("0")
        font = QtGui.QFont("Arial",200)
        self.texto.setFont(font)
        self.texto.setAlignment(QtCore.Qt.AlignCenter)
        self.timerUnSegundoLavado.start(1000)

    def timeoutTimerUnSegundoLavado(self):
        self.contadorUnSegundoLavado = self.contadorUnSegundoLavado + 1
        self.texto.setText(str(self.contadorUnSegundoLavado))
        font = QtGui.QFont("Arial",200)
        self.texto.setFont(font)
        self.texto.setAlignment(QtCore.Qt.AlignCenter)
        if (self.contadorUnSegundoLavado > 35):
            self.timerUnSegundoLavado.stop()
            self.timerInicioDeEnjuague.start(10000)
            self.texto.setText("Puede enjuagarse las manos")
            font = QtGui.QFont("Arial",100)
            self.texto.setFont(font)
            self.texto.setAlignment(QtCore.Qt.AlignCenter)
            self.contadorUnSegundoLavado = 0
            GPIO.output(25,GPIO.LOW)

    def timeoutTimerInicioDeEnjuague(self):
        self.timerInicioDeEnjuague.stop()
        GPIO.output(25,GPIO.HIGH)
        self.texto.setText("No olvide secarse las manos.\nGracias por colaborar")
        font = QtGui.QFont("Arial",50)
        self.texto.setFont(font)
        self.texto.setAlignment(QtCore.Qt.AlignCenter)
        self.timerMensajeFinal.start(5000)

    def timeoutTimerMensajeFinal(self):
        self.timerMensajeFinal.stop()
        self.texto.setText("Que tenga un buen dia.")
        font = QtGui.QFont("Arial",120)
        self.texto.setFont(font)
        self.texto.setAlignment(QtCore.Qt.AlignCenter)
        self.banderaEjecucionSecuenciaLavado = 0
        self.mediaListPlayer.play()

    def setListaDeReproduccion(self,listaDeReproduccion):
        self.listaDeReproduccion = listaDeReproduccion
        self.media = self.instanciaDeVideo.media_new(self.listaDeReproduccion[0])
        self.mediaPlayerLavamanos.set_media(self.media)
        #self.mediaPlayerLavamanos.play()
        #self.mediaPlayerLavamanos.pause()
        #self.inicioDeSecuenciaDeLavado()
        i = 0
        for video in self.listaDeReproduccion:
            if(i != 0):
                self.media = self.instanciaDeVideo.media_new(video)
                self.playlist.add_media(self.media)
                i = i + 1
                #self.playlist.addMedia(QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(video)))
        #self.playlist.setCurrentIndex(1)
        #self.mediaPlayer.setPlaylist(self.playlist)
        self.mediaListPlayer.set_media_list(self.playlist)
        #self.mediaListPlayer.play()
