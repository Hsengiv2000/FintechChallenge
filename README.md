# FintechChallenge Fraud Detection API

System which parses invoices/Forms and compares against database to continue on the process.

## Instructions

To start the server, run "paths.py". This should start the Flask server on http://localhost:5000.

Run "invoiceAI.py" and follow the instructions on the command line to select the invoice/forms to set the template. Take note of the Object ID provided, as can be seen in the screenshot below.

![Pic1](https://github.com/Hsengiv2000/FintechChallenge/blob/main/Gallery/settemplate.PNG)

Once the template has been set the following curl command can then be used to evaluate your existing invoices/forms.

curl -X POST -v -F 'filename=receipt.png' -F 'file=@testreceipt.jpg' -F "template=600c5cd07e03a162d98eb1e5"  http://localhost:5000/parseInvoice

*NOTE*: In the above, replace "testreceipt.jpg" with the path to your invoice and set the template to the Object ID you obtained above.

## GUI
A simple and intuitive GUI is provided to upload invoice/Form templates for the system to parse.
![Pic1](https://github.com/Hsengiv2000/FintechChallenge/blob/main/Gallery/templatecreation.png)
![Pic2](https://github.com/Hsengiv2000/FintechChallenge/blob/main/Gallery/alltemplate.PNG)

## Correct Result
A correct result returns the message "True" along with the parsed values of each item in the invoice.

We will test it out on this correct invoice.

![Pic3](https://github.com/Hsengiv2000/FintechChallenge/blob/main/invoices/demoinvoice.png)

The API called on the above particular invoice/form yields the below result.

![Pic3](https://github.com/Hsengiv2000/FintechChallenge/blob/main/Gallery/correctresult.PNG)

## Duplicate Invoice/Form
WHen a form already exists/has been signed before, it means that we should proceed with the next step in the process

![Pic4](https://github.com/Hsengiv2000/FintechChallenge/blob/main/Gallery/fraudresult.PNG)

