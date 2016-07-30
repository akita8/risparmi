from npyscreen import ActionPopup, Popup, Pager, Textfield, TitleText
from risparmi.misc import NoInputException
'''
POPUP CLASSES
'''


class SimplePopup(ActionPopup):

    def on_cancel(self):
        raise NoInputException


class NotInChoicesPopup(SimplePopup):

    def create(self):
        self.name = 'Inserisci un altro valore'
        self.question = self.add(Textfield, begin_entry_at=0)


class AutocompletePopup(SimplePopup):

    def create(self):
        self.name = 'Inserisci il simbolo'
        self.question = self.add(Textfield, begin_entry_at=0)


class SingleReportPopup(SimplePopup):

    def create(self):
        self.keypress_timeout = 10
        self.name = 'Inserisci il simbolo'
        p_name = 'Simbolo:'
        self.question = self.add(TitleText, name=p_name, begin_entry_at=len(
            p_name) + 1, use_two_lines=False)


class ResultDisplay(Popup):

    def create(self):
        self.pager = self.add(Pager)
