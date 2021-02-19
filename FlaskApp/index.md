# gustav web server
A simple Python web server with a lightweight frontend to run psychoacoustics experiments.
Requires Python >= 3.7

## Usage
```
cd FlaskApp
python app.py
```
Go to your browser and open `0.0.0.0:5000`.

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

```
