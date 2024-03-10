import pandas as pd
import requests

CSV_FILE_NAME = "desynced_instructions.csv"


def update_instruction_table_from_url():
    url = r'https://wiki.desyncedgame.com/Special:CargoTables/instruction'
    #header = {
    #    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    #    "X-Requested-With": "XMLHttpRequest"
    #}
    #r = requests.get(url, headers=header)
    r = requests.get(url)
    # directly reading with pandas from the url gives 403 forbidden
    dfs = pd.read_html(r.text)

    assert (len(dfs) == 1)
    df = dfs[0]
    df.to_csv(CSV_FILE_NAME)


def main():
    #update_instruction_table_from_url()

    df = pd.read_csv(CSV_FILE_NAME)

    print(df)


if __name__ == "__main__":
    main()
