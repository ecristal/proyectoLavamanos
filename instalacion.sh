sudo apt-get update 
sudo apt-get install qt5-default pyqt5-dev pyqt5-dev-tools -y
sudo apt-get install python3-pyqt5.qtmultimedia -y
#curl -s 'https://raw.githubusercontent.com/zerotier/ZeroTierOne/master/doc/contact%40zerotier.com.gpg' | gpg --import && \
#if z=$(curl -s 'https://install.zerotier.com/' | gpg); then echo "$z" | sudo bash; fi
#sudo systemctl enable zerotier-one
#sudo zerotier-cli join a84ac5c10aacc8bc
sudo apt-get install vino -y
sudo gsettings set org.gnome.Vino require-encryption false
sudo gsettings set org.gnome.Vino prompt-enabled false
sudo gsettings set org.gnome.Vino authentication-methods "['none']"
touch vsrv.sh
echo "#! /bin/bash" | tee -a vsrv.sh
echo "/usr/lib/vino/vino-server" | tee -a vsrv.sh
sudo chmod +x vsrv.sh
sudo mv vsrv.sh /etc/sudoers.d/
sudo echo "@/etc/sudoers.d/vsrv.sh" | sudo tee -a /etc/xdg/lxsession/LXDE/autostart 
