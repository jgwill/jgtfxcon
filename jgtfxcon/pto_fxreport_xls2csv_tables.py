import shutil
import pandas as pd
import os

import sys
import subprocess

from jgtutils.jgtcommon import new_parser, parse_args,add_demo_flag_argument
from jgtutils.jgtos import mkfn_cdata_filepath

def _parse_args(from_jgt_env=True):
    parser = new_parser("JGT FX Report Transformer CLI", "Transform FX report XLSX to CSV tables", "fxreport2csv")
    parser=add_demo_flag_argument(parser,from_jgt_env=from_jgt_env)
    
    
    args=parse_args(parser)
    return args

def main():
    args=_parse_args()
    demo=args.demo
    #if "demo" in os.environ and os.environ["demo"]=="1":
    #    demo=True
    
    doit(demo=demo)

def doit(bn="__REAL",demo=False):

    if demo:
        bn="__DEMO"
    
    fn=bn+".xlsx"
    file_path=mkfn_cdata_filepath(fn)
    # Load the spreadsheet
    #file_path = f'./data/jgt/{bn}.xlsx'

    # before we load, check if exists, otherwise run soffice --headless --convert-to xlsx "file_path.replace('.xlsx', '.xls')" "file_path"
    source_xls = file_path.replace('.xlsx', '.xls')
    if not os.path.exists(source_xls):
        from jgtutils.jgtcommon import dt_from_last_week_as_string_fxformat
        print("Running the fxreport first to get the XLS file")
        arg_demo="--demo" if demo else "--real" 
        subprocess.run(['fxreport',arg_demo,'--no_tlid','-B',bn,'-s',dt_from_last_week_as_string_fxformat(),'-F','xls'],check=True)
    
    if not os.path.exists(file_path):            
        print(f"Converting File: {source_xls} -> {file_path}")
        #check if soffice is in the path
        if not shutil.which("soffice"):
            print("soffice not found in the path. Please install LibreOffice and make sure soffice is in the path before running this script without the XLSX file already created")
        base_dir=os.path.dirname(file_path)
        subprocess.run(['soffice', '--headless', '--convert-to', 'xlsx', source_xls, "--outdir",base_dir],check=True)




    #xls = pd.ExcelFile(file_path)

    # Load the sheet into a DataFrame
    sheet_name = 'Combined Account Statement'
    df = pd.read_excel(file_path, sheet_name=sheet_name)


    # Adjust the function to handle cases where the keyword is not found
    def extract_table(df, header_keyword):
        try:
            ending_search_str = 'Total:'
            table = _extract_table(df, header_keyword, ending_search_str)
            #print(table.)
            if table is None:
                alt_endding_kw="No data found for the statement period"
                table = _extract_table(df, header_keyword, alt_endding_kw)
                #print(header_keyword)
                #print(table)
            else:
                #print("We got it the first time:",header_keyword)
                pass
            if table is None:return pd.DataFrame()
            
            return table
        except IndexError:
            
            return pd.DataFrame() 

        

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
            #print(table.columns)
            df.drop(df.index[0:end_idx+1], inplace=True)
            df.reset_index(drop=True, inplace=True)
            ldf = len(df)
            #print("head", df.head(1))
            #print("tail", df.tail(1))
            #print("columns:",table.columns)
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

    #df.to_csv("_tmp_fxreport_df.csv",index=False)
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


if __name__ == '__main__':
    main()

