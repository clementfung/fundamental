#from dateutil.relativedelta import relativedelta


def add_months_to_today(months_to_add):
    #return str(date.today() + relativedelta(months = + months_to_add ))

    return '2015-01-01'


def calculate_investment(annum_i, monthly_term, prinicipal):
    return (annum_i / 100 * monthly_term / 12 + 1) * prinicipal 
