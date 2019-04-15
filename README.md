![](https://raw.githubusercontent.com/joemcmanus/honeyBot/master/img/dashboard.png)
# honeyBot
A set of tools for creating a honeypot that alerts in the real world .

![](https://raw.githubusercontent.com/joemcmanus/honeyBot/master/img/light.jpg)

# Setup
This is designed around a RaspberryPi using a PiRelay Hat to raise a physical alarm. 
First we will need to make the Pi require ssh keys and  log iptables. 

    vi /etc/sshd_config
    #PasswordAuthentication yes
    PasswordAuthentication no

Then restart sshd. 

    sudo service ssh restart

Next install iptables-persistent and modify iptables. 

    apt-get install iptables-persistent

    vi /etc/iptables/rules.v4

Add the line:

    -A INPUT -m limit --limit 30/min -j LOG --log-prefix "iptables: "

There is a sample list of rules in the repo called sampleIptables, you could copy that in to place, modifying the 443 line with your subnet. 

Modify rsyslog.conf to create a iptables.log

   vi /etc/rsyslog.d/10-iptables.conf
   :msg,contains,"iptables: " /var/log/iptables.log


Restart rsyslog . 

Install a lot of prereqs: 

    apt-get install python3-rpi.gpio \
     daemonize mosquitto \
     mosquitto-clients

    pip3 paho-mqtt flask maxminddb-geolite2l \
      geopandas pyshp shapely \
      plotly  psutil



Copy the files from the repo in to /var/honeyBoy. Then move the startup scripts in to place and start


    cp startupScripts/*.service /lib/systemd/system
    systemctl enable honeyBotMon.service
    systemctl enable honeyMqtt.service
    systemctl enable honeyWeb.service


#Modular
You can deploy this on multiple systems as it was desinged to be modular. 

![](https://raw.githubusercontent.com/joemcmanus/honeyBot/master/img/honeyBot.jpg)

#honeyBotMon.py 

    usage: honeyBotMon.py [-h] [--pid] [--server SERVER] [--log] [--relay RELAY]
                          [--delay DELAY]
    
    HoneyBot Log Monitor
    
    optional arguments:
      -h, --help       show this help message and exit
      --pid            Create a pid file in /var/run/honeyBotMon.pid
      --server SERVER  Server to send alerts to, default 127.0.0.1
      --log            Create a log file in /var/log/honeyBotMon.log
      --relay RELAY    Which relay to activate, default 1
      --delay DELAY    Number of seconds to wait between readings, default 1

#honeyMqtt.py 

    usage: honeyMqtt.py [-h] [--pid] [--dbPath DBPATH]
    
    HoneyMQTT Event Monitor
    
    optional arguments:
      -h, --help       show this help message and exit
      --pid            Create a pid file in /var/run/honeyMqtt.pid
      --dbPath DBPATH  Create a sqlite db file in specified path, defaults to
                       /var/honeyBot

#honeyWeb.py 

    usage: honeyBotMon.py [-h] [--pid] [--server SERVER] [--log] [--relay RELAY]
                          [--delay DELAY]
    
    HoneyBot Log Monitor Web Front End
    
    optional arguments:
      -h, --help       show this help message and exit
      --pid            Create a pid file in /var/run/honeyBotMon.pid
      --server SERVER  Server to send alerts to, default 127.0.0.1
      --log            Create a log file in /var/log/honeyBotMon.log
      --relay RELAY    Which relay to activate, default 1
      --delay DELAY    Number of seconds to wait between readings, default 1

#Parts
I used a regular RPi and a Pi Relay Hat from Amazon: 
https://www.amazon.com/Raspberry-Pi-Expansion-Module-XYGStudy/dp/B01G05KLIE/

![](https://raw.githubusercontent.com/joemcmanus/honeyBot/master/img/relay.jpg)

