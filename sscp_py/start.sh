for p_pid in `ps -ef |grep python|egrep -v grep | awk '{print $2}'`; do kill -9 $p_pid; done
nohup python3 manage.py runserver 0.0.0.0:8000>/dev/null 2>&1 &
