# pylint: disable=C,R
import npyscreen
from risparmi import Risparmi

'''
FORM ID DECLARATION
'''

buy_stock_form_id='buy_stock'
sell_stock_form_id='sell_stock'
dividend_stock_form_id='dividend'
buy_bond_form_id='buy_bond'
sell_bond_form_id='sell_bond'
coupon_bond_form_id='coupon'
currency_form_id='currency'
cash_form_id='cash'
stock_report_id='stock_report'
temp_id='temp' #temporanea per la valorizzazione, devo farlo meglio!

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
                    price_id, dividend_coupon_id, quantity_id, commission_id, tax_id, owner_id, date_id, transaction_id, description_id,
                    amount_id, type_id, price_issued_id, date_issued_id, price_issued_id, date_refund_id]

'''
MAIN APP
'''


class Interface(npyscreen.NPSAppManaged):



    def onStart(self):
        # pylint: disable=W
        self.myRisparmi = Risparmi()
        self.addForm("MAIN", MainForm)


    def form_creation(self, form_id):
        # pylint: disable=W
        self.active_form_id=form_id

        if form_id==buy_stock_form_id:
            self.addForm(form_id, BuyStockForm)
        elif form_id==sell_stock_form_id:
            self.addForm(form_id, SellStockForm)
        elif form_id==dividend_stock_form_id:
            self.addForm(form_id, DividendStockForm)
        elif form_id==buy_bond_form_id:
            self.addForm(form_id, BuyBondForm)
        elif form_id==sell_bond_form_id:
            self.addForm(form_id, SellBondForm)
        elif form_id==coupon_bond_form_id:
            self.addForm(form_id, CouponBondForm)
        elif form_id==currency_form_id:
            self.addForm(form_id, CurrencyForm)
        elif form_id==cash_form_id:
            self.addForm(form_id, CashForm)
        elif form_id==stock_report_id:
            self.addForm(stock_report_id, ReportVisualization)
        elif form_id==temp_id:
            self.addForm(temp_id, ValorizationVisualization)

'''
USEFUL FUNCTIONS
'''
def is_number(number):
    try:
        return bool(float(number))
    except (ValueError, TypeError):
        return False

def formatted_values(values_dict):
    values=[]
    for element in values_dict:
        values.append(str(element)+' : '+str(values_dict[element]))
    return values

def stock_report_cleaned_matrix(values):

    cleaned_list=[[values[0][i] for i in range(len(values[0]))]]
    for i in range(1, len(values)):
        line=[]
        for j, cell in enumerate(values[i]):
            if cell!=values[i-1][j] or cell==0:
                if j!=1:
                    try:
                        cell=float("{0:.4f}".format(cell)) #per la precisione
                    except (TypeError, ValueError):
                        pass
                line.append(cell)
            else:
                line.append('')
        cleaned_list.append(line)
    return cleaned_list

'''
GRID CLASSES
'''
class ReportGrid(npyscreen.GridColTitles):
    default_column_number = 10

'''
MAIN FORM CLASS
'''


class MainForm(npyscreen.FormBaseNewWithMenus):

    # MENU_KEY='Q'  #per cambiare la chiave di accesso per il menu

    def create(self):


        self.active_stock_report_grid_creation()

        self.menu = self.new_menu(name='Menu principale')
        self.submenu_t = self.menu.addNewSubmenu('aggiungi transazione', '1')

        self.submenu_ts = self.submenu_t.addNewSubmenu('azione', '1')
        self.submenu_ts.addItemsFromList([('acquisto', self.to_buy_stock_form, '1'), (
            'vendita', self.to_sell_stock_form, '2'), ('dividendo', self.to_dividend_stock_form, '3')])

        self.submenu_tb = self.submenu_t.addNewSubmenu('obbligazione', '2')
        self.submenu_tb.addItemsFromList([('acquisto', self.to_buy_bond_form, '1'), (
            'vendita', self.to_sell_bond_form, '2'), ('cedola', self.to_coupon_bond_form, '3')])

        self.submenu_t.addItem('currency', self.to_currency_form, '3')
        self.submenu_t.addItem('cash', self.to_cash_form, '4')

        self.submenu_sr = self.menu.addNewSubmenu('mostra report', '2')
        self.submenu_sr.addItem('stock', self.to_stock_report, '1')
        self.submenu_sr.addItem('bond', self.temp, '2')

        self.menu.addItem('valorizzazione e cambi', self.to_valorization, '3')
        self.menu.addItem('aggiorna', self.update_internal_values, '4')
        self.menu.addItem('salva', self.save, '5')
        self.menu.addItem('esci', self.exit, '6')

    def active_stock_report_grid_creation(self):
        report=self.parentApp.myRisparmi.active_stock_report.copy()

        values=report.to_records()
        index_name=list(report.index.names)
        columns_name=list(report.columns)
        cleaned_matrix=stock_report_cleaned_matrix(values)

        if not hasattr(self, 'grid'):
            # pylint: disable=W
            self.grid = self.add(ReportGrid, col_titles=index_name+columns_name, values=cleaned_matrix, select_whole_line=True)
        else:
            self.grid.values=cleaned_matrix
            self.grid.display()

    def temp(self):
        npyscreen.notify_confirm(self.parentApp.myRisparmi.bond_report.to_string())
    def to_dividend_stock_form(self):
        self.parentApp.form_creation(dividend_stock_form_id)
        self.parentApp.setNextForm(dividend_stock_form_id)
        self.parentApp.switchFormNow()

    def to_sell_stock_form(self):
        self.parentApp.form_creation(sell_stock_form_id)
        self.parentApp.setNextForm(sell_stock_form_id)
        self.parentApp.switchFormNow()

    def to_buy_stock_form(self):
        self.parentApp.form_creation(buy_stock_form_id)
        self.parentApp.setNextForm(buy_stock_form_id)
        self.parentApp.switchFormNow()

    def to_coupon_bond_form(self):
        self.parentApp.form_creation(coupon_bond_form_id)
        self.parentApp.setNextForm(coupon_bond_form_id)
        self.parentApp.switchFormNow()

    def to_sell_bond_form(self):
        self.parentApp.form_creation(sell_bond_form_id)
        self.parentApp.setNextForm(sell_bond_form_id)
        self.parentApp.switchFormNow()

    def to_buy_bond_form(self):
        self.parentApp.form_creation(buy_bond_form_id)
        self.parentApp.setNextForm(buy_bond_form_id)
        self.parentApp.switchFormNow()

    def to_currency_form(self):
        self.parentApp.form_creation(currency_form_id)
        self.parentApp.setNextForm(currency_form_id)
        self.parentApp.switchFormNow()

    def to_cash_form(self):
        self.parentApp.form_creation(cash_form_id)
        self.parentApp.setNextForm(cash_form_id)
        self.parentApp.switchFormNow()

    def to_valorization(self):
        self.parentApp.form_creation(temp_id)
        self.parentApp.setNextForm(temp_id)
        self.parentApp.switchFormNow()

    def to_stock_report(self):
        self.parentApp.myRisparmi.stock_report_gen()
        self.parentApp.form_creation(stock_report_id)
        self.parentApp.setNextForm(stock_report_id)
        self.parentApp.switchFormNow()

    def update_internal_values(self):
        self.parentApp.myRisparmi.updated_assets_values_gen(True)
        self.parentApp.myRisparmi.stock_report_gen()
        self.active_stock_report_grid_creation()

    def save(self):
        self.parentApp.myRisparmi.save_to_csv()

    def exit(self):
        self.parentApp.myRisparmi.save_to_csv()
        self.parentApp.setNextForm(None)
        self.editing = False
        self.parentApp.switchFormNow()

'''
COSTUM ERROR DECLARATION
'''

class NoInputException(Exception):
    pass

'''
POPUP CLASSES
'''

class SimplePopup(npyscreen.ActionPopup):

    def on_cancel(self):
        raise NoInputException


class NotInChoicesPopup(SimplePopup):

    def create(self):
        self.name = 'Inserisci un altro valore'
        self.question = self.add(npyscreen.Textfield, begin_entry_at=0)


class AutocompletePopup(SimplePopup):

    def create(self):
        self.name = 'Inserisci il simbolo'
        self.question = self.add(npyscreen.Textfield, begin_entry_at=0)

class SingleReportPopup(SimplePopup):

    def create(self):
        self.keypress_timeout=10
        self.name = 'Inserisci il simbolo'
        p_name='Simbolo:'
        self.question = self.add(npyscreen.TitleText, name=p_name, begin_entry_at=len(p_name)+1, use_two_lines=False)


class ResultDisplay(npyscreen.Popup):

    def create(self):
        self.pager=self.add(npyscreen.Pager)

'''
VISUALIZATION FORM CLASSES
'''
class ReportVisualization(npyscreen.FormWithMenus):

    def create(self):

        self.name='Stock Report'

        report=self.parentApp.myRisparmi.stock_report.copy()

        values=report.to_records()
        index_name=list(report.index.names)
        columns_name=list(report.columns)
        cleaned_matrix=stock_report_cleaned_matrix(values)


        self.grid = self.add(ReportGrid, col_titles=index_name+columns_name, values=cleaned_matrix, select_whole_line=True)

        self.menu = self.new_menu(name='Stock Report Menu')
        self.menu.addItem('Report per titolo', self.single_report, '1')

    def single_report(self):

        try:
            pop = SingleReportPopup()
            pop.center_on_display()
            pop.edit()

            values=self.parentApp.myRisparmi.get_single_stock_report(pop.question.value)

            rdy_values=formatted_values(values)

            pop1 = ResultDisplay()
            pop1.center_on_display()
            pop1.name=pop.question.value
            pop1.pager.values=rdy_values
            pop1.edit()

        except (NoInputException, TypeError):
            pass


    def afterEditing(self):
        self.parentApp.setNextForm('MAIN')
        self.parentApp.removeForm(self.parentApp.active_form_id)


class ValorizationVisualization(npyscreen.Form): #temporanea

    def create(self):

        self.name='Valorizzazioni e cambi'

        a_values=formatted_values(self.parentApp.myRisparmi.stock_val_account)
        self.val_account=self.add(npyscreen.TitlePager, name='Valorizzazione conti', values=a_values, max_width=50, max_height=len(a_values))

        self.nextrely+=1

        s_values=formatted_values(self.parentApp.myRisparmi.stock_val_sector)
        self.val_sector=self.add(npyscreen.TitlePager, name='Valorizzazione settori', values=s_values, max_width=50, max_height=len(s_values))

        self.nextrely+=1

        c_values=formatted_values(self.parentApp.myRisparmi.get_exchange_rate())
        self.val_exchange_rate=self.add(npyscreen.TitlePager, name='Cambi', values=c_values, max_width=50, max_height=len(c_values))

        self.nextrely+=1






    def afterEditing(self):
        self.parentApp.setNextForm('MAIN')
        self.parentApp.removeForm(self.parentApp.active_form_id)


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

        self.add_multiple_values_widget(type_id, 'Scegli il tipo', ['annuale', 'semstrale'])
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

        s_name = "Inserisci il simbolo dell'obbligazione:"
        self.symbol = self.add_widget_intelligent(
            npyscreen.TitleText, w_id=symbol_id,  name=s_name, begin_entry_at=len(s_name) + 1, use_two_lines=False)

        self.nextrely += 1

        d_name = "Inserisci la denominazione dell'obbligazione:"
        self.denom = self.add_widget_intelligent(
            npyscreen.TitleText, w_id=denom_id, name=d_name, begin_entry_at=len(d_name) + 1, use_two_lines=False)

        self.nextrely += 1

        market_data = self.parentApp.myRisparmi.get_asset_values_list(
            self.asset_type, market_id)
        market_data.append('altro...')
        self.market = self.add_widget_intelligent(
            npyscreen.TitleSelectOne, w_id=market_id, name='Scegli il mercato di appartenenza:', max_width=50, max_height=8)
        self.market.values = market_data

        self.nextrely += 1

        currency_data = self.parentApp.myRisparmi.get_asset_values_list(
            self.asset_type, currency_id)
        currency_data.append('altro...')

        self.currency = self.add_widget_intelligent(
            npyscreen.TitleSelectOne, w_id=currency_id, name="Scegli la valuta dell'obbligazione:", max_width=50, max_height=5)
        self.currency.values = currency_data

        self.nextrely += 1

        i_name = "Inserisci il ISIN dell'obbligazione:"
        self.isin = self.add_widget_intelligent(
            npyscreen.TitleText, w_id=isin_id, name=i_name, begin_entry_at=len(i_name) + 1, use_two_lines=False)

        self.nextrely += 1

        nation_data = self.parentApp.myRisparmi.get_asset_values_list(
            self.asset_type, nation_id)
        nation_data.append('altro...')
        self.nation = self.add_widget_intelligent(
            npyscreen.TitleSelectOne, w_id=nation_id, name='Scegli la nazione di appartenenza:', max_width=50, max_height=10)
        self.nation.values = nation_data

        self.nextrely += 1

        account_data = self.parentApp.myRisparmi.get_asset_values_list(
            self.asset_type, account_id)
        account_data.append('altro...')
        self.account = self.add_widget_intelligent(
            npyscreen.TitleSelectOne, w_id=account_id, name='Scegli il conto in cui si è effetuata la transazione:', max_width=50, max_height=10)
        self.account.values = account_data

        self.nextrely += 1

        p_name = 'Inserisci il prezzo di vendita:'
        self.price = self.add_widget_intelligent(
            npyscreen.TitleText, w_id=price_id, name=p_name, begin_entry_at=len(p_name) + 1, use_two_lines=False)

        self.nextrely += 1

        q_name = 'Inserisci la quantità di obbligazioni vendute:'
        self.quantity = self.add_widget_intelligent(
            npyscreen.TitleText, w_id=quantity_id, name=q_name, begin_entry_at=len(q_name) + 1, use_two_lines=False)

        self.nextrely += 1

        t_name = 'Inserisci la percentuale di tassazione applicata sulla transazione:'
        self.commission = self.add_widget_intelligent(
            npyscreen.TitleText, w_id=tax_id, name=t_name, begin_entry_at=len(t_name) + 1, use_two_lines=False)

        self.nextrely += 1

        c_name = 'Inserisci la commisione sulla transazione:'
        self.commission = self.add_widget_intelligent(
            npyscreen.TitleText, w_id=commission_id, name=c_name, begin_entry_at=len(c_name) + 1, use_two_lines=False)

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
        missing_values = {'transazione': self.transaction,
                          exchange_rate_id: '', dividend_coupon_id: ''}

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


class CouponBondForm(BaseInputForm):

    def create(self):

        self.transaction = 'cedola-dividendo'
        self.asset_type = 'bond'

        self.name = 'Cedola obbligazioni'

        self.keypress_timeout = 5

        self.menu = self.new_menu(name='Form Menu')
        self.menu.addItem('Autocomplete', self.autocomplete_with_existing, '1')
        self.menu.addItem('Reset Form', self.clear_all_values, '2')

        s_name = "Inserisci il simbolo dell'obbligazione:"
        self.symbol = self.add_widget_intelligent(
            npyscreen.TitleText, w_id=symbol_id,  name=s_name, begin_entry_at=len(s_name) + 1, use_two_lines=False)

        self.nextrely += 1

        d_name = "Inserisci la denominazione dell'obbligazione:"
        self.denom = self.add_widget_intelligent(
            npyscreen.TitleText, w_id=denom_id, name=d_name, begin_entry_at=len(d_name) + 1, use_two_lines=False)

        self.nextrely += 1

        market_data = self.parentApp.myRisparmi.get_asset_values_list(
            self.asset_type, market_id)
        market_data.append('altro...')
        self.market = self.add_widget_intelligent(
            npyscreen.TitleSelectOne, w_id=market_id, name='Scegli il mercato di appartenenza:', max_width=50, max_height=8)
        self.market.values = market_data

        self.nextrely += 1

        currency_data = self.parentApp.myRisparmi.get_asset_values_list(
            self.asset_type, currency_id)
        currency_data.append('altro...')

        self.currency = self.add_widget_intelligent(
            npyscreen.TitleSelectOne, w_id=currency_id, name="Scegli la valuta dell'obbligazione:", max_width=50, max_height=5)
        self.currency.values = currency_data

        self.nextrely += 1

        i_name = "Inserisci il ISIN dell'obbligazione:"
        self.isin = self.add_widget_intelligent(
            npyscreen.TitleText, w_id=isin_id, name=i_name, begin_entry_at=len(i_name) + 1, use_two_lines=False)

        self.nextrely += 1

        nation_data = self.parentApp.myRisparmi.get_asset_values_list(
            self.asset_type, nation_id)
        nation_data.append('altro...')
        self.nation = self.add_widget_intelligent(
            npyscreen.TitleSelectOne, w_id=nation_id, name='Scegli la nazione di appartenenza:', max_width=50, max_height=10)
        self.nation.values = nation_data

        self.nextrely += 1

        account_data = self.parentApp.myRisparmi.get_asset_values_list(
            self.asset_type, account_id)
        account_data.append('altro...')
        self.account = self.add_widget_intelligent(
            npyscreen.TitleSelectOne, w_id=account_id, name='Scegli il conto in cui si è effetuata la transazione:', max_width=50, max_height=10)
        self.account.values = account_data

        self.nextrely += 1

        t_name = 'Inserisci la percentuale di tassazione applicata sulla transazione:'
        self.commission = self.add_widget_intelligent(
            npyscreen.TitleText, w_id=tax_id, name=t_name, begin_entry_at=len(t_name) + 1, use_two_lines=False)

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
        missing_values = {'transazione': self.transaction, exchange_rate_id: '',
                          commission_id: '', price_id: '', quantity_id: '', dividend_coupon_id:''}

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


class CurrencyForm(BaseInputForm):

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

if __name__ == '__main__':
    IT = Interface()
    IT.run()
