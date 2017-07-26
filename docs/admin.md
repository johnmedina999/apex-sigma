nano /etc/systemd/system/sickle.service
systemctl daemon-reload
systemctl start sickle.service
systemctl status sickle.service
systemctl stop sickle.service
journalctl -u sickle.service




[ sickle.service ]

Description=sickle

[Service]
Type=simple
User=server
Group=server
WorkingDirectory=/home/server/discord/sigma/
ExecStart=/home/server/discord/sigma/run.sh
Restart=always
StandardOutput=sickle.log
StandardError=sickle.log

[Install]
WantedBy=multi-user.target

