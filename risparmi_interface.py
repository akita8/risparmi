# pylint: disable=C,R
import npyscreen
from risparmi_modules import *

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
            self.addForm(form_id, ReportVisualization)
        elif form_id==temp_id:
            self.addForm(form_id, ValorizationVisualization)


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


if __name__ == '__main__':
    IT = Interface()
    IT.run()
