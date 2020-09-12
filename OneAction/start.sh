if pgrep -x "mongod" > /dev/null
then
  systemctl status mongod
else
  sudo systemctl start mongod
fi
gunicorn -D -w 4 -b 0:5000 app:app
