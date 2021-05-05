# gustav web server
A simple Python web server with a lightweight frontend to run psychoacoustics experiments.
Requires Python >= 3.7

## Usage

### RPI Server

Connect to the server and start `tmux`
```
# ssh in to the server
ssh kutay@74.109.252.140

# load the tmux session
tmux a
# if no sessions are available create a new one
tmux
```

Create as many `tmux` tabs tab as you need and run `app.py` from each
- create new tab `ctrl + b + c`
- navigate to a specific tab (with numeric index): `ctrl + b + <num>`

To run the main server:
```
cd gustav/FlaskApp
python app.py
```

To run an experiment server:
```
cd gustav/FlaskApp
python app.py --port 5051
```

### Local
To run the main server
```
cd gustav/FlaskApp
python app.py --local
```
Go to your browser and open `0.0.0.0:5050`.

To run an experiment server open a new terminal window and run:
```
cd gustav/FlaskApp
python app.py --local --port 5051
```

## Server Installations

```
# install apache
sudo apt-get install apache2
sudo apt-get install libapache2-mod-wsgi-py3

# distutils was missing for some reason
sudo apt-get install python3-distutils

# and also pip was missing
sudo apt get install curl
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo python3 get-pip.py

# install requirements (flask, requests)
sudo pip3 install flask requests numpy

sudo apt-get install libasound-dev
# Install psylab
# Install gustav

# install git
sudo apt install git

# clone gustav and run the server
git clone https://github.com/kbsezginel/gustav.git
cd gustav/FlaskApp
python3 app.py

# Install pysoundfile
conda install cffi numpy
pip install pysoundfile
sudo apt-get install libsndfile1

```

## Raspberry PI Setup

```
sudo pacman -S gcc tmux python-pip python-numpy python-scipy python-flask python-requests python-matplotlib python-pandas
sudo pacman -S fakeroot binutils make cmake patch yay python-wheel tk micro xclip mc

pip install soundfile
pip install git+https://github.com/cbrown1/psylab

# Install gustav
cd ~
git clone https://github.com/kbsezginel/gustav
cd gustav
pip install -e .

# Run app.py on startup
echo "[Desktop Entry]
name=Start gustav_web
Comment=Gustav main page
Exec=./home/gustav/FlaskApp/start.sh
Type=Application
Categories=Accessory;
StartupNotify=true" > gustav_web.desktop

cp gustav_web.desktop ~/.config/autostart

# Setup auto login
sudo cp /etc/lightdm/lightdm.conf /etc/lightdm/lightdm.conf.bak
sudo sed -i
's/\[Seat:\*\]/[Seat:\*]\nautologin-guest=false\nautologin-user=$USER\nautologin-user-timeout=0\n'
/etc/lightdm/lightdm.conf
sudo groupadd -r autologin
sudo gpasswd -a $USER autologin
```
