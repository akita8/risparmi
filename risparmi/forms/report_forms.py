from risparmi.core.misc import npyscreen, formatted_values,stock_report_cleaned_matrix, ReportGrid, NoInputException
from risparmi.forms.popup_forms import SingleReportPopup, ResultDisplay


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
