# FintechChallenge Fraud Detection API

System which parses invoices and compares against realtime prices to detect frauds and duplicate submission of invoices.

## Instructions

To start the server, run "paths.py". This should start the Flask server on http://localhost:5000.

Run "invoiceAI.py" and follow the instructions on the command line to select the invoice to set the template. Take note of the Object ID provided, as can be seen in the screenshot below.

![Pic1](https://github.com/Hsengiv2000/FintechChallenge/blob/main/Gallery/settemplate.PNG)

Once the template has been set the following curl command can then be used to evaluate your existing invoices.

curl -X POST -v -F 'filename=receipt.png' -F 'file=@testreceipt.jpg' -F "template=600c5cd07e03a162d98eb1e5"  http://localhost:5000/parseInvoice

*NOTE*: In the above, replace "testreceipt.jpg" with the path to your invoice and set the template to the Object ID you obtained above.

## GUI
A simple and intuitive GUI is provided to upload invoice templates for the system to parse.
![Pic1](https://github.com/Hsengiv2000/FintechChallenge/blob/main/Gallery/templatecreation.png)
![Pic2](https://github.com/Hsengiv2000/FintechChallenge/blob/main/Gallery/alltemplate.PNG)

## Correct Result
A correct result returns the message "True" along with the parsed values of each item in the invoice.

We will test it out on this correct invoice.

![Pic3](https://github.com/Hsengiv2000/FintechChallenge/blob/main/invoices/demoinvoice.png)

The API called on the above particular invoice yields the below result.

![Pic3](https://github.com/Hsengiv2000/FintechChallenge/blob/main/Gallery/correctresult.PNG)

## Duplicate Invoice
When an invoice is duplicated (it already exists in the database) the API will return "False" indicating potential fraud and suggesting further inspection.


![Pic4](https://github.com/Hsengiv2000/FintechChallenge/blob/main/Gallery/fraudresult.PNG)

## Falsified Prices
When an invoice overstates commodity prices, the API will return "False" indicating potential fraud and suggesting further inspection.


![Pic5](https://github.com/Hsengiv2000/FintechChallenge/blob/main/Gallery/fraudtransaction.PNG)
