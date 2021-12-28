import json
import time
from azure.core.exceptions import ResourceNotFoundError
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import FormRecognizerClient
import pyodbc
import datetime
import re

#DBMS connection
dbms_conn = json.load(open('C:/Users/trish/Documents/GitHub/EarmarkVeraciously_Project_deliverables/credentials.json'))
username = dbms_conn['username']
password = dbms_conn['password']
server = 'localhost'
database = 'budgets'
driver='{ODBC Driver 17 for SQL Server}'
driver = 'SQL Server'

# making global variables to set few values for insert statements
exp_user_id = 1
exp_description = ""
merchant_id = 0
merchant_address = ""
merchant_name = ""
merchant_number = ""
tax = 0.0
total_amt = 0.0 
purchase_date = datetime.datetime.now().date()
purchase_time = datetime.datetime.now().time()
# purchase_date = ""
# purchase_time = ""
category_name = 'Fun'
final_merchant_id = 0
category_id = 0
product_name = ""
product_price = 0.0


credentials = json.load(open('C:/Users/trish/Documents/GitHub/EarmarkVeraciously_Project_deliverables/credentials.json'))
API_KEY = credentials['API_KEY']
ENDPOINT = credentials['ENDPOINT']
form_recognizer_client = FormRecognizerClient(ENDPOINT, AzureKeyCredential(API_KEY))

with open(r"C:\Users\trish\Documents\GitHub\EarmarkVeraciously_Project_deliverables\images\TFun.jpeg", "rb") as f:
    poller = form_recognizer_client.begin_recognize_receipts(f.read())
print(poller.status())


time.sleep(3)
if poller.status() == 'succeeded' or 'InProgress':
#if poller.status() == 'InProgress':
    result = poller.result()
    for receipt in result:
        print(receipt.form_type)
        #print(receipt)
        for name, field in receipt.fields.items():
            if name == 'Items':
                print('Purchase Item')
                with open('log.txt', 'w') as out_f:
                    for indx, item in enumerate(field.value):
                        print('\tItem #{0}'.format(indx + 1), file=out_f)
                        for item_name, item in item.value.items():
                            print('\t{0}: {1}'.format(item_name, item.value), file=out_f)
            else:
                with open('JSONlog.txt', 'a') as out_f:
                    print('{0}: {1}'.format(name, field.value), file=out_f)
        # for insert statements creating all the variables
        for name, field in receipt.fields.items():
            #print('{0}: {1}'.format(name, field.value))
            if name == "MerchantAddress":
                merchant_address = field.value
            if name == "MerchantName":
                merchant_name = field.value
            if name == "MerchantPhoneNumber":
                merchant_number = field.value
            if name == "Tax":
                tax = field.value
            if name == "Total":
                total_amt = field.value
            if name == "TransactionDate":
                purchase_date = field.value 
            if name == "TransactionTime":
                purchase_time = field.value
            print("-============-")
        # Inserting into merchants table 
        if None not in (merchant_address, merchant_name, merchant_number, tax,
                        total_amt, purchase_date, purchase_time):
            with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=5000;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
                with conn.cursor() as cursor: #merchant_id, exp_merchant_name exp_category_id,
                    cursor.execute('''Select merchant_name \
                                   from merchants where merchant_name=?''', merchant_name)
                    row = cursor.fetchone()
                    #print(row)
                    if row:
                        print("The value is already in the merchants table so we will not do any \
                              insert into our merchants table")
                    else:
                        cursor.execute('''INSERT into merchants (merchant_name,\
                                       merchant_address, merchant_number) \
                            VALUES (?, ?, ?)''', (merchant_name, merchant_address, merchant_number))
                        print(f"Inserted values{merchant_name, merchant_address, merchant_number} into merchant table")
                    # Inserting into total_expenses 
                    # first seeing if the value exists in totaL_expense table 
                    print(tax,total_amt, purchase_date,purchase_time)
                    cursor.execute('''select merchant_id from total_expenses 
                                   where tax=? and total_amt=? and purchase_date=? 
                                   and  purchase_time=?  ''', 
                                       (tax,total_amt, purchase_date.strftime('%Y-%m-%d'), 
                                        purchase_time.strftime('%H:%M:%S')))
                    merchant_id = cursor.fetchone()
                    # if merchant id exists dont insert else insert 
                    if merchant_id:
                        final_merchant_id = merchant_id[0]
                        print("The row entry for the total_expense already exists so not inserting it again")
                    else:    
                        cursor.execute('''select merchant_id as id from merchants where merchant_name=?
                                       ''', merchant_name)
                        merchant_id_merchant_table = cursor.fetchone() 
                        final_merchant_id = merchant_id_merchant_table[0]
                        cursor.execute('''insert into total_expenses (merchant_id,\
                                       tax, total_amt, purchase_date, \
                                   purchase_time) VALUES \
                            (?,?,?,?,?)''', (final_merchant_id, 
                                       tax, total_amt, purchase_date.strftime('%Y-%m-%d'), 
                                        purchase_time.strftime('%H:%M:%S')))
                        print(f"Inserted values{final_merchant_id, tax, total_amt, purchase_date.strftime('%Y-%m-%d'), purchase_time.strftime('%H:%M:%S')} into total_expense table")
                        
            for name, field in receipt.fields.items():
                if name == 'Items':    
                    print("came here")
                    for indx, item in enumerate(field.value):
                       # print(item.value.keys())
                        for item_name, item in item.value.items():
                            #print('\t{0}: {1}'.format(item_name, item.value))
                            if item.name == 'Name': #str(item.value):
                                product_name = item.value
                            elif item.name == 'TotalPrice':
                                product_price = item.value
                                #check if value is null or not for product price 
                                #to avoid null error while inserting data into expense table
                                if product_price:
                                    pass
                                else:
                                    product_price = float(re.sub('[^0-9,.]', '', item.value_data.text)[1:])
                                    
                            # check category id 
                            cursor.execute('''select category_id as id from categories 
                                           where category_name=?''', category_name)
                            category_id = cursor.fetchone()
                            final_category_id =  category_id[0]
                            if final_category_id:
                                pass
                            else:
                                cursor.execute('''insert into categories (category_name)
                                               values (?)''', category_name)
                                cursor.execute('''select category_id as id from categories 
                                           where category_name=?''', category_name)
                                category_id = cursor.fetchone()
                                final_category_id =  category_id[0]
                        # inserting into expenses table
                        if str(product_name) and float(product_price):
                            #print(f"the name is {product_name} and price is {product_price} \
                            #      and item is {item}")
                            cursor.execute('''select exp_item_name from expenses \
                                   where exp_user_id=? and exp_item_name=? and \
                                   exp_item_price=? and \
                                   exp_purchase_date=? and exp_purchase_time=? and \
                                   exp_merchant_id=? and exp_merchant_name=? and \
                                            exp_category_id=? ''',  
                                       (exp_user_id, product_name,
                                        product_price,purchase_date.strftime('%Y-%m-%d'), 
                                        purchase_time.strftime('%H:%M:%S')
                                        ,final_merchant_id, merchant_name,
                                        final_category_id))
                            
                            value_exists = cursor.fetchone()
                            if value_exists:
                                print("The row entry for the expenses table already exists so not inserting it again") 
                            else:
                                cursor.execute(''' INSERT INTO expenses 
                                               (exp_user_id, exp_item_name, exp_item_price,
                                                exp_purchase_date, exp_purchase_time,
                                                exp_description,
                                                exp_merchant_id, exp_merchant_name,
                                                exp_category_id) VALUES 
                                               (?,?,?,?,?,?,?,?,?)''',  (exp_user_id, product_name,
                                               product_price,purchase_date.strftime('%Y-%m-%d'), 
                                            purchase_time.strftime('%H:%M:%S'), exp_description
                                            ,final_merchant_id, merchant_name,
                                            final_category_id))  
                                conn.commit()
                                print(f"Inserted values{exp_user_id, product_name,product_price,purchase_date.strftime('%Y-%m-%d'), purchase_time.strftime('%H:%M:%S'), exp_description,final_merchant_id, merchant_name,final_category_id} into expenses table")               
                         
                              
                           

                
                
else:
    print("not running")




# References
# https://azuresdkdocs.blob.core.windows.net/$web/python/azure-ai-formrecognizer/1.0.0b2/azure.ai.formrecognizer.html

# https://docs.microsoft.com/en-us/python/api/azure-ai-formrecognizer/azure.ai.formrecognizer.formrecognizerclient?view=azure-python

# https://learndataanalysis.org/source-code-getting-started-with-azure-form-recognizer-api-in-python/

# https://hugoworld.wordpress.com/2019/01/06/slow-python-insert-performance-into-microsoft-sql-server/