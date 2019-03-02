from flask import Flask, render_template
import requests

import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import IBMQ, execute, BasicAer as aer
from qiskit.tools.monitor import job_monitor
from qiskit.providers.ibmq import least_busy

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

    print("created registers")

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

app = Flask(__name__)

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/info")
def get_user_info():
    return {"" : ""}

# Get price range from user
@app.route("/range")
def set_price_range():
    return (10, 20)

# Search for items within a set price range
@app.route("/items")
def select_items(price_range):
    return None

# Build cart from selected items
@app.route("/cart")
def build_cart(items):
    return None

# Finalize purchase with user information
@app.route("/finalize")
def commit_purchase():
    return None

if __name__ == "__main__":
    print(qrng("sim", size=32))
    app.run()