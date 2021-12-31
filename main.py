# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from models.pandas_validator import PandasValidator
from models.table import Table
from query_sender.connector import MariadbConnector


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    sender = MariadbConnector(
        host='localhost',
        port=3307,
        user='scott',
        password='tiger',
        database='maasbi'
    )
    source = Table(name='dw_vn_prct_bs', sender=sender) \
        .where("date_format(etl_cre_dtm, '%Y%m%d') = '20210714'")

    target = Table(name='dw_vn_prct_bs', sender=sender) \
        .where("date_format(etl_cre_dtm, '%Y%m%d') = '20210714'")

    res = PandasValidator.value_compare(source=source, target=target)

    print(res.result)

