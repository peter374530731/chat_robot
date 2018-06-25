netstat -lntp |grep -w 8000 | awk '{print $7}' | awk -F '/' '{print $1}' | xargs -I '{}' kill -9  {}
