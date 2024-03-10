import pandas as pd
import requests

CSV_FILE_NAME = "desynced_instructions.csv"


def fetch_instruction_table_from_url():
    url = r'https://wiki.desyncedgame.com/Special:CargoTables/instruction'
    # header = {
    #    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    #    "X-Requested-With": "XMLHttpRequest"
    # }
    # r = requests.get(url, headers=header)
    r = requests.get(url)
    # directly reading with pandas from the url gives 403 forbidden
    dfs = pd.read_html(r.text)

    assert (len(dfs) == 1)
    df = dfs[0]
    return df


def main():
    df = fetch_instruction_table_from_url()

    # containing only the information needed by the compile step
    # name is the index
    df_result = pd.DataFrame(columns=['num_args', 'arg_idxs','output_arg_num', 'is_iterator'])
    # print(df.columns)

    # generate function stubs
    result_str = "# stubs of functions for usage with an IDE"

    for index, row in df.iterrows():
        name = row['luaId']
        is_iterator = False
        if name.startswith('for_'):
            name = name[4:]
            is_iterator = True
        output_name = None
        output_pos = pd.NA
        args = []
        args_to_populate = []
        cfg_edge_args = []
        for i in range(1, 12):
            arg_type = row['argsType' + str(i)]
            arg_name = row['argsName' + str(i)]
            arg_datatype = row['argsDataType' + str(i)]
            if not pd.isna(arg_type):
                assert arg_type in ["Input", "Output", "Exec"]
                if arg_type == "Input" or (arg_type == "Output" and output_name is not None):
                    arg_name = arg_name.lower().replace(' ', '_')  # into pythonic form
                    args.append(arg_name)
                    args_to_populate.append(i-1)
                if arg_type == "Output" and output_name is None:
                    arg_name = arg_name.lower().replace(' ', '_')  # into pythonic form
                    output_name = arg_name
                    output_pos = i-1
                if arg_type == "Exec":
                    cfg_edge_args.append(arg_name)
        result_str += "\n\ndef " + name + "("

        for arg in args:
            result_str += arg + ", "

        if len(args) > 0:
            result_str = result_str[:-2]  # remove trailing ,
        result_str += "):\n"
        if is_iterator:
            result_str += "\tyield "
        else:
            result_str += "\treturn "
        if output_name is not None:
            result_str += "'" + output_name + "'\n"
        else:
            result_str += "None\n"

        result_df_row = pd.Series()
        result_df_row['num_args'] = len(args)
        result_df_row['arg_idxs'] = args_to_populate
        result_df_row['output_arg_num'] = output_pos
        result_df_row['is_iterator'] = is_iterator

        df_result.loc[name] = result_df_row

    with open("desynced_functions.py", "w") as f:
        f.write(result_str)
    df_result.to_csv(CSV_FILE_NAME, index_label="name")


if __name__ == "__main__":
    main()
