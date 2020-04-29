from PyQt5 import uic, QtCore, QtGui, QtWidgets, QtMultimedia, QtMultimediaWidgets
import vlc
import RPi.GPIO as GPIO

widget_ui_ = uic.loadUiType("/home/pi/proyectoLavamanos/UI/widgetDeTexto.ui")[0]

class widgetDeTexto(QtWidgets.QDialog, widget_ui_):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)

        self.ejecutarSinPublicidad = False

        self.widgetReproductorDePublicidad = QtWidgets.QWidget()

        #self.mediaPlayer = QtMultimedia.QMediaPlayer(None,QtMultimedia.QMediaPlayer.VideoSurface)
        #self.videoWidget = QtMultimediaWidgets.QVideoWidget()
        #self.mediaPlayer.setVideoOutput(self.videoWidget)

        #self.playlist = QtMultimedia.QMediaPlaylist()

        self.texto = QtWidgets.QLabel()
        self.texto.setFixedHeight(300)
        self.texto.setFixedWidth(2000)
        self.texto.setText("Que tenga un buen dia.")
        font = QtGui.QFont("Arial",120)
        self.texto.setFont(font)
        self.texto.setAlignment(QtCore.Qt.AlignCenter)
        self.videoFrame = QtWidgets.QFrame()
        self.instanciaDeVideo = vlc.Instance()
        #self.instanciaDeVideoPublicidad = vlc.Instance()
        self.mediaListPlayer = self.instanciaDeVideo.media_list_player_new()
        self.mediaPlayer = self.instanciaDeVideo.media_player_new()
        self.mediaPlayerLavamanos = self.instanciaDeVideo.media_player_new()

        self.mediaListPlayer.set_playback_mode(vlc.PlaybackMode.loop)

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
        self.mediaPlayer.set_xwindow(self.widgetReproductorDePublicidad.winId())

        self.timerInicioDeSecuenciaLavado = QtCore.QTimer()
        self.timerInicioDeSecuenciaLavado.timeout.connect(self.timeoutTimerInicioDeSecuencia)

        self.timerUnSegundoLavado = QtCore.QTimer()
        self.timerUnSegundoLavado.timeout.connect(self.timeoutTimerUnSegundoLavado)
        self.contadorUnSegundoLavado = 0

        self.timerInicioDeEnjuague = QtCore.QTimer() # esto crea el timer llamano timeriniciodenjuague
        self.timerInicioDeEnjuague.timeout.connect(self.timeoutTimerInicioDeEnjuague) ## conecta la senha .timeout a timerenjuague

        self.timerMensajeFinal = QtCore.QTimer()
        self.timerMensajeFinal.timeout.connect(self.timeoutTimerMensajeFinal)

        self.timerFinLavado = QtCore.QTimer()
        self.timerFinLavado.timeout.connect(self.timeoutTimerFinLavado)

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

        self.setWindowState(QtCore.Qt.WindowMinimized)

        GPIO.setmode(GPIO.BCM)
        #GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Canilla
        GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP) # Jabon entrada
        GPIO.setup(8, GPIO.IN, pull_up_down = GPIO.PUD_UP) # Agua entrada
        GPIO.setup(24, GPIO.OUT) # Jabon salida
        GPIO.setup(25, GPIO.OUT) # salida de agua

        GPIO.output(24,GPIO.HIGH)
        GPIO.output(25,GPIO.HIGH)

        self.tiempoCanillaAbiertaInicial = 0
        self.tiempoLavamanos = 0
        self.tiempoCanillaAbiertaEnjuague = 0
        self.tiempoSecadoDeManos = 0
        self.tiempoMensajeFinal = 0
        self.tiempoJabon = 0

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

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
            #self.mediaListPlayer.pause()
            self.pauseMediaListPlayer()
            self.setWindowState(QtCore.Qt.WindowFullScreen)
        if ((not GPIO.input(23)) and self.banderaEjecucionSecuenciaDispensarJabon == 0):
            GPIO.output(24,GPIO.LOW)
            self.banderaEjecucionSecuenciaDispensarJabon = 1
            self.timerDispensandoJabon.start(self.tiempoJabon)

    def timeoutTimerCheckSensorAgua(self):
        if ((not GPIO.input(8)) and self.banderaEjecucionSecuenciaLavado == 0):
            self.banderaEjecucionSecuenciaLavado = 1
            self.inicioDeSecuenciaDeLavado()
            #self.mediaListPlayer.pause()
            self.pauseMediaListPlayer()
            self.setWindowState(QtCore.Qt.WindowFullScreen)

    def timeoutTimerDispensandoJabon(self):
        GPIO.output(24,GPIO.HIGH)
        self.timerDispensandoJabon.stop()
        self.banderaEjecucionSecuenciaDispensarJabon = 0

    def inicioDeSecuenciaDeLavado(self):
        self.mediaPlayerLavamanos.play()
        self.texto.setText("La OMS recomienda un lavado especial de manos.\nSu duracion es de 35 segundos")
        font = QtGui.QFont("Arial",50)
        self.texto.setFont(font)
        self.texto.setAlignment(QtCore.Qt.AlignCenter)
        GPIO.output(25,GPIO.LOW)
        self.timerInicioDeSecuenciaLavado.start(self.tiempoCanillaAbiertaInicial)
        self.mediaPlayerLavamanos.pause()

    def timeoutTimerInicioDeSecuencia(self):
        GPIO.output(25,GPIO.HIGH)
        self.timerInicioDeSecuenciaLavado.stop()
        self.media = self.instanciaDeVideo.media_new(self.listaDeReproduccion[0])
        self.mediaPlayerLavamanos.set_media(self.media)
        self.mediaPlayerLavamanos.pause()
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
        if (self.contadorUnSegundoLavado > int(self.tiempoLavamanos/1000)):
            self.timerUnSegundoLavado.stop()
            self.timerInicioDeEnjuague.start(self.tiempoCanillaAbiertaEnjuague)
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
        self.timerMensajeFinal.start(self.tiempoSecadoDeManos)

    def timeoutTimerMensajeFinal(self):
        self.timerMensajeFinal.stop()
        self.texto.setText("Que tenga un buen dia.")
        font = QtGui.QFont("Arial",120)
        self.texto.setFont(font)
        self.texto.setAlignment(QtCore.Qt.AlignCenter)
        self.banderaEjecucionSecuenciaLavado = 0
        self.timerFinLavado.start(self.tiempoMensajeFinal)

    def timeoutTimerFinLavado(self):
        self.timerFinLavado.stop()
        if(not self.ejecutarSinPublicidad):
            self.setWindowState(QtCore.Qt.WindowMinimized)
        #self.mediaListPlayer.pause()
        self.pauseMediaListPlayer()

    def setListaDeReproduccion(self,listaDeReproduccion):
        self.listaDeReproduccion = listaDeReproduccion
        self.media = self.instanciaDeVideo.media_new(self.listaDeReproduccion[0])
        self.mediaPlayerLavamanos.set_media(self.media)
        #self.mediaPlayerLavamanos.play()
        #self.mediaPlayerLavamanos.pause()
        #self.inicioDeSecuenciaDeLavado()
        for i in range(1,len(self.listaDeReproduccion)):
            self.media = self.instanciaDeVideo.media_new(self.listaDeReproduccion[i])
            self.playlist.add_media(self.media)
            #self.playlist.addMedia(QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(video)))
        #self.playlist.setCurrentIndex(1)
        #self.mediaPlayer.setPlaylist(self.playlist)
        self.mediaListPlayer.set_media_list(self.playlist)
        #self.mediaListPlayer.play()
        self.playMediaListPlayer()

    def setEjecutarSinPublicidad(self, ejecutarSinPublicidad):
        self.ejecutarSinPublicidad = ejecutarSinPublicidad
        self.checkIniciarSinPublicidad()

    def checkIniciarSinPublicidad(self):
        if(self.ejecutarSinPublicidad):
            self.showFullScreen()
        else:
            self.showMinimized()
            self.widgetReproductorDePublicidad.showFullScreen()

    def playMediaListPlayer(self):
        if(not self.ejecutarSinPublicidad):
            self.mediaListPlayer.play()

    def pauseMediaListPlayer(self):
        if(not self.ejecutarSinPublicidad):
            self.mediaListPlayer.pause()

    def setTiemposDeCiclo(self, tiempoCanillaAbiertaInicial, tiempoLavamanos, tiempoCanillaAbiertaEnjuague, tiempoSecadoDeManos, tiempoMensajeFinal, tiempoJabon):
        self.tiempoCanillaAbiertaInicial = tiempoCanillaAbiertaInicial
        self.tiempoLavamanos = tiempoLavamanos
        self.tiempoCanillaAbiertaEnjuague = tiempoCanillaAbiertaEnjuague
        self.tiempoSecadoDeManos = tiempoSecadoDeManos
        self.tiempoMensajeFinal = tiempoMensajeFinal
        self.tiempoJabon = tiempoJabon

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            #GPIO.cleanup()
            self.mediaListPlayer.stop()
            self.mediaPlayerLavamanos.stop()
            self.accept()
