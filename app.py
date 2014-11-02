import os
from flask import Flask, render_template, request, jsonify, make_response
import db
import venmo
import uuid
import util
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)

account_collection_str = "account_info"
new_investments_str = "new_investments"
bought_investments_str = "bought_investments"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def hello():
    return make_response(open('%s/templates/index.html' % BASE_DIR).read())

@app.route('/api/test')
def test():
    print 'trying to query database'
    return str(db.test_connection())

#### SHARED APIS ######################################

@app.route('/account/info/<venmo_name>', methods=['GET'])
def getAccountInfo(venmo_name):

    account_info = db.find_one(account_collection_str, {"user_id" : str(venmo_name)})

    if account_info is None:
        return jsonify(**{}) 

    return jsonify(**{
         "user_name" : account_info['user_name'],
         "chequing_balance" : account_info['chequing_balance'],
         "savings_balance" : account_info['savings_balance'],
         "allowance_amount" : account_info['allowance_amount'],
         "debt_amount" : account_info['debt_amount'],
         "savings_amount" : account_info['savings_amount'],
         "savings_interest_rate" : account_info['savings_interest_rate'],
         "loan_interest_rate" : account_info['loan_interest_rate']
         })

@app.route('/register')
def register():

    venmo_id = request.form['venmo_name']
    name = request.form['user_name']
    p_venmo_id = request.form['parent_venmo_name']
    p_name = request.form['parent_name']

    account_collection = db.get_collection(account_collection_str)
    account_collection.insert({
        "user_id" : venmo_id,
        "user_name" : name,
        "chequing_balance" : 0,
        "savings_balance" : 0,
        "parent_id" : p_venmo_id,
        "parent_name" : p_name,
        "allowance_amount" : 0,
        "savings_amount" : 0,
        "savings_interest_rate" : 0, 
        "debt_amount" : 0,
        "loan_interest_rate" : 0,
        "user_token": "u_token",
        "access_token": "a_token",
        "refresh_token": "r_token"
        })
    # TODO: Venmo fields are totally sucky

    return jsonify(**{
        "success": True
        })

#### MOBILE APIS ########################################

@app.route('/account/savings_amount', methods=['POST'])
def setSavingsAmount():

    venmo_id = request.form['venmo_name']
    savings_amount = float(request.form['amount'])

    # post as long as value is 0
    if savings_amount < 0:    
        return jsonify(**{
            "success": False
            })

    else:        
        account_info = db.get_collection(account_collection_str)
        account_info.update({"user_id" : venmo_id}, 
            {"$set": {"savings_amount": savings_amount}})
    
    return jsonify(**{
        "success": True
        })

@app.route('/account/withdraw', methods=['POST'])
def withdrawAmount():

    venmo_id = request.form['venmo_name']
    withdraw_amount = float(request.form['amount'])

    account_info = db.get_collection(account_collection_str)
    account_info_record = account_info.find_one({"user_id" : venmo_id})
    current_amount = account_info_record['chequing_balance']

    if (withdraw_amount > current_amount):
        return jsonify(**{
            "success": False
            })
    else:
        print venmo.post_payment(
            account_info_record['access_token'],
            venmo_id,
            'Cash out made',
            withdraw_amount,
        ) 
        current_amount = current_amount - withdraw_amount
        account_info.update({"user_id" : venmo_id},
                {"$set": {"chequing_balance" : current_amount}})

    return jsonify(**{
        "success": True
        })

@app.route('/account/take_loan', methods=['POST'])
def takeLoan():

    venmo_id = request.form['venmo_name']
    loan_amount = float(request.form['amount'])

    account_info = db.get_collection(account_collection_str)
    account_info_record = account_info.find_one({"user_id" : venmo_id})
    current_chequing = account_info_record['chequing_balance']
    current_debt = account_info_record['debt_amount']

    if (loan_amount < 0):
        return jsonify(**{
            "success": False
            })

    current_chequing += loan_amount;
    current_debt += loan_amount; 
    account_info.update({"user_id" : venmo_id},
            {"$set": {
                "chequing_balance" : current_chequing,
                "debt_amount" : current_debt
                }})

    return jsonify(**{
        "success" : True
        })

@app.route('/account/pay_loan', methods=['POST'])
def payLoan():

    venmo_id = request.form['venmo_name']
    payment_amount = float(request.form['amount'])

    account_info = db.get_collection(account_collection_str)
    account_info_record = account_info.find_one({"user_id" : venmo_id})
    current_chequing = account_info_record['chequing_balance']
    current_debt = account_info_record['debt_amount']

    # Need to be careful to maintain good state
    if (payment_amount < 0 or payment_amount > current_chequing or payment_amount > current_debt):
        return jsonify(**{
            "success": False
            })

    current_chequing -= payment_amount;
    current_debt -= payment_amount; 
    account_info.update({"user_id" : venmo_id},
            {"$set": {
                "chequing_balance" : current_chequing,
                "debt_amount" : current_debt
                }})

    return jsonify(**{
        "success" : True
        })

@app.route('/account/transfer_to_chequing', methods=['POST'])
def transferToChequing():

    venmo_id = request.form['venmo_name']
    transfer_amount = float(request.form['amount'])

    account_info = db.get_collection(account_collection_str)
    account_info_record = account_info.find_one({"user_id" : venmo_id})
    current_chequing = account_info_record['chequing_balance']
    current_savings = account_info_record['savings_balance']

    if (transfer_amount > current_savings):
        return jsonify(**{
            "success": False
            })
    else:
        current_savings = current_savings - transfer_amount;
        current_chequing = current_chequing + transfer_amount;
        account_info.update({"user_id" : venmo_id},
                {"$set": {
                    "chequing_balance" : current_chequing,
                    "savings_balance" : current_savings
                    }})

    return jsonify(**{
        "success": True
        })

@app.route('/account/transfer_to_savings', methods=['POST'])
def transferToSavings():

    venmo_id = request.form['venmo_name']
    transfer_amount = float(request.form['amount'])

    account_info = db.get_collection(account_collection_str)
    account_info_record = account_info.find_one({"user_id" : venmo_id})
    current_chequing = account_info_record['chequing_balance']
    current_savings = account_info_record['savings_balance']

    if (transfer_amount > current_chequing):
        return jsonify(**{
            "success": False
            })
    else:
        current_savings = current_savings + transfer_amount;
        current_chequing = current_chequing - transfer_amount;
        account_info.update({"user_id" : venmo_id},
                {"$set": {
                    "chequing_balance" : current_chequing,
                    "savings_balance" : current_savings
                    }})

    return jsonify(**{
        "success": True
        })

#### INVESTMENTS ##################################

def addNewInvestment(venmo_id, name, term, rate):

    new_investments_collection = db.get_collection(new_investments_str)
    investment_id = str(uuid.uuid4())
    new_investments_collection.insert({
        "user_id": venmo_id,
        "name": name,
        "term_length" : term,
        "rate" : rate,
        "investment_id": investment_id,
        "is_purchased": False,
        })
 
def addBoughtInvestment(user_id, investment_id, amount):
    new_investments_collection = db.get_collection(new_investments_str)

    new_investments_collection.update({'investment_id': investment_id},
                                                   {"$set": {"is_purchased" : True}})
    investment = new_investments_collection.find_one({'investment_id': investment_id})
    term_length = int(investment['term_length'])
    rate = float(investment['rate'])

    bought_investments_collection = db.get_collection(bought_investments_str)
    bought_investments_collection.insert({
        "name" : investment['name'],
        "term_length": term_length,
        "rate": investment['rate'],
        "end_date": util.add_months_to_today(term_length),
        "amount": amount,
        "final_amount": util.calculate_investment(rate, term_length, amount), 
        "is_redeemed": False,
        "investment_id": investment_id,
        "user_id": user_id,
        })

@app.route('/account/investment/new', methods=['POST'])
def setNewInvestment():
    venmo_id = request.form['venmo_name']
    rate = float(request.form['rate'])
    name = request.form['name']
    term_length = int(request.form['term_length'])
    
    # post as long as value is 0
    if rate < 0:    
        return jsonify(**{
            "success": False
            })

    else:        
        addNewInvestment(venmo_id, name, term_length, rate)

              
    return jsonify(**{
        "success": True
        })


@app.route('/account/investment/delete', methods=['POST'])
def deleteNewInvestment():
    investment_id = request.form['investment_id']

    new_investments_collection = db.get_collection(new_investments_str)

    new_investments_collection.remove({'investment_id': investment_id})

    return jsonify(**{
            "success": True
            })



@app.route('/account/investment/current', methods=['POST'])
def setCurrentInvestment():
    venmo_id = request.form['venmo_name']
    investment_id = request.form['investment_id']
    amount = float(request.form['amount']) 

    account_info = db.find_one(account_collection_str, {"user_id" : str(venmo_id)})
    current_chequing = float(account_info['chequing_balance'])
    new_investments_collection = db.get_collection(new_investments_str)

    investment  = new_investments_collection.find_one({'investment_id': investment_id})
                                                
    # post as long as value is 0
    if amount < 0 or current_chequing < amount or investment['is_purchased'] == True:
        return jsonify(**{
            "success": False
            })

    else:        
        addBoughtInvestment(venmo_id, 
                            investment_id, 
                            amount,
                            )
        new_chequing_balance = current_chequing - amount
        account_info = db.get_collection(account_collection_str)
        account_info.update({"user_id" : venmo_id},
                {"$set": {"chequing_balance" : new_chequing_balance}})


        new_investment_list = db.find(new_investments_str, {"user_id" : venmo_id, "is_purchased": False })
        current_investment_list = db.find(bought_investments_str, {"user_id" : venmo_id })

    
    return jsonify(**{
        "chequing_balance": new_chequing_balance,
        "new_investments" : new_investment_list,
        "my_investments"  : current_investment_list,
        })

@app.route('/account/investment/new/<venmo_id>', methods=['GET'])
def getNewInvestments(venmo_id):

    documents = db.find(new_investments_str, {"user_id" : venmo_id })

    return jsonify(**{
        "List": documents 
        })
     
@app.route('/account/investment/current/<venmo_id>', methods=['GET'])
def getCurrentInvestments(venmo_id):

    documents = db.find(bought_investments_str, {"user_id" : venmo_id , "is_redeemed" : False})


    return jsonify(**{
        "List": documents 
        })
    

#### WEB APIS #####################################

@app.route('/account/savings_interest', methods=['POST'])
def setSavingsInterest():

    venmo_id = request.form['venmo_name']
    rate = float(request.form['rate'])

    # post as long as value is 0
    if rate < 0:    
        return jsonify(**{
            "success": False
            })

    else:        
        account_info = db.get_collection(account_collection_str)
        account_info.update({"user_id" : venmo_id}, 
            {"$set": {"savings_interest_rate" : rate}})
    
    return jsonify(**{
        "success": True
        })

@app.route('/account/loan_interest', methods=['POST'])
def setLoanInterest():

    venmo_id = request.form['venmo_name']
    rate = float(request.form['rate'])

    # post as long as value is 0
    if rate < 0:    
        return jsonify(**{
            "success": False
            })

    else:        
        account_info = db.get_collection(account_collection_str)
        account_info.update({"user_id" : venmo_id}, 
            {"$set": {"loan_interest_rate": rate}})
    
    return jsonify(**{
        "success": True
        })

@app.route('/account/set_allowance', methods=['POST'])
def setAllowance():

    venmo_id = request.form['venmo_name']
    rate = float(request.form['rate'])

    # post as long as value is 0
    if rate < 0:    
        return jsonify(**{
            "success": False
            })

    else:        
        account_info = db.get_collection(account_collection_str)
        account_info.update({"user_id" : venmo_id}, 
            {"$set": {"allowance_amount": rate}})
    
    return jsonify(**{
        "success": True
        })

@app.route('/account/savings/history/<venmo_name>', methods=['GET'])
def getSavingsHistory(venmo_name):
    return jsonify(**{
        'row': ['10/5', '10/12', '10/19', '10/26', '11/2'],
        'amount': [180, 185, 195, 200, 240]
        })

@app.route('/account/chequings/history/<venmo_name>', methods=['GET'])
def getChequingsHistory(venmo_name):
    return jsonify(**{
        'row': ['10/5', '10/12', '10/19', '10/26', '11/2'],
        'amount': [20, 50, 100, 70, 10]
        })


### RUNNER ########################################

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

