import json

def analyze_trades_orders_relationship(json_file_path):
    data = load_transactions_json_table(json_file_path)
    
    trades = data.get('trades', [])
    orders = data.get('orders', [])
    
    analysis_results = []
    
    for trade in trades:
        trade_id = trade.get('trade_id')
        open_order_id = trade.get('open_order_id')
        open_order_req_id = trade.get('open_order_req_id')
        
        related_orders = [
            order for order in orders 
            if order.get('order_id') == open_order_id or order.get('request_id') == open_order_req_id
        ]
        
        if related_orders:
          analysis_results.append({
            'trade_id': trade_id,
            'related_orders': related_orders,
            'relationship': f"Trade {trade_id} is related to Orders {[order.get('order_id') for order in related_orders]}"
        }) 
    
    return analysis_results

def load_transactions_json_table(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    return data

from jgtutils import jgtcommon

def args_parse():
    PROG = "fxtransactanalyze"
    EPILOG = "Analyze trades and orders relationship"
    parser=jgtcommon.new_parser("JGT Transact Analyzer CLI",EPILOG,PROG)
    parser=jgtcommon.add_demo_flag_argument(parser)
    
    args=jgtcommon.parse_args(parser)
    return args
    
def main():
    args=args_parse()
    # Example usage
    json_file_path = 'demo_fxtransact.json' if args.demo else 'fxtransact.json'
    results = analyze_trades_orders_relationship(json_file_path)
    json_str=json.dumps(results, indent=2)
    print(json_str)
    # for result in results:
    #     print(result)

if __name__ == '__main__':
    main()