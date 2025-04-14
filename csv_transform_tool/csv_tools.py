import pandas as pd
import uuid
import re
import boto3
import json
from io import StringIO

s3 = boto3.client('s3')

BUCKET_NAME="boomi-ai-agent-tools-csv-tools-files"

def _write_file(filename, contents):
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=f"output/{filename}",
        Body=contents
    )

def _read_file(filename):
    response = s3.get_object(
        Bucket=BUCKET_NAME,
        Key=filename
    )
    return response['Body'].read().decode('utf-8')

def _load_csv(filename):
    file_contents = _read_file(filename)
    csv_buffer = StringIO(file_contents)
    return pd.read_csv(csv_buffer, dtype=str)

def operation_regex_replace(running_value, args):
    if running_value['type'] != 'csv':
        raise Exception("REGEX-REPLACE operation requires a csv as input")

    df = running_value['data']
    col = args['column_name']
    match_pattern = args['match_pattern']
    repl_pattern = args['replacement_pattern']

    # some special cases because the LLM makes these mistakes sometimes:
    if repl_pattern == 'None':
        repl_pattern = ''
    repl_pattern = re.sub('(\$)(\d)', '\\\2', repl_pattern)

    before_values = df[col].tolist()
    df[col] = df[col].apply(lambda value: re.sub(match_pattern, repl_pattern, value))
    after_values = df[col].tolist()

    print(f"LOG: REGEX-REPLACE applied '{match_pattern}' -> '{repl_pattern}' to column {col}:\nBefore:\n", before_values, "After:\n", after_values)

    return running_value

def operation_extract_column(running_value, args):
    if running_value['type'] != 'csv':
        raise Exception("EXTRACT-COLUMN operation requires a csv as input")

    df = running_value['data']
    from_col = args['from_column_name']
    new_col = args['new_column_name']
    match_pattern = args['match_pattern']
    repl_pattern = args['replacement_pattern']

    # some special cases because the LLM makes these mistakes sometimes:
    if repl_pattern == 'None':
        repl_pattern = ''
    repl_pattern = re.sub('(\$)(\d)', '\\\2', repl_pattern)

    source_col_values = df[from_col].tolist()
    df[new_col] = df[from_col].apply(lambda value: re.sub(match_pattern, repl_pattern, value))
    dest_col_values = df[new_col].tolist()

    print(f"LOG: EXTRACT-COLUMN applied '{match_pattern}' -> '{repl_pattern}' from column {from_col} t column {new_col}:\Original:\n", 
        source_col_values, "New:\n", dest_col_values)

    return running_value

def operation_drop_duplicates(running_value, args):
    if running_value['type'] != 'csv':
        raise Exception("LOG: DROP-DUPLICATES operation requires a csv as input")

    df = running_value['data']

    starting_row_count = len(df.index)
    df.drop_duplicates(inplace=True)
    ending_row_count = len(df.index)
    dropped_row_count = starting_row_count - ending_row_count
    
    print(f"LOG: DROP-DUPLICATES dropped {dropped_row_count} duplicate rows")
    
    return running_value

def operation_convert_to_json(running_value, args):
    if running_value['type'] != 'csv':
        raise Exception("CONVERT-TO-JSON operation requires a csv as input")
    
    df = running_value['data']

    column_order = df.columns.tolist()
    json_str = df[column_order].to_json(orient='records')
    json_str = json.dumps(json.loads(json_str), indent=4) # For pretty printing

    print(f"LOG: CONVERT-TO-JSON successful")
    return {'type': 'json', 'data': json_str}

def operation_copy_to_file(running_value, args):
    filename = args['filename']

    if running_value['type'] == 'csv':
        file_contents = running_value['data'].to_csv(index=False)
    elif running_value['type'] == 'json':
        file_contents = running_value['data']
    
    _write_file(filename, file_contents)

    print(f"LOG: MAKE-COPY for {filename} successful")
    
    # don't modify the value or type, just passthrough
    return running_value

available_operations = {
    'REGEX-REPLACE'  : operation_regex_replace,
    'EXTRACT-COLUMN' : operation_extract_column,
    'DROP-DUPLICATES': operation_drop_duplicates,
    'CONVERT-TO-JSON': operation_convert_to_json,
    'MAKE-COPY'      : operation_copy_to_file
}

def run_operations(filename, operations):
    df = _load_csv(filename)

    running_value = {'type': 'csv', 'data': df}
    for op in operations:
        op_func = available_operations[op['operation']]
        running_value = op_func(running_value, op)

    return running_value
