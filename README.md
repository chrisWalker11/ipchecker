you must add the following for it to work to the invite url
```
&permissions=3072&scope=bot
```
ex 
```
https://discord.com/oauth2/authorize?client_id=1234567890&permissions=3072&scope=bot
```
also for the systemd service (if you're using linux)
```
sudo vim /etc/systemd/system/<WHATEVER_NAME_YOU_WANT>.service
sudo systemctl daemon-reload
sudo systemctl enable --now <WHATEVER_NAME_YOU_WANT>
```
