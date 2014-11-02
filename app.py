import os
from flask import Flask, render_template, request, jsonify
import db

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)

account_collection_str = "account_info"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def hello():
    return make_response(open('%s/templates/index.html' % BASE_DIR).read())

@app.route('/api/test')
def test():
    print 'trying to query database'
    return str(db.test_connection())

#### SHARED APIS ######################################

@app.route('/account/info/<venmo_name>')
def getAccountInfo(venmo_name):

    account_info = db.find_one(account_collection_str, {"user_id" : str(venmo_name)})

    if account_info is None:
        return jsonify(**{}) 

    return jsonify(**{
         "user_name" : account_info['user_name'],
         "chequing_balance" : account_info['chequing_balance'],
         "savings_balance" : account_info['savings_balance'],
         "allowance_amount" : account_info['allowance_amount'],
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
        "loan_interest_rate" : 0,
        "user_token": "u_token",
        "access_token": "a_token",
        "refresh_token": "r_token"
        });
    # TODO: Venmo fields are totally sucky

    return jsonify(**{
        "success": true
        })

#### MOBILE APIS ########################################

@app.route('/account/savings_amount', methods=['POST'])
def setSavingsAmount():

    venmo_id = request.form['venmo_name']
    savings_amount = float(request.form['amount'])

    # post as long as value is 0
    if savings_amount < 0:    
        return jsonify(**{
            "success": false
            })

    else:        
        account_info = db.get_collection(account_collection_str)
        account_info.update({"user_id" : venmo_id}, 
            {"$set": {"savings_amount": savings_amount}})
    
    return jsonify(**{
        "success": true
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
            "success": false
            })
    else:
        current_amount = current_amount - withdraw_amount
        account_info.update({"user_id" : venmo_id},
                {"$set": {"chequing_balance" : current_amount}})

    return jsonify(**{
        "success": true
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
            "success": false
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
        "success": true
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
            "success": false
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
        "success": true
        })


#### WEB APIS #####################################

@app.route('/account/savings_interest', methods=['POST'])
def setSavingsInterest():

    venmo_id = request.form['venmo_name']
    rate = float(request.form['rate'])

    # post as long as value is 0
    if rate < 0:    
        return jsonify(**{
            "success": false
            })

    else:        
        account_info = db.get_collection(account_collection_str)
        account_info.update({"user_id" : venmo_id}, 
            {"$set": {"loan_interest_rate": rate}})
    
    return jsonify(**{
        "success": true
        })

@app.route('/account/loan_interest', methods=['POST'])
def setLoanInterest():

    venmo_id = request.form['venmo_name']
    rate = float(request.form['rate'])

    # post as long as value is 0
    if rate < 0:    
        return jsonify(**{
            "success": false
            })

    else:        
        account_info = db.get_collection(account_collection_str)
        account_info.update({"user_id" : venmo_id}, 
            {"$set": {"loan_interest_rate": rate}})
    
    return jsonify(**{
        "success": true
        })

@app.route('/account/set_allowance', methods=['POST'])
def setAllowance():

    venmo_id = request.form['venmo_name']
    rate = float(request.form['rate'])

    # post as long as value is 0
    if rate < 0:    
        return jsonify(**{
            "success": false
            })

    else:        
        account_info = db.get_collection(account_collection_str)
        account_info.update({"user_id" : venmo_id}, 
            {"$set": {"allowance_amount": rate}})
    
    return jsonify(**{
        "success": true
        })

### RUNNER ########################################

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

