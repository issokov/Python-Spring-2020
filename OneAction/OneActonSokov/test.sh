if pgrep -x "gunicorn" > /dev/null
then
  echo gunicorn is open
else
  echo opening gunicorn
  bash start.sh
fi

ab -p post_create.data -T application/x-www-form-urlencoded -n 10000 -c 100 http://localhost:5000/
