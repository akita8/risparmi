class Config:

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
    type_id = 'tipologia' #per bond
    price_issued_id = 'prezzo_emissione' #per bond
    date_issued_id = 'data_emissione' #per bond
    date_refund_id = 'data_rimborso'
    transaction_id = 'transazione'  # serve per currency
    description_id = 'descrizione'# serve per cash
    amount_id ='importo'# serve per cash

    '''
    LISTS OF WIDGET ID DECLARATION
    '''

    popup_id_list = [market_id, sector_id,
                     currency_id, nation_id, account_id, owner_id]

    multiple_autocomplete_id_list = [
        market_id, sector_id, currency_id, nation_id, account_id, owner_id]

    single_autocomplete_id_list = [symbol_id, denom_id, isin_id]

    is_number_check_id_list = [price_id, quantity_id, tax_id, commission_id,
                               amount_id, price_issued_id]

    complete_id_list = [symbol_id, denom_id, market_id, sector_id, currency_id,
                        isin_id, nation_id, account_id, price_id, type_id,
                        quantity_id, commission_id, tax_id, owner_id, date_id,
                        transaction_id, description_id, amount_id, date_refund_id,
                        price_issued_id, date_issued_id, price_issued_id,
                        dividend_coupon_id, ]

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
