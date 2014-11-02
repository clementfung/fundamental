import os
from flask import Flask, render_template, request, jsonify
import db

DEBUG = True
app = Flask(__name__)
<<<<<<< HEAD
app.config.from_object(__name__)

account_collection_str = "account_info"
=======
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
>>>>>>> master

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
         "chequings_balance" : account_info['chequings_balance'],
         "savings_balance" : account_info['savings_balance'],
         "allowance_amount" : account_info['allowance_amount'],
         "savings_amount" : account_info['savings_amount'],
         "interest_rate" : account_info['interest_rate']
        })

@app.route('/register')
def register():

    venmo_id = request.form['venmo_name']
    name = request.form['user_name']
    p_venmo_id = request.form['parent_venmo_name']
    p_name = request.form['parent_name']
    success = 0

    return jsonify(**{
        "success": success
        })

#### MOBILE APIS ########################################

@app.route('/account/savings_amount', methods=['POST'])
def setSavingsAmount():

    venmo_id = request.form['venmo_name']
    savings_amount = int(request.form['amount'])
    success = 0

    # post as long as value is 0
    if savings_amount < 0:    
        return jsonify(**{
            "success":1
            })

    else:        
        account_info = db.get_collection(account_collection_str)
        account_info.update({"user_id" : venmo_id}, 
            {"$set": {"savings_amount": savings_amount}})
    
    return jsonify(**{
        "success": success
        })

@app.route('/account/withdraw', methods=['POST'])
def withdrawAmount():

    venmo_id = request.form['venmo_name']
    withdraw_amount = int(request.form['amount'])

    account_info = db.get_collection(account_collection_str)
    account_info_record = account_info.find_one({"user_id" : venmo_id})
    current_amount = account_info_record['chequings_balance']

    if (withdraw_amount > current_amount):
        return jsonify(**{
            "success":1
            })
    else:
        current_amount = current_amount - withdraw_amount
        account_info.update({"user_id" : venmo_id},
                {"$set": {"chequings_balance" : current_amount}})

    return jsonify(**{
        "success": 0
        })

@app.route('/account/transfer_to', methods=['POST'])
def transferTo():

    venmo_id = request.form['venmo_name']
    destination = request.form['destination']
    withdraw_amount = request.form['amount']
    success = 0

    return jsonify(**{
        "success": success
        })

#### WEB APIS #####################################

@app.route('/account/savings_interest', methods=['POST'])
def setSavingsInterest():

    venmo_id = request.form['venmo_name']
    savings_interest = request.form['rate']
    success = 0

    return jsonify(**{
        "success": success
        })

@app.route('/account/loan_interest', methods=['POST'])
def setLoanInterest():

    venmo_id = request.form['venmo_name']
    loan_interest = request.form['rate']
    success = 0

    return jsonify(**{
        "success": success
        })


### RUNNER ########################################

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

