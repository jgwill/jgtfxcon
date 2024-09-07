import pandas as pd
import os

import sys
import subprocess

from jgtutils.jgtos import mkfn_cdata_filepath


bn="__REAL"
if "demo" in os.environ and os.environ["demo"]=="1":
    bn="__DEMO"
fn=bn+".xlsx"
file_path=mkfn_cdata_filepath(fn)
# Load the spreadsheet
#file_path = f'./data/jgt/{bn}.xlsx'

# before we load, check if exists, otherwise run soffice --headless --convert-to xlsx "file_path.replace('.xlsx', '.xls')" "file_path"
if not os.path.exists(file_path):
    print(f"File {file_path} does not exist. Run soffice --headless --convert-to xlsx {file_path.replace('.xlsx', '.xls')} {file_path}")
    print("Trying to run it for us !")
    subprocess.run(['soffice', '--headless', '--convert-to', 'xlsx', file_path.replace('.xlsx', '.xls'), file_path])




xls = pd.ExcelFile(file_path)

# Load the sheet into a DataFrame
sheet_name = 'Combined Account Statement'
df = pd.read_excel(file_path, sheet_name=sheet_name)


# Define a function to extract tables based on the given pattern
"""
def extract_table(df, header_keyword):
    start_idx = df[df.iloc[:, 0].str.contains(header_keyword, na=False)].index[0] + 3
    end_idx = df[df.iloc[:, 0].str.contains('Total', na=False)].index[0]
    table = df.iloc[start_idx:end_idx]
    table.columns = table.iloc[0]
    table = table[1:]
    return table

# Extract the tables
closed_trade_list = extract_table(df, 'CLOSED TRADE LIST')
outstanding_orders = extract_table(df, 'OUTSTANDING ORDERS')
open_floating_positions = extract_table(df, 'OPEN/FLOATING POSITIONS')

OPEN/FLOATING POSITIONS

"""
table_columns_must_have={
    "CLOSED TRADE LIST":["Ticket #","Symbol","Volume","Date","Sold","Bought","Gross P/L","Net P/L","Comm"],
    "OUTSTANDING ORDERS":["Ticket #","Symbol","Volume","Type","Date","Price","S/L","T/P","Time"],
    "OPEN/FLOATING POSITIONS":["Ticket #","Symbol","Volume","Type","Date","Price","S/L","T/P","Time"]
}
# Adjust the function to handle cases where the keyword is not found
def extract_table(df, header_keyword):
    try:
        ending_search_str = 'Total:'
        table = _extract_table(df, header_keyword, ending_search_str)
        #print(table.)
        if table is None:
            alt_endding_kw="No data found for the statement period"
            table = _extract_table(df, header_keyword, alt_endding_kw)
            print(header_keyword)
            print(table)
        else:
            print("We got it the first time:",header_keyword)
        if table is None:return pd.DataFrame()
        
        return table
    except IndexError:
        
        return pd.DataFrame() 

def _extract_table_V1_buggy(df, header_keyword, ending_search_str,alt_endding_kw="No data found for the statement period"):
    try:
        start_idx = df[df.iloc[:, 0].str.contains(header_keyword, na=False)].index[0] + 2
        end_idx = df[df.iloc[:, 0].str.contains(ending_search_str, na=False)].index[0] + 1 if ending_search_str == 'Total:' else 0
        ldf=len(df)
        table = df.iloc[start_idx:end_idx]
        table.columns = table.iloc[0]
        table = table[1:]
        #trip df from our end_idx
        extracted_table = table.copy()
        print(table.columns)
        df.drop(df.index[0:end_idx+1],inplace=True)
        df.reset_index(drop=True,inplace=True)
        ldf=len(df)
        print("head",df.head(1))
        print("tail",df.tail(1))
        return extracted_table # Return an empty DataFrame if the keyword is not found
    except IndexError:
        return None

def _extract_table(df, header_keyword, ending_search_str, alt_ending_kw="No data found for the statement period"):
    try:
        start_idx = df[df.iloc[:, 0].str.contains(header_keyword, na=False)].index[0] + 2
        
        # Try to find the ending_search_str
        end_idx_candidates = df[df.iloc[:, 0].str.contains(ending_search_str, na=False)].index
        if len(end_idx_candidates) == 0:
            # If ending_search_str is not found, use alt_ending_kw
            end_idx_candidates = df[df.iloc[:, 0].str.contains(alt_ending_kw, na=False)].index
            if len(end_idx_candidates) == 0:
                raise IndexError("Neither ending_search_str nor alt_ending_kw found in the DataFrame.")
        
        end_idx = end_idx_candidates[0] #+ 1 if ending_search_str == 'Total:' else 0
        
        ldf = len(df)
        table = df.iloc[start_idx:end_idx]
        table.columns = table.iloc[0]
        table = table[1:]
        
        # Trim df from our end_idx
        extracted_table = table.copy()
        print(table.columns)
        df.drop(df.index[0:end_idx+1], inplace=True)
        df.reset_index(drop=True, inplace=True)
        ldf = len(df)
        print("head", df.head(1))
        print("tail", df.tail(1))
        print("columns:",table.columns)
        return extracted_table  # Return the extracted table
    except IndexError as e:
        print(f"Error: {e}")
        return None
#print(df)
clean_from_before_anything_header_keyword="ACCOUNT ACTIVITY"
clean_to_before_anything_header_keyword="CLOSED TRADE LIST"

def _clean_from_before_table(df,header_keyword,quiet=True):
    try:
        start_idx = df[df.iloc[:, 0].str.contains(header_keyword, na=False)].index[0] 
        if not quiet:print("clean from before:",header_keyword)
        if not quiet:print("  start_idx:",start_idx)
        df.drop(df.index[start_idx:],inplace=True)
        df.reset_index(drop=True,inplace=True)
        return df
    except IndexError:
        pass

def _clean_to_before_table(df,header_keyword,quiet=True):
    try:
        start_idx = df[df.iloc[:, 0].str.contains(header_keyword, na=False)].index[0] 
        if not quiet:print("clean to before:",header_keyword)
        if not quiet:print("  start_idx:",start_idx)
        df.drop(df.index[:start_idx],inplace=True)
        #reset index
        df.reset_index(drop=True,inplace=True)
        return df
    except IndexError:
        pass

df=_clean_to_before_table(df,clean_to_before_anything_header_keyword)
df=_clean_from_before_table(df,clean_from_before_anything_header_keyword)

df.to_csv("_tmp_fxreport_df.csv",index=False)
#exit(0)
# Extract the tables
closed_trade_list = extract_table(df, 'CLOSED TRADE LIST')
outstanding_orders = extract_table(df, 'OUTSTANDING ORDERS')
open_positions = 'OPEN/FLOATING POSITIONS'
# open_positions = 'OPEN'
open_floating_positions = extract_table(df, open_positions)
#exit(0)

# Save the non empty tables to separate csv files at the same location as the input file with the same basename and an additional suffix .TABLE.csv
output_dir = os.path.dirname(file_path)
output_basename = os.path.basename(file_path).replace('.xlsx', '')
closed_trade_columns_to_keep_as_csv="Ticket #,Symbol,Volume,Date,Sold,Bought,Gross P/L,Net P/L,Comm"
closed_trade_list_filtered = closed_trade_list[closed_trade_columns_to_keep_as_csv.split(',')].copy()
closed_trade_list_filtered.to_csv(os.path.join(output_dir, output_basename + '.closed.csv'), index=False)
outstanding_orders_columns_to_keep_as_csv="Order #,Expire Date,Type,Ticket,Symbol,Volume,Date,B/S,Price,Peg Offset,Market Price,Created By"
outstanding_orders_filtered = outstanding_orders[outstanding_orders_columns_to_keep_as_csv.split(',')].copy()
outstanding_orders_filtered.to_csv(os.path.join(output_dir, output_basename + '.orders.csv'), index=False)
open_floating_positions_columns_to_keep_as_csv="Ticket #,Symbol,Volume,Date,Sold,Bought,Floating P/L,Markups (pips),Comm,Dividends,Rollover,Net P/L,Rebates,Condition,Created By"
open_floating_positions_filtered = open_floating_positions[open_floating_positions_columns_to_keep_as_csv.split(',')].copy()
open_floating_positions_filtered.to_csv(os.path.join(output_dir, output_basename + '.opens.csv'), index=False)


#closed_trade_list.tail(15)


