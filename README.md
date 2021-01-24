# FintechChallenge Fraud Detection API

System which parses invoices and compares against realtime prices to detect frauds and duplicate submission of invoices.

## GUI
A simple and intuitive GUI is provided to upload invoice templates for the system to parse.
![Pic1](https://github.com/Hsengiv2000/FintechChallenge/blob/main/Gallery/templatecreation.png)
![Pic2](https://github.com/Hsengiv2000/FintechChallenge/blob/main/Gallery/alltemplate.PNG)

## Correct Result
A correct result returns the message "True" along with the parsed values of each item in the invoice.
![Pic3](https://github.com/Hsengiv2000/FintechChallenge/blob/main/Gallery/correctresult.PNG)

## Duplicate Invoice
When an invoice is duplicated (it already exists in the database) the API will return "False" indicating potential fraud and suggesting further inspection.
![Pic4](https://github.com/Hsengiv2000/FintechChallenge/blob/main/Gallery/fraudresult.PNG)

## Duplicate Invoice
When an invoice overstates commodity prices, the API will return "False" indicating potential fraud and suggesting further inspection.
![Pic5](https://github.com/Hsengiv2000/FintechChallenge/blob/main/Gallery/fraudtransaction.PNG)
