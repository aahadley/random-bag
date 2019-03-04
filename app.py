from flask import Flask, render_template, request
import requests, json
import random, time
import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import IBMQ, execute, BasicAer as aer
from qiskit.tools.monitor import job_monitor
from qiskit.providers.ibmq import least_busy

from requests.auth import HTTPBasicAuth

###
with open("zinctoken.txt", "r") as z:
    zinctoken = z.read()
    print(zinctoken)
###

app = Flask(__name__)

def qrng(phys_or_sim, size=16, qubits=4, max_credits=3):
    '''Return a random size bit integer'''

    if phys_or_sim in ['p', "phys", "physical"]:
        IBMQ.load_accounts()
        large_enough_devices = IBMQ.backends(filters=lambda x: x.configuration().n_qubits >= qubits and not x.configuration().simulator)
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
    queries = 4
    products = []

    flag = 0
    while flag < queries:
        for i in range (queries):
            #print("top")

            if(i == 0):
                xornum = 0
            else:
                xornum = random.randint(1, 10000)

            itemnum = (qnum ^ xornum) % 10000

            #print("after if")
            url = "https://api.zinc.io/v1/search?query={}&page=1&retailer=amazon".format(itemnum)
            #print(url)

            try:
                res = requests.get(url, auth=HTTPBasicAuth('09EC5307D55F0123E02A2BAB', ''), timeout=6)            
            except requests.exceptions.RequestException as e:
                print("Still thinkin' hang in there", e)
                continue    

            res = res.json() 
            #print(type(res), res.text, sep='\n')
            #print(res)

            try:
                products += res['results']        
            except KeyError:   
                print("caught key error")         
                continue

            flag += 1 
                
    spent = 0
    full = False
    priced = []

    bought = []
    for i in products:
        if( "price" in i):
            priced.append(i)

    i = 0
    while len(priced) > 0:

        #print (len(priced))

        if( price_range[0] > price_range[1] - spent ):
            break

        ch = random.choice(priced)

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
@app.route("/order", methods=["POST", "GET"])
def build_order():

    user = get_user_info()

    '''
    user['shipping_address']['first_name'] = request.form['firstShip']
    user['shipping_address']['last_name'] = request.form['lastShip']
    user['shipping_address']['phone_number'] = request.form['phoneShip']
    user['shipping_address']['address_line1'] = request.form['shipping1']
    user['shipping_address']['address_line2'] = request.form['shipping2']
    user['shipping_address']['zip_code'] = request.form['zipShip']
    user['shipping_address']['city'] = request.form['cityShip']
    user['shipping_address']['state'] = request.form['stateShip']
    user['shipping_address']['country'] = request.form['countryShip']

    user['billing_address']['first_name'] = request.form['firstBill']
    user['billing_address']['last_name'] = request.form['lastBill']
    user['billing_address']['phone_number'] = request.form['phoneBill']
    user['billing_address']['address_line1'] = request.form['billing1']
    user['billing_address']['address_line2'] = request.form['billing2']
    user['billing_address']['zip_code'] = request.form['zipBill']
    user['billing_address']['city'] = request.form['cityBill']
    user['billing_address']['state'] = request.form['stateBill']
    user['billing_address']['country'] = request.form['countryBill']

    user['shipping_address']['last_name'] = request.form['lastShip']

    user['shipping']['payment_method']['name_on_card'] = request.form['credit']
    user['shipping']['payment_method']['number'] = request.form['creditName']
    user['shipping']['payment_method']['security_code'] = request.form['creditCode']
    user['shipping']['payment_method']['expiration_year'] = request.form['expYear']
    user['shipping']['payment_method']['expiration_month'] = request.form['expMonth']
    '''

    price_range = set_price_range(int(request.form['pricemin']), int(request.form['budget']), int(request.form['pricemax'])) 

    # Build a list of product-id pairs
    products = []
    p_list = select_items(price_range, qrng("sim"))[0]

    for p in p_list:
        products.append({"product_id": p["product_id"] , "quantity": 1})

    user.pop("products", None)

    # add products into user
    user["products"] = products

    req = requests.post("https://api.zinc.io/v1/orders", auth=(zinctoken, ''), data=json.dumps(user) ).text
    #print(req) # for debugging

    return str([p["title"] + p["image"] for p in p_list])
    
if __name__ == "__main__":
    app.run()
