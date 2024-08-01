#!/bin/bash

. _load_variables.sh

#@STCGoal To grab the OrderID from the output
#@STCIssue The script will grab the OrderID from the output


entry_rate=0.9000 
stop_rate=0.8997
instrument=AUD/CAD 
buysell=B 
lots=1 

python CreateEntryOrderPtoAddStop.py $real_fx_cli_base_args -lots $lots -r $entry_rate -d $buysell -i $instrument -stop $stop_rate  | tee __output.txt  && \
  OrderID=$(cat __output.txt| grep -o 'OrderID=[0-9]*' | cut -d '=' -f2) && \
  echo "OrderID: $OrderID" && sleep 2 &&  \
  python RemoveOrder.py $real_fx_cli_base_args -orderid $OrderID && \
  echo "OrderID: $OrderID removed" || \
  echo "Test order failed"