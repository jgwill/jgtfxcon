cversion=$(cat pyproject.toml |tr '"' " " |awk '/version/ {print $3}')
make dist  && \
  pip install --user dist/jgtfxcon-$cversion-py3-none-any.whl  && \
  jgtfxcli -i "USD/CAD" -t "m15" -o  -v 2 && echo "--------TST1 passed " && \
  jgtfxcli -i "USD/CAD,EUR/USD,SPX500" -t "m15,m5,H1,H4,D1,W1" -c 1500 -o -v 2
