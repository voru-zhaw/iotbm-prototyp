# 3rd party modules
import pandas as pd


def get_css(file):

    with open(file) as css:
        return css.read()


def get_data(file, sheet):

    with pd.ExcelFile(file) as excel:
        return pd.read_excel(excel, sheet_name=sheet, skiprows=3)
