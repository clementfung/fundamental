import os
from flask import Flask, render_template, request
import db

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/api/test')
def test():
    print 'trying to query database'
    db.test_connection()
    print 'test'
    return 'success'

#### SHARED APIS ######################################

@app.route('/account/info/<venmo_name>')
def getAccountInfo(venmo_name):

    return jsonify(**{
        "sample_field": 0
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
    savings_amount = request.form['amount']
    success = 0

    return jsonify(**{
        "success": success
        })

@app.route('/account/withdraw', methods=['POST'])
def withdrawAmount():

    venmo_id = request.form['venmo_name']
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

