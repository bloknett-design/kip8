#!/bin/bash
# Task 490-492 SMOKE kip8: поднятие http-сервера (9007) + прогон
# browser-check + остановка сервера. Вывод — в файл и stdout.
cd /home/z/my-project/kip8 || exit 2
python3 -m http.server 9007 -d /home/z/my-project/kip8 \
    > /tmp/http9007.log 2>&1 &
SERVER_PID=$!
sleep 1.5
python3 scripts/task490-492-smoke-k8.py 2>&1
RC=$?
kill $SERVER_PID 2>/dev/null
exit $RC
