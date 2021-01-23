from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'Server is up and running!'

@app.route('/setTemplate', methods = ['POST'])
def callSetTemplate():
    pass

@app.route('/parseInvoice', methods = ['POST'])
def callParseInvoice():
    pass

@app.route('/removeInvoice', methods = ['DELETE'])
def callRemoveInvoice():
    pass

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')