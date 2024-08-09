import json

def analyze_trades_orders_relationship(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    trades = data.get('trades', [])
    
    analysis_results = []
    
    for trade in trades:
        trade_id = trade.get('trade_id')
        open_order_id = trade.get('open_order_id')
        open_order_req_id = trade.get('open_order_req_id')
        
        analysis_results.append({
            'trade_id': trade_id,
            'open_order_id': open_order_id,
            'open_order_req_id': open_order_req_id,
            'relationship': f"Trade {trade_id} is related to Order {open_order_id} with Request ID {open_order_req_id}"
        })
    
    return analysis_results

# Example usage
json_file_path = 'demo_fxtransact.json'
results = analyze_trades_orders_relationship(json_file_path)
print(json.dumps(results, indent=2))
# for result in results: