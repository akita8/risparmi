# pylint: disable=C,R
import datetime as dt
from sqlalchemy import create_engine
from costum_orms import Stock, Bond, Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.reflection import Inspector

class SqlIO:

    def __init__(self):

        self.engine = create_engine('sqlite:///prova.db', echo=False)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        self.inpector = Inspector.from_engine(self.engine)

        if not self.inpector.get_table_names():
            self.create_tables()

    def create_tables(self):
        Base.metadata.bind = self.engine
        Base.metadata.create_all(self.engine)


# temporaneo
    def import_stock_csv(self):
        def cleaned(value):

            if value == '':
                return None
            if '/' in value:
                d = value.split('/')
                year = d[2]
                if len(year) == 4:
                    pass
                elif int(year) > 16:
                    year = '19' + year
                else:
                    year = '20' + year
                return dt.date(int(year), int(d[1]), int(d[0]))

            return value
        filename = input('inserisci filename: ')
# '/home/marco/Documenti/progetti-atom/progetto-finanza/fabio/stock.csv'
        with open(filename, 'r') as f:
            temp = f.read().split('\n')
            rows = [el.split(',') for el in temp if el != '']
            del rows[0]
            rows_cleaned = [[cleaned(x) for x in el] for el in rows]
        tipo = input('metti il tipo: ')
        # stock
        if tipo == 'stock':

            columns_names = ['id', 'symbol', 'denomination', 'market',
                             'sector', 'currency', 'isin', 'nation',
                             'transaction', 'tax_on_purchase_percentage',
                             'account', 'quantity', 'buy_sell_price',
                             'dividend', 'commission',
                             'tax_percentage', 'exchange_rate', 'owner',
                             'date_of_transaction']

            commit_list = [Stock(**dict(zip(columns_names, el)))
                           for el in rows_cleaned]

            self.session.add_all(commit_list)
            self.session.commit()
