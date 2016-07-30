# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 15:33:17 2016

@author: marco
"""
#test
from requests.exceptions import ConnectionError
import datetime as dt
import numpy as np
from pandas import DataFrame, Series, set_option
from pandas_datareader import data
from shutil import copytree
from os import path, stat


class Risparmi:

    def __init__(self, directory='fabio'):

        set_option('expand_frame_repr', False)
        set_option('precision', 4)

        # crea una nuova cartella con il nome passato a init
        if not path.exists(directory):
            # e il contenuto di asset(template)
            copytree('assets(template)', directory)

        self.date = dt.datetime.today().strftime("%d/%m/%y")

        self.directory = directory
        self.assets = {'stock': DataFrame(), 'bond': DataFrame(), 'currency': DataFrame(),
                       'cash': DataFrame()}
        self.assets_inizialization()  # inizializzazione asset da file csv

        self.stock_val_account = {}
        self.stock_val_sector = {}
        self.updated_assets_values_gen()

        self.stock_report_gen()
        self.bond_report_gen()

    def assets_inizialization(self):
        '''Popola il dizionario con i valori localizzati nella cartella assets'''

        for el in self.assets:
            path_to_data = self.directory + '/' + el + '.csv'
            self.assets[el] = self.assets[el].from_csv(path_to_data)

    def get_asset_values_list(self, asset_type, asset_value):
        return list(set(self.assets[asset_type][asset_value]))

    def get_asset_preloded(self, symbol):
        asset_types = ['stock', 'bond', 'currency']
        for asset_type in asset_types:
            preloaded = self.assets[asset_type][
                self.assets[asset_type].simbolo == symbol]
            if not preloaded.empty:
                return preloaded.head(1).to_dict(orient='list')

    def get_complete_symbol_list(self):

        asset_types = ['stock', 'bond', 'currency']
        complete_list = []
        for asset_type in asset_types:
            complete_list.extend(list(set(self.assets[asset_type]['simbolo'])))
        return complete_list

    def get_inizialized_values(self, asset_type, external=True, asset=None):

        with open(self.directory + '/' + asset_type + '.csv', 'r') as f:
            header = f.readline().strip('\n')
        header_list = header[1:].split(',')
        if external:
            return {header: '' for header in header_list}
        else:
            return dict(zip(header_list, asset))

    def save_to_csv(self):
        '''Accede a ogni dataframe del dizionario e lo salva sul corrispondente file CSV'''

        for el in self.assets:
            file_path = self.directory + '/' + el + '.csv'
            temp = self.assets[el].to_csv()
            f = open(file_path, 'w')
            f.write(temp)
            f.close()

    def updated_asset_values_save(self):

        with open('stock_value.csv', 'w') as f:
            f.write(self.updated_stock_values.to_csv(header=True))

        with open('currency_value.csv', 'w') as f:
            f.write(self.updated_currency_values.to_csv(header=True))

    def add_asset_transaction(self, transaction_values_dict, asset_type):

        self.assets[asset_type].loc[
            len(self.assets[asset_type].index)] = transaction_values_dict

    def updated_assets_values_gen(self, forced=False):
        '''Crea un dataframe dei valori attuali di stock e currency dal sito Yahoo Finance'''

        last_download = dt.datetime.fromtimestamp(
            stat('stock_value.csv').st_mtime).strftime("%d/%m/%y")

        if last_download != self.date or forced:
            try:
                # stocks
                self.updated_stock_values = DataFrame()
                for symbol in list(set(self.assets['stock']['simbolo'])):
                    temp = data.get_quote_yahoo(symbol)
                    self.updated_stock_values = self.updated_stock_values.append(
                        temp)
                self.updated_stock_values.index.name = 'simbolo'
                self.updated_stock_values = self.updated_stock_values.drop(
                    ['PE', 'short_ratio', 'time', 'change_pct'], axis=1)

                # currency
                self.updated_currency_values = DataFrame()
                for symbol in list(set(self.assets['currency']['simbolo'])):
                    temp = data.get_quote_yahoo(symbol)
                    self.updated_currency_values = self.updated_currency_values.append(
                        temp)
                self.updated_currency_values.index.name = 'simbolo'
                self.updated_currency_values = self.updated_currency_values.drop(
                    ['PE', 'short_ratio', 'time', 'change_pct'], axis=1)

                self.updated_asset_values_save()
            except ConnectionError:
                self.updated_stock_values = DataFrame().from_csv('stock_value.csv')
                self.updated_currency_values = DataFrame().from_csv('currency_value.csv')
        else:
            self.updated_stock_values = DataFrame().from_csv('stock_value.csv')
            self.updated_currency_values = DataFrame().from_csv('currency_value.csv')

    def stock_report_gen(self):

        def stock_agg_func(*args):
            '''da gestire il caso con conversione in euro per flag'''

            flag = False  # temporanea
            asset = args[0]

            index = ['conto', 'simbolo', 'settore', 'valuta', 'quantità', 'acquisto_tot',
                     'vendita_tot', 'cedola-dividendo_netto_tot']
            report = [asset[9], asset[0], asset[3], asset[4]]

            if asset[7] == 'acquisto':

                tobin_tax = asset[8]
                gross_price = asset[11] * asset[10]
                commission = asset[13]

                if np.isnan(tobin_tax) == False:
                    tobin_tax *= gross_price
                else:
                    tobin_tax = 0

                if flag and np.isnan(asset[15]) == False:
                    gross_price = (asset[11] * asset[15]) * asset[10]
                    commission *= asset[15]

                temp = tobin_tax + gross_price + commission
                report.append(asset[10])
                report.append(temp)
                report.append(np.nan)
                report.append(np.nan)

            elif asset[7] == 'vendita':
                gross_price = asset[11] * asset[10]
                tax = gross_price * asset[14]
                commission = asset[13]

                if flag and np.isnan(asset[15]) == False:
                    gross_price = (asset[11] * asset[15]) * asset[10]
                    tax = gross_price * asset[14]
                    commission *= asset[15]

                temp = gross_price - commission - tax
                report.append((-1) * asset[10])
                report.append(np.nan)
                report.append(temp)
                report.append(np.nan)

            elif asset[7] == 'cedola-dividendo':

                gross_dividend = asset[12]
                tax = gross_dividend * asset[14]
#               # cosi è giusto secondo flake
                if flag and not np.isnan(asset[15]):
                    gross_dividend *= asset[15]
                    tax = gross_dividend * asset[14]

                temp = gross_dividend - tax
                report.append(np.nan)
                report.append(np.nan)
                report.append(np.nan)
                report.append(temp)

            return Series(report, index=index)

        def stock_report_func(*args):

            asset = args[0]
            price = asset[0]

            currency = asset.name[0].lower()
            symbol = asset.name[3]
            account = asset.name[1]
            settore = asset.name[2]
            # questo if serve per aggiustare i prezzi(yahoo) inglesi
            if currency == 'sterline':
                # asset.name è la variabile per accedere all indice/i della
                # riga e gli indici dipendono dal groupby in fondo
                price = asset[0] / 100.0
            #print (str(price)+''+str(asset[1])+''+str(type(price))+''+str(type(asset[1])))
            flash = price * asset[1]

            # questa funzione serve a calcolare la valorizzazione dei conti, è
            # temporanea

            self.val_gen(symbol, account, flash, settore)

            status = flash - asset[2]

            if np.isnan(asset[3]) == False:  # questo aggiunge le vendite a status
                status += asset[3]
            if np.isnan(asset[4]) == False:  # questo aggiunge  i dividendi a status
                status += asset[4]

            report = [asset[2], asset[3], asset[4], price, flash, status]
            index = ['investito', 'venduto', 'dividendi',
                     'prezzo', 'flash', 'status']

            return Series(report, index=index)


#       pylint:enable = E1101

        aggregated_stock = self.assets['stock'].apply(
            stock_agg_func, axis=1).groupby(['valuta', 'conto', 'settore',
                                             'simbolo']).sum()

        joined_stock = self.updated_stock_values.join(
            aggregated_stock, how='inner')

        self.stock_report = joined_stock.apply(stock_report_func, axis=1)

        self.active_stock_report = self.stock_report.query('flash!=0.0')

    def bond_report_gen(self):

        def bond_agg_func(*args):

            asset = self.get_inizialized_values(
                'bond', external=False, asset=args[0])
            #print (asset)

            coupon = asset['cedola-dividendo']
            # gestisco le date
            date_formating = lambda y: (
                list(map((lambda x: int(x)), y.split('-'))))

            issue_date = dt.date(*date_formating(asset['data_emissione']))
            refund_date = dt.date(*date_formating(asset['data_rimborso']))
            transfer_date = dt.date(
                *date_formating(asset['data']))  # data valuta

            first_coupon_date = dt.date(
                transfer_date.year, issue_date.month, issue_date.day)
            # print(first_coupon_date)
            if first_coupon_date > transfer_date:
                first_coupon_date = dt.date(
                    first_coupon_date.year - 1, issue_date.month, issue_date.day)

            if asset['tipologia'] == 'annuale':

                days_to_coupon = (transfer_date - first_coupon_date).days
                first_next_coupon = dt.date(
                    first_coupon_date.year + 1, first_coupon_date.month, first_coupon_date.day)
                days_between_coupon = (
                    first_next_coupon - first_coupon_date).days
                # print(days_to_coupon)
                # print(days_between_coupon)
            else:

                month_second_coupon = first_coupon_date.month + 6
                year_second_coupon = first_coupon_date.year
                if month_second_coupon > 12:
                    month_second_coupon -= 12
                    year_second_coupon += 1
                second_coupon_date = dt.date(
                    year_second_coupon, month_second_coupon, first_coupon_date.day)
                #print([first_coupon_date, second_coupon_date])
                if second_coupon_date > transfer_date:
                    days_to_coupon = (transfer_date - first_coupon_date).days
                else:
                    days_to_coupon = (transfer_date - second_coupon_date).days
                # print(days_to_coupon)
                if transfer_date > second_coupon_date:
                    first_next_coupon = dt.date(
                        first_coupon_date.year + 1, first_coupon_date.month, first_coupon_date.day)
                    days_between_coupon = (
                        first_next_coupon - second_coupon_date).days

                else:
                    days_between_coupon = (
                        second_coupon_date - first_coupon_date).days

                # print(days_between_coupon)
                coupon /= 2

            days_from_issue_date = (transfer_date - issue_date).days
            bond_life = (refund_date - issue_date).days
            # print(days_from_issue_date)
            # print(bond_life)

            price_r = 100.0
            price_i = asset['prezzo_emissione']
            price_t = asset['prezzo_acquisto-vendita']
            quantity = asset['quantità']
            commission = asset['commissione']
            tax = asset['tasse']

# acquisto puro
            x = quantity * (price_t / 100)
# rateo maturato all acquisto
            y = ((coupon * days_to_coupon) / days_between_coupon) * quantity
# ritenuta sul rateo all acquisto
            z = y * tax
# disaggio di emissione maturato
            k = (((price_r - price_i) * days_from_issue_date) /
                 bond_life) * (quantity / 100)
# ritenuta sul disaggio
            h = k * tax
# formula investimento(gestire il disaggio negativo)
            price_purchase = x + y - z - h + commission

            #print('{0} {1} {2} {3} {4}'.format(x, y, z, k, price_purchase))
            return Series({'conto': asset['conto'], 'simbolo': asset['simbolo'], 'prezzo': price_purchase})

        self.bond_report = self.assets['bond'].apply(
            bond_agg_func, axis=1).groupby(['conto', 'simbolo']).sum()

    def get_exchange_rate(self):  # temporanea

        usd = self.updated_currency_values.at['eurusd=x', 'last']
        gbp = self.updated_currency_values.at['eurgbp=x', 'last']  # cambi
        chf = self.updated_currency_values.at['eurchf=x', 'last']

        return {'Dollari': usd, 'Sterline': gbp, 'Franchi Svizzeri': chf}

    def get_single_stock_report(self, selection):

        stock_report_copy = self.stock_report.copy()

        unstacked_report = stock_report_copy.reset_index(
            level=['valuta', 'conto', 'settore'], drop=True).reset_index(
                level=['simbolo'])

        df = unstacked_report.groupby(['simbolo']).sum()

        try:
            ris = df.loc[selection]
            ris['prezzo'] = self.updated_stock_values.at[selection, 'last']
        except KeyError:
            return 'simbolo non presente'
        return ris.to_dict()

    def val_gen(self, symbol, account, flash, settore):  # temporanea
        '''serve a popolare il dizionario che contiene la valorizzazione dei conti'''

        is_italian = False

        if symbol[len(symbol) - 3:].lower() == '.mi':
            is_italian = True
        elif symbol[len(symbol) - 2:].lower() == '.l' and is_italian == False:
            # cosi estrapolo il valore(float) del cambio
            cambio = self.updated_currency_values.at['eurgbp=x', 'last']
            flash = flash / cambio
        elif symbol[len(symbol) - 3:].lower() == '.vx' and is_italian == False:
            cambio = self.updated_currency_values.at['eurchf=x', 'last']
            flash = flash / cambio
        elif is_italian == False:
            cambio = self.updated_currency_values.at['eurusd=x', 'last']
            flash = flash / cambio

        if account not in self.stock_val_account:
            self.stock_val_account[account] = flash
        else:
            self.stock_val_account[account] += flash

        if settore not in self.stock_val_sector:
            self.stock_val_sector[settore] = flash
        else:
            self.stock_val_sector[settore] += flash
