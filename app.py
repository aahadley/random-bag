from flask import Flask, render_template, request
import requests, json
import random
import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import IBMQ, execute, BasicAer as aer
from qiskit.tools.monitor import job_monitor
from qiskit.providers.ibmq import least_busy

###
zinctoken = "09EC5307D55F0123E02A2BAB"
###

def qrng(phys_or_sim, size=16, qubits=4, max_credits=3):
    '''Return a random size bit integer'''

    if phys_or_sim in ['p', "phys", "physical"]:
        IBMQ.load_accounts()
        large_enough_devices = IBMQ.backends(filters=lambda x: x.configuration().n_qubits >= 4 and not x.configuration().simulator)
        backend = least_busy(large_enough_devices)
        #print("Selected", backend.name())

    elif phys_or_sim in ['s', "sim", "simulated"]:
        backend = aer.get_backend('qasm_simulator')

    shots = size//qubits

    # quantum register with 8 qubits
    qreg = QuantumRegister(qubits, 'q')
    creg = ClassicalRegister(qubits, 'c')

    #print("created registers")

    # quantum circuit acting on q
    circ = QuantumCircuit(qreg, creg)

    for qubit in qreg:
        circ.h(qubit)

    for i in range(qubits):
        circ.measure(qreg[i], creg[i])

    job = execute(circ, backend, shots=shots, max_credits=max_credits)
    #job_monitor(job)
    result = job.result()
    counts = result.get_counts(circ)
    #print(counts)
    num = ""

    for i in list((counts.keys())):
        num += i

    return int(num, 2)
from flask import Flask, render_template, redirect, url_for
import requests

app = Flask(__name__)

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/cart")
def cart():
    return render_template("cart.html")

@app.route("/log")
def log():
    return render_template("log.html")

@app.route("/test")
def test():
    return render_template("test.html")

@app.route("/info")
def get_user_info():
    f = open("default_user.json", "r")
    user = json.load(f)
    f.close()
    return user

# Get price range from user
@app.route("/range")
def set_price_range(min, bug, max):
    return (min, bug, max)

# Search for items within a set price range
@app.route("/items")
def select_items(price_range,qnum):
    crng= random.Random()
    products = []
    for i in range (2):
        print("top")
        if(i == 0):
            xornum = 0
        else:
            xornum = crng.randint(1, qnum)
        itemnum = qnum

        print("after if")
        url = "https://api.zinc.io/v1/search?query={}&page=1&retailer=amazon".format(itemnum)
        print(url)


        res = requests.get(url, auth=(zinctoken, '')).json()
        #print(res)

        try:
            products += res['results']
        except:
            print("caught")
            continue

    spent = 0
    full = False
    priced = []

    bought = []
    for i in products:
        if( "price" in i):
            priced.append(i)

    i = 0
    while len(priced) > 0:

        print (len(priced))

        if( price_range[0] > price_range[1] - spent ):
            break

        ch = crng.choice(priced)


        if(ch['price']/100 > price_range[1] - spent or ch['price']/100 > price_range[2]):
            priced.remove(ch)
            continue

        if( ch['price']/100 > price_range[0] and ch['price']/100 < price_range[2] ):
            bought.append(ch)

            spent += int(ch['price']/100)

        priced.remove(ch)
        print(bought)
    return (bought , spent)

# Build cart from selected items
@app.route("/order", methods=["POST"])
def build_order():

    user = get_user_info()

    user['shipping_address']['first_name'] = request.form['firstShip']
    user['shipping_address']['last_name'] = request.form['lastShip']
    user['shipping_address']['phone_number'] = request.form['phoneShip']
    user['shipping_address']['address_line1'] = request.form['shipping1']
    user['shipping_address']['address_line2'] = request.form['shipping2']
    user['shipping_address']['zip_code'] = request.form['zipShip']
    user['shipping_address']['city'] = request.form['cityShip']
    user['shipping_address']['state'] = request.form['stateShip']
    user['shipping_address']['country'] = request.form['countryShip']

    user['shipping_address']['last_name'] = request.form['lastShip']

    user['shipping']['payment_method']['name_on_card'] = request.form['credit']
    user['shipping']['payment_method']['number'] = request.form['creditName']
    user['shipping']['payment_method']['security_code'] = request.form['creditCode']
    user['shipping']['payment_method']['expiration_year'] = request.form['expYear']
    user['shipping']['payment_method']['expiration_month'] = request.form['expMonth']


    price_range = set_price_range(request.form['pricemin'], request.form['budget'], request.form['pricemax'])

    # Build a list of product-id pairs
    products = []

    for p in select_items(price_range, qrng("sim"))[0]:
        products.append({"product_id": p["product_id"] , "quantity": 1})

    user.pop("products", None)

    # add products into user
    user["products"] = products

    req = requests.post("https://api.zinc.io/v1/orders", auth=(zinctoken, ''), data=json.dumps(user) ).text
    print(req) # for debugging
    return req

if __name__ == "__main__":
    app.run()
