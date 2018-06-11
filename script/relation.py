import pandas as pd
from pandas import DataFrame


def main():
    datas = pd.read_csv("../data/split.csv")
    columns = datas.columns

    for row in datas.iterrows():
        print(row)

    # relations = datas[]


if __name__ == '__main__':
    main()