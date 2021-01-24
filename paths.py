from invoiceAI import parseInvoice
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return 'Server is up and running!'

"""
Ignore this one.
"""
@app.route('/setTemplate', methods = ['POST'])
def callSetTemplate():
    pass

@app.route('/parseInvoice', methods = ['POST'])
def callParseInvoice():
    uploaded_file = request.files['file']
    template = request.form['template']
    print(request.form)

    if uploaded_file.filename != '':
        res = parseInvoice(uploaded_file, template)
        result = { "msg": "pass", result: res }
        return jsonify(result)
    else:
        result = { "response": "error" }
        return jsonify(result)


@app.route('/removeInvoice', methods = ['DELETE'])
def callRemoveInvoice():
    pass

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')