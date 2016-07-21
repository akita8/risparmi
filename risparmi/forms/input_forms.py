from risparmi.core.misc import npyscreeni

'''
WIDGET ID DECLARATION
'''

symbol_id = 'simbolo'
denom_id = 'denominazione'
market_id = 'mercato'
sector_id = 'settore'
currency_id = 'valuta'
isin_id = 'isin'
nation_id = 'nazione'
account_id = 'conto'
price_id = 'prezzo_acquisto-vendita'
dividend_coupon_id = 'cedola-dividendo'
quantity_id = 'quantità'
commission_id = 'commissione'
tax_id = 'tasse'
exchange_rate_id = 'cambio'
owner_id = 'proprietario'
date_id = 'data' #per bond indica data valuta
type_id='tipologia' #per bond
price_issued_id='prezzo_emissione' #per bond
date_issued_id='data_emissione' #per bond
date_refund_id='data_rimborso'
transaction_id = 'transazione'  # serve per currency
description_id='descrizione'# serve per cash
amount_id='importo'# serve per cash

'''
WIDGET ID LISTS
'''

popup_id_list = [market_id, sector_id,
                 currency_id, nation_id, account_id, owner_id]

multiple_autocomplete_id_list = [
    market_id, sector_id, currency_id, nation_id, account_id, owner_id]

single_autocomplete_id_list = [symbol_id, denom_id, isin_id]

is_number_check_id_list=[price_id, quantity_id, tax_id, commission_id, amount_id, price_issued_id]

complete_id_list = [symbol_id, denom_id, market_id, sector_id, currency_id, isin_id, nation_id, account_id,
                    price_id, dividend_coupon_id, quantity_id, commission_id, tax_id, owner_id, date_id,
                    transaction_id, description_id, amount_id, type_id, price_issued_id, date_issued_id,
                    price_issued_id, date_refund_id]



'''
BASE DATA INPUT FORM CLASS
'''


class BaseInputForm(npyscreen.FormMultiPageActionWithMenus):

    def while_waiting(self):
        self.popup_other()

    def popup_other(self):
        for el in popup_id_list:

            try:
                value = self.get_widget(el).get_selected_objects()[0]
            except (IndexError, TypeError, KeyError):
                continue

            if value == 'altro...':
                try:
                    pop = NotInChoicesPopup()
                    pop.center_on_display()
                    pop.edit()
                    self.get_widget(el).values[self.get_widget(
                        el).value[0]] = pop.question.value
                    self.get_widget(el).display()
                except NoInputException:
                    self.get_widget(el).value = []
            else:
                continue

    def autocomplete_with_existing(self):
        symbol_list = self.parentApp.myRisparmi.get_complete_symbol_list()
        try:
            pop = AutocompletePopup()
            pop.center_on_display()
            pop.edit()
            symbol_input = pop.question.value
            # symbol_input=self.get_widget(symbol_id).value
            if symbol_input in symbol_list:
                preloaded = self.parentApp.myRisparmi.get_asset_preloded(
                    symbol_input)
                for id_single in single_autocomplete_id_list:
                    try:
                        self.get_widget(id_single).set_value(
                            preloaded[id_single][0])
                    except KeyError:
                        continue
                for id_multiple in multiple_autocomplete_id_list:
                    try:
                        value = self.get_widget_index(
                            preloaded[id_multiple][0], id_multiple)
                        self.get_widget(id_multiple).set_value(value)
                    except KeyError:
                        continue
                self.display()
            else:
                npyscreen.notify_confirm(
                    'Il simbolo inserito non è presente nel database')
        except NoInputException:
            pass

    def get_widget_index(self, value, widget_id):
        values = self.get_widget(widget_id).values
        indexed_values = {}
        for i in range(len(values)):
            indexed_values[values[i]] = i
        return indexed_values[value]

    def clear_all_values(self):
        for _id in complete_id_list:
            try:
                self.get_widget(_id).value = None
                if _id in multiple_autocomplete_id_list and hasattr(self.get_widget(_id), 'values'):
                    self.get_widget(_id).values.pop()
                    self.get_widget(_id).values.append('altro...')
                    self.get_widget(_id).display()
            except KeyError:
                continue

    def collect_form_values(self, values_dict):
        for _id in complete_id_list:
            try:
                if hasattr(self.get_widget(_id), 'values'):
                    value = self.get_widget(_id).get_selected_objects()[0]
                    values_dict[_id] = value
                else:
                    value = self.get_widget(_id).value
                    values_dict[_id] = value
                    if _id in is_number_check_id_list and not is_number(value):
                        npyscreen.notify_wait('Input errato: il valore nel widget {0} non è un numero'.format(_id))
                        raise IndexError
            except KeyError:
                continue
            except IndexError:
                return
        return values_dict

    def add_date_widget(self, _id, description):

        self.add_widget_intelligent(npyscreen.TitleDateCombo, w_id=_id, name=description,
                                                begin_entry_at=len(description) + 1, use_two_lines=False)
        self.nextrely+=2

    def add_single_value_widget(self, _id,  description):

        self.add_widget_intelligent(npyscreen.TitleText, w_id=_id,  name=description,
                                    begin_entry_at=len(description) + 1, use_two_lines=False)
        self.nextrely += 2

    def add_multiple_values_widget(self, _id, description, values):

        self.add_widget_intelligent(npyscreen.TitleSelectOne, w_id=_id, name=description,
                                    max_width=50, max_height=len(values)+1, values=values)
        self.nextrely+=2

    def add_multiple_values_widget_external(self, _id, description, value_type, asset_type):

        data = self.parentApp.myRisparmi.get_asset_values_list(
            asset_type, value_type)

        data.append('altro...')

        self.add_widget_intelligent(npyscreen.TitleSelectOne, w_id=_id, name=description,
                                    max_width=50, max_height=len(data)+1, values=data)
        self.nextrely+=2

    def commit(self, transaction, asset_type):
        missing_values = self.parentApp.myRisparmi.get_inizialized_values(asset_type)

        missing_values['transazione']=transaction
        choice = npyscreen.notify_yes_no('Vuoi aggiungere questa transazione?')
        values=self.collect_form_values(missing_values)

        if choice:
            if values:
                # fino a quando ci sarà la tobin tax
                nation=self.get_widget(nation_id).get_selected_objects()[0]
                if nation == 'italia' and transaction=='acquisto' and asset_type=='stock':
                    values['tobin'] = 0.001

                #devo forzare un float su tutti valori numerici di values!!!
                for _id in values:
                    if is_number(values[_id]) and _id is not account_id:
                        values[_id]=float(values[_id])

                self.parentApp.myRisparmi.add_asset_transaction(
                    values, asset_type)
                self.parentApp.setNextForm('MAIN')
                self.parentApp.removeForm(self.parentApp.active_form_id)
            else:
                npyscreen.notify_wait('Il form non è completo!')

    def on_cancel(self):
        self.parentApp.setNextForm('MAIN')
        self.parentApp.removeForm(self.parentApp.active_form_id)


'''
STOCK FORM CLASSES
'''


class BuyStockForm(BaseInputForm):

    def create(self):

        self.transaction = 'acquisto'
        self.asset_type = 'stock'

        self.name = 'Acquisto azioni'

        self.keypress_timeout = 5

        self.menu = self.new_menu(name='Form Menu')
        self.menu.addItem('Autocomplete', self.autocomplete_with_existing, '1')
        self.menu.addItem('Reset Form', self.clear_all_values, '2')

        self.add_single_value_widget(symbol_id, "Inserisci il simbolo dell'azione:")

        self.add_single_value_widget(denom_id, "Inserisci la denominazione dell'azione:")

        self.add_single_value_widget(isin_id, "Inserisci il ISIN dell'azione:")

        self.add_multiple_values_widget_external(account_id, 'Scegli il conto in cui si è effetuata la transazione:',
                                                'conto', self.asset_type)

        self.add_multiple_values_widget_external(owner_id, 'Scegli il proprietario del conto:',
                                                'proprietario', self.asset_type)

        self.add_multiple_values_widget_external(market_id, 'Scegli il mercato di appartenenza:',
                                                'mercato', self.asset_type)

        self.add_multiple_values_widget_external(sector_id, 'Scegli il settore di appartenenza:',
                                                'settore', self.asset_type)

        self.add_multiple_values_widget_external(currency_id, "Scegli la valuta dell'azione:",
                                                'valuta', self.asset_type)

        self.add_multiple_values_widget_external(nation_id, 'Scegli la nazione di appartenenza:',
                                                'nazione', self.asset_type)

        self.add_single_value_widget(price_id, 'Inserisci il prezzo di acquisto:')

        self.add_single_value_widget(quantity_id, 'Inserisci la quantità di azioni comprate:')

        self.add_single_value_widget(commission_id, 'Inserisci la commisione sulla transazione:')

        self.add_date_widget(date_id, 'Inserisci la data della transazione:')


    def on_ok(self):

        self.commit(self.transaction, self.asset_type)


class SellStockForm(BaseInputForm):

    def create(self):

        self.transaction = 'vendita'
        self.asset_type = 'stock'

        self.name = 'vendita azioni'

        self.keypress_timeout = 5

        self.menu = self.new_menu(name='Form Menu')
        self.menu.addItem('Autocomplete', self.autocomplete_with_existing, '1')
        self.menu.addItem('Reset Form', self.clear_all_values, '2')

        self.add_single_value_widget(symbol_id, "Inserisci il simbolo dell'azione:")

        self.add_single_value_widget(denom_id, "Inserisci la denominazione dell'azione:")

        self.add_single_value_widget(isin_id, "Inserisci il ISIN dell'azione:")

        self.add_multiple_values_widget_external(account_id, 'Scegli il conto in cui si è effetuata la transazione:',
                                                'conto', self.asset_type)

        self.add_multiple_values_widget_external(owner_id, 'Scegli il proprietario del conto:',
                                                'proprietario', self.asset_type)

        self.add_multiple_values_widget_external(market_id, 'Scegli il mercato di appartenenza:',
                                                'mercato', self.asset_type)

        self.add_multiple_values_widget_external(sector_id, 'Scegli il settore di appartenenza:',
                                                'settore', self.asset_type)

        self.add_multiple_values_widget_external(currency_id, "Scegli la valuta dell'azione:",
                                                'valuta', self.asset_type)

        self.add_multiple_values_widget_external(nation_id, 'Scegli la nazione di appartenenza:',
                                                'nazione', self.asset_type)

        self.add_single_value_widget(price_id, 'Inserisci il prezzo di vendita:')

        self.add_single_value_widget(tax_id, 'Inserisci la tassazione applicata alla transazione:')

        self.add_single_value_widget(quantity_id, 'Inserisci la quantità di azioni vendute:')

        self.add_single_value_widget(commission_id, 'Inserisci la commisione sulla transazione:')

        self.add_date_widget(date_id, 'Inserisci la data della transazione:')


    def on_ok(self):
        self.commit(self.transaction, self.asset_type)


class DividendStockForm(BaseInputForm):

    def create(self):

        self.transaction = 'cedola-dividendo'
        self.asset_type = 'stock'

        self.name = 'Dividendo azioni'

        self.keypress_timeout = 5

        self.menu = self.new_menu(name='Form Menu')
        self.menu.addItem('Autocomplete', self.autocomplete_with_existing, '1')
        self.menu.addItem('Reset Form', self.clear_all_values, '2')

        self.add_single_value_widget(symbol_id, "Inserisci il simbolo dell'azione:")

        self.add_single_value_widget(denom_id, "Inserisci la denominazione dell'azione:")

        self.add_single_value_widget(isin_id, "Inserisci il ISIN dell'azione:")

        self.add_multiple_values_widget_external(account_id, 'Scegli il conto in cui si è effetuata la transazione:',
                                                'conto', self.asset_type)

        self.add_multiple_values_widget_external(owner_id, 'Scegli il proprietario del conto:',
                                                'proprietario', self.asset_type)

        self.add_multiple_values_widget_external(market_id, 'Scegli il mercato di appartenenza:',
                                                'mercato', self.asset_type)

        self.add_multiple_values_widget_external(sector_id, 'Scegli il settore di appartenenza:',
                                                'settore', self.asset_type)

        self.add_multiple_values_widget_external(currency_id, "Scegli la valuta dell'azione:",
                                                'valuta', self.asset_type)

        self.add_multiple_values_widget_external(nation_id, 'Scegli la nazione di appartenenza:',
                                                'nazione', self.asset_type)

        self.add_single_value_widget(dividend_coupon_id, "Inserisci l'ammontare lordo del dividendo:")

        self.add_single_value_widget(tax_id, 'Inserisci la tassazione applicata alla transazione:')

        self.add_date_widget(date_id, 'Inserisci la data della transazione:')

    def on_ok(self):
        self.commit(self.transaction, self.asset_type)
'''
BOND FORM CLASSES
'''


class BuyBondForm(BaseInputForm):

    def create(self):

        self.transaction = 'acquisto'
        self.asset_type = 'bond'

        self.name = 'Acquisto obbligazioni'

        self.keypress_timeout = 5

        self.menu = self.new_menu(name='Form Menu')
        self.menu.addItem('Autocomplete', self.autocomplete_with_existing, '1')
        self.menu.addItem('Reset Form', self.clear_all_values, '2')

        self.add_single_value_widget(symbol_id, "Inserisci il simbolo dell'obbligazione:")

        self.add_single_value_widget(denom_id, "Inserisci la denominazione dell'obbligazione:")

        self.add_single_value_widget(isin_id, "Inserisci il ISIN dell'obbligazione:")

        self.add_multiple_values_widget(type_id, 'Scegli il tipo', ['annuale', 'semestrale'])
        self.add_multiple_values_widget_external(account_id, 'Scegli il conto in cui si è effetuata la transazione:',
                                                'conto', self.asset_type)

        self.add_multiple_values_widget_external(owner_id, 'Scegli il proprietario del conto:',
                                                'proprietario', self.asset_type)

        self.add_multiple_values_widget_external(market_id, 'Scegli il mercato di appartenenza:',
                                                'mercato', self.asset_type)

        self.add_multiple_values_widget_external(currency_id, "Scegli la valuta dell'obbligazione:",
                                                'valuta', self.asset_type)

        self.add_multiple_values_widget_external(nation_id, 'Scegli la nazione di appartenenza:',
                                                'nazione', self.asset_type)

        self.add_single_value_widget(price_id, 'Inserisci il prezzo di acquisto:')

        self.add_single_value_widget(price_issued_id, 'Inserisci il prezzo di emissione:')

        self.add_single_value_widget(quantity_id, 'Inserisci la quantità di azioni comprate:')

        self.add_single_value_widget(dividend_coupon_id, 'Inserisci la percentuale della cedola:')

        self.add_single_value_widget(commission_id, 'Inserisci la commisione sulla transazione:')

        self.add_single_value_widget(tax_id, 'Inserisci la tassazione applicata:')

        self.add_date_widget(date_id, 'Inserisci la data valuta della transazione:')

        self.add_date_widget(date_issued_id, 'Inserisci la data della emissione:')

        self.add_date_widget(date_refund_id, 'Inserisci la data della rimborso:')

    def on_ok(self):
        self.commit(self.transaction, self.asset_type)

class SellBondForm(BaseInputForm):

    def create(self):

        self.transaction = 'vendita'
        self.asset_type = 'bond'

        self.name = 'vendita obbligazioni'

        self.keypress_timeout = 5

        self.menu = self.new_menu(name='Form Menu')
        self.menu.addItem('Autocomplete', self.autocomplete_with_existing, '1')
        self.menu.addItem('Reset Form', self.clear_all_values, '2')

        self.add_single_value_widget(symbol_id, "Inserisci il simbolo dell'obbligazione:")

        self.add_single_value_widget(denom_id, "Inserisci la denominazione dell'obbligazione:")

        self.add_single_value_widget(isin_id, "Inserisci il ISIN dell'obbligazione:")

        self.add_multiple_values_widget(type_id, 'Scegli il tipo', ['annuale', 'semestrale'])
        self.add_multiple_values_widget_external(account_id, 'Scegli il conto in cui si è effetuata la transazione:',
                                                'conto', self.asset_type)

        self.add_multiple_values_widget_external(owner_id, 'Scegli il proprietario del conto:',
                                                'proprietario', self.asset_type)

        self.add_multiple_values_widget_external(market_id, 'Scegli il mercato di appartenenza:',
                                                'mercato', self.asset_type)

        self.add_multiple_values_widget_external(currency_id, "Scegli la valuta dell'obbligazione:",
                                                'valuta', self.asset_type)

        self.add_multiple_values_widget_external(nation_id, 'Scegli la nazione di appartenenza:',
                                                'nazione', self.asset_type)

        self.add_single_value_widget(price_id, 'Inserisci il prezzo di vendita:')

        self.add_single_value_widget(quantity_id, 'Inserisci la quantità di azioni vendute:')

        self.add_single_value_widget(commission_id, 'Inserisci la commisione sulla transazione:')

        self.add_single_value_widget(tax_id, 'Inserisci la tassazione applicata:')

        self.add_date_widget(date_id, 'Inserisci la data valuta della transazione:')


    def on_ok(self):
        self.commit(self.transaction, self.asset_type)


class CouponBondForm(BaseInputForm):

    def create(self):

        self.transaction = 'cedola-dividendo'
        self.asset_type = 'bond'

        self.name = 'Cedola obbligazioni'

        self.keypress_timeout = 5

        self.menu = self.new_menu(name='Form Menu')
        self.menu.addItem('Autocomplete', self.autocomplete_with_existing, '1')
        self.menu.addItem('Reset Form', self.clear_all_values, '2')

        self.add_single_value_widget(symbol_id, "Inserisci il simbolo dell'obbligazione:")

        self.add_single_value_widget(denom_id, "Inserisci la denominazione dell'obbligazione:")

        self.add_single_value_widget(isin_id, "Inserisci il ISIN dell'obbligazione:")

        self.add_multiple_values_widget(type_id, 'Scegli il tipo', ['annuale', 'semestrale'])
        self.add_multiple_values_widget_external(account_id, 'Scegli il conto in cui si è effetuata la transazione:',
                                                'conto', self.asset_type)

        self.add_multiple_values_widget_external(owner_id, 'Scegli il proprietario del conto:',
                                                'proprietario', self.asset_type)

        self.add_multiple_values_widget_external(market_id, 'Scegli il mercato di appartenenza:',
                                                'mercato', self.asset_type)

        self.add_multiple_values_widget_external(currency_id, "Scegli la valuta dell'obbligazione:",
                                                'valuta', self.asset_type)

        self.add_multiple_values_widget_external(nation_id, 'Scegli la nazione di appartenenza:',
                                                'nazione', self.asset_type)

        self.add_single_value_widget(price_id, "Inserisci l'importo della cedola:")

        self.add_single_value_widget(tax_id, 'Inserisci la tassazione applicata:')

        self.add_date_widget(date_id, 'Inserisci la data valuta della transazione:')

    def on_ok(self):
        self.commit(self.transaction, self.asset_type)

class CurrencyForm(BaseInputForm):
    '''not functional needs better implementation'''
    def create(self):

        self.asset_type = 'currency'

        self.name = 'Cambio valuta'

        self.keypress_timeout = 5

        self.menu = self.new_menu(name='Form Menu')
        self.menu.addItem('Reset Form', self.clear_all_values, '1')


        symbol_data = self.parentApp.myRisparmi.get_asset_values_list(
            self.asset_type, symbol_id)
        symbol_data.append('altro...')
        self.account = self.add_widget_intelligent(
            npyscreen.TitleSelectOne, w_id=symbol_id, name='Scegli il simbolo:', max_width=50, max_height=6)
        self.account.values = symbol_data

        self.nextrely += 1

        d_name = "Inserisci la denominazione della divisa:"
        self.denom = self.add_widget_intelligent(
            npyscreen.TitleText, w_id=denom_id, name=d_name, begin_entry_at=len(d_name) + 1, use_two_lines=False)

        self.nextrely += 1

        account_data = self.parentApp.myRisparmi.get_asset_values_list(
            self.asset_type, account_id)
        account_data.append('altro...')
        self.account = self.add_widget_intelligent(
            npyscreen.TitleSelectOne, w_id=account_id, name='Scegli il conto in cui si è effetuata la transazione:', max_width=50, max_height=10)
        self.account.values = account_data

        self.nextrely += 1

        t_name = 'Inserisci la tipologia di transazione:'
        self.currency_transaction = self.add_widget_intelligent(
            npyscreen.TitleSelectOne, w_id=transaction_id, name=t_name, values=['acquisto', 'vendita'], max_width=50, max_height=3)

        self.nextrely += 1

        p_name = 'Inserisci il prezzo di vendita:'
        self.price = self.add_widget_intelligent(
            npyscreen.TitleText, w_id=price_id, name=p_name, begin_entry_at=len(p_name) + 1, use_two_lines=False)

        self.nextrely += 1

        q_name = 'Inserisci la quantità di obbligazioni vendute:'
        self.quantity = self.add_widget_intelligent(
            npyscreen.TitleText, w_id=quantity_id, name=q_name, begin_entry_at=len(q_name) + 1, use_two_lines=False)

        self.nextrely += 1

        owner_data = self.parentApp.myRisparmi.get_asset_values_list(
            self.asset_type, owner_id)
        owner_data.append('altro...')
        self.owner = self.add_widget_intelligent(
            npyscreen.TitleSelectOne, w_id=owner_id, name='Scegli il proprietario del conto:', max_width=50, max_height=5)
        self.owner.values = owner_data

        self.nextrely += 1

        da_name = 'Inserisci la data della transazione:'
        self.date = self.add_widget_intelligent(
            npyscreen.TitleDateCombo, w_id=date_id, name=da_name, begin_entry_at=len(da_name) + 1, use_two_lines=False)

    def on_ok(self):
        missing_values = {}

        choice = npyscreen.notify_yes_no('Vuoi aggiungere questa transazione?')
        values=self.collect_form_values(missing_values)

        if choice:
            if values:
                self.parentApp.myRisparmi.add_asset_transaction(
                    values, self.asset_type)
                self.parentApp.setNextForm('MAIN')
                self.parentApp.removeForm(self.parentApp.active_form_id)
            else:
                npyscreen.notify_wait('Il form non è completo')

class CashForm(BaseInputForm):
    '''not functional needs better implementation'''

    def create(self):

        self.asset_type = 'cash'

        self.name = 'Movimenti conto'

        self.keypress_timeout = 5

        self.menu = self.new_menu(name='Form Menu')
        self.menu.addItem('Reset Form', self.clear_all_values, '1')

        account_data = self.parentApp.myRisparmi.get_asset_values_list(
            self.asset_type, account_id)
        account_data.append('altro...')
        self.account = self.add_widget_intelligent(
            npyscreen.TitleSelectOne, w_id=account_id, name='Scegli il conto in cui si è effetuata la transazione:', max_width=50, max_height=10)
        self.account.values = account_data

        self.nextrely += 1

        ds_name = 'Inserisci la descrizione:'
        self.description = self.add_widget_intelligent(
            npyscreen.TitleText, w_id=description_id, name=ds_name, begin_entry_at=len(ds_name) + 1, use_two_lines=False)

        self.nextrely += 1

        am_name = "Inserisci l'importo:"
        self.amount = self.add_widget_intelligent(
            npyscreen.TitleText, w_id=amount_id, name=am_name, begin_entry_at=len(am_name) + 1, use_two_lines=False)

        self.nextrely += 1

        t_name = 'Inserisci la tipologia di transazione:'
        self.currency_transaction = self.add_widget_intelligent(
            npyscreen.TitleSelectOne, w_id=transaction_id, name=t_name, values=['entrata', 'uscita', 'trasferimento'], max_width=50, max_height=4)

        self.nextrely += 1

        sector_data = self.parentApp.myRisparmi.get_asset_values_list(
            self.asset_type, sector_id)
        sector_data.append('altro...')
        self.sector = self.add_widget_intelligent(
            npyscreen.TitleSelectOne, w_id=sector_id, name='Scegli la categoria del movimento:', max_width=50, max_height=15)
        self.sector.values = sector_data

        self.nextrely += 1

        owner_data = self.parentApp.myRisparmi.get_asset_values_list(
            self.asset_type, owner_id)
        owner_data.append('altro...')
        self.owner = self.add_widget_intelligent(
            npyscreen.TitleSelectOne, w_id=owner_id, name='Scegli il proprietario del conto:', max_width=50, max_height=5)
        self.owner.values = owner_data

        self.nextrely += 1

        da_name = 'Inserisci la data valuta della transazione:'
        self.date = self.add_widget_intelligent(
            npyscreen.TitleDateCombo, w_id=date_id, name=da_name, begin_entry_at=len(da_name) + 1, use_two_lines=False)

    def on_ok(self):
        missing_values = {}

        choice = npyscreen.notify_yes_no('Vuoi aggiungere questa transazione?')
        values=self.collect_form_values(missing_values)

        if choice:
            if values:
                self.parentApp.myRisparmi.add_asset_transaction(
                    values, self.asset_type)
                self.parentApp.setNextForm('MAIN')
                self.parentApp.removeForm(self.parentApp.active_form_id)
            else:
                npyscreen.notify_wait('Il form non è completo')
