# Installation
Run the following commands on Raspberry Pi terminal:
```
cd /lib/systemd/system/
sudo nano SolarManager.service
```

Copy content from SolarManager.service into terminal nano editor.
Run the following commands to install and start the service:
```
sudo chmod 644 /lib/systemd/system/SolarManager.service
chmod +x /home/pi/SolarManager/main.py
sudo systemctl daemon-reload
sudo systemctl enable SolarManager.service
sudo systemctl start SolarManager.service
```

For details see https://gist.github.com/emxsys/a507f3cad928e66f6410e7ac28e2990f
