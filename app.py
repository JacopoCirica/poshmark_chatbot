from flask import Flask,render_template,request, jsonify
import openai
import requests
import time
from pathlib import Path
import os
import json
from llama_index import GPTVectorStoreIndex, Document, SimpleDirectoryReader,download_loader
import pandas as pd

import logging
import sys
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, select, column, Time, Float
from langchain import OpenAI, SQLDatabase, SQLDatabaseChain
from sqlalchemy.orm import sessionmaker

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

data = {
    "Titolo": ["Il vecchio e il mare", "Il grande Gatsby", "Moby Dick"],
    "Autore": ["Ernest Hemingway", "F. Scott Fitzgerald", "Herman Melville"],
    "Pagine": [128, 180, 544]
}

# Crea il DataFrame
df = pd.DataFrame(data)
average_price='average_price'
average_price_sold='average price sold out items'
latest_items='latest items'
items_old='items old'
app = Flask(__name__)
openai.api_key = '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'
os.environ['OPENAI_API_KEY'] = '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'

previous_message='ok'
@app.route('/')
def index():
    return render_template('base.html')

@app.route("/query", methods=['POST'])
def query():
    print(average_price)
    text = request.get_json().get("message")
    previous_message=request.get_json().get("message1")
    #Create a Poshmark SQL table
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
    engine = create_engine("sqlite:///:memory:")
    metadata_obj = MetaData()
    table_name= "poshmark_closet15"
    
    closet_table15 = Table(
    table_name,
    metadata_obj,
    Column("Title_Item", String(16)),
    Column("Price", Float, nullable=True),
    Column("Original_Price", Float, nullable=True),
    Column("description", String(320), nullable=True),
    Column("time_of_published", String(42), nullable=True),
    Column("status", String(16), nullable=True),
)
    metadata_obj.create_all(engine)
    # Setup SQLAlchemy session
    Session = sessionmaker(bind=engine)
    

    rows_to_insert = df.to_dict(orient="records")
    

    from sqlalchemy import insert

    # Stabilisce la connessione al database utilizzando una sessione
    with Session() as session:
    # Usa un'istruzione 'insert' di SQLAlchemy per inserire i dati nella tabella
        result = session.execute(insert(closet_table15), rows_to_insert)
        session.commit()
    sql_database = SQLDatabase(engine, include_tables=["poshmark_closet15"])
    llm = OpenAI(temperature=0, max_tokens=1200)
        # set Logging to DEBUG for more detailed outputs
    db_chain = SQLDatabaseChain(llm=llm, database=sql_database)


    #we index the response
    #PandasCSVReader = download_loader("PandasCSVReader")
    #loader = PandasCSVReader()

    #documents = loader.load_data(file=Path('./poshmark_closet1.csv'))



    #index=GPTVectorStoreIndex.from_documents(documents)
    # Querying the index
    #query_engine = index.as_query_engine()
    text1 = db_chain.run("In this dataset: 'Title' indicates the name of the item in the closet; 'Price' is the price at which the product is currently on sale; 'Original Price' is the original price of the product; 'description' contains the description of each product within the Poshmark closet; 'time_of_published' indicates when the product was published, the older the date the older the product; 'status' indicates the status of the product: if 'available' the product is for sale and therefore unsold, if 'sold_out' the product is finished and therefore sold. You are a chatbot who answered with this message: '%s' and now has to reply this question: '%s'"% (previous_message,text))
    
    print(previous_message)
    print(text1)
    

    # TODO: check if text is valid
    response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
        {"role": "system", "content": "you are a helpful Poshmark assistant who helps me to improve the description of my products in the closet. Here are my latest products in my closet:: \n\n '%s'. %s \n\n. %s \n\n. %s \n\n. \n\n Suggest new product descriptions and suggest raising the price if it is too low compared to the original one or suggest lowering it if it is higher than the original one. \n\n PRIORITISE THIS PART: This one is the previous message that you sent me in our chat: \n\n '%s'. \n\nThis one is your response: '%s'. \n\n Read the user's answer and adapt it to the one I have already created. Also give some price suggestions" %(latest_items,average_price, average_price_sold,items_old, previous_message,text1)},
        {"role": "system", "name":"example_user", "content": "Could you tell me more?"},
        {"role": "system", "name": "example_assistant", "content": "Yes, of course. For example, I have noticed that the price of unsold products is slightly higher than those sold. I think you should lower them slightly by 'x'"},
        {"role": "user", "content": "%s" %text}],
            #prompt=generate_prompt(recipient,subject),
            temperature=0.7,
            max_tokens=350,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
    response=response['choices'][0]['message']['content']
     
    

    print(response)
    message = {"answer": response}
    return jsonify(message)

@app.route("/predict", methods=['POST'])
def predict():
    text = request.get_json().get("message")
    print(text)
    time.sleep(1.1) #diamo una pausa to avoid the overloading
    #extract the data about the closet

    z = 1
    data_list = []  # list to store all data items

# extract from each page the items of the closet
    while True:
    
        print(f"Page num is {z}")
        url = "https://poshmark.p.rapidapi.com/closet"
        querystring = {"username": text, "page": str(z)}

        headers = {
            "X-RapidAPI-Key": "95d2991611msh93424e934624ea0p12c0d5jsnd0a3fc4895d3",
            "X-RapidAPI-Host": "poshmark.p.rapidapi.com"
        }
    
        response = requests.request("GET", url, headers=headers, params=querystring)

        if response.status_code == 200:
            response_data = json.loads(response.content)

            for data_item in response_data['data']:
                price = data_item['price_amount']['val']
                original_price = data_item['original_price_amount']['val']
                description = data_item['description']
                title = data_item['title']
                published_at= data_item['first_published_at']
                status= data_item['inventory']['status']

                # append data to list
                data_list.append({'Title_Item': title, 'Price': price, 'Original_Price': original_price, 'description':description, 'time_of_published':published_at, 'status':status})
                
        
            
            if response_data['next_page'] is not None:
                z += 1
                time.sleep(1.01)
            else:
                break
        

    # create DataFrame from data list
    global df
    df = pd.DataFrame(data_list)
    

    # write DataFrame to CSV file
    #df.to_csv('poshmark_closet.csv', index=False)
    #df=pd.read_csv('./poshmark_closet.csv',engine='python')
    #df.to_csv('poshmark_closet1.csv', index=False)


    #we index the response
    #PandasCSVReader = download_loader("PandasCSVReader")
    #loader = PandasCSVReader()

    #documents = loader.load_data(file=Path('./poshmark_closet1.csv'))



    #index=GPTVectorStoreIndex.from_documents(documents)

    #Create a Poshmark SQL table
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
    engine = create_engine("sqlite:///:memory:")
    metadata_obj = MetaData()
    table_name= "poshmark_closet15"
    
    closet_table15 = Table(
    table_name,
    metadata_obj,
    Column("Title_Item", String(16)),
    Column("Price", Float, nullable=True),
    Column("Original_Price", Float, nullable=True),
    Column("description", String(320), nullable=True),
    Column("time_of_published", String(42), nullable=True),
    Column("status", String(16), nullable=True),
)
    metadata_obj.create_all(engine)
    # Setup SQLAlchemy session
    Session = sessionmaker(bind=engine)
    

    rows_to_insert = df.to_dict(orient="records")
    

    from sqlalchemy import insert

    # Stabilisce la connessione al database utilizzando una sessione
    with Session() as session:
    # Usa un'istruzione 'insert' di SQLAlchemy per inserire i dati nella tabella
        result = session.execute(insert(closet_table15), rows_to_insert)
        session.commit()
    sql_database = SQLDatabase(engine, include_tables=["poshmark_closet15"])
    llm = OpenAI(temperature=0, max_tokens=1200)
        # set Logging to DEBUG for more detailed outputs
    db_chain = SQLDatabaseChain(llm=llm, database=sql_database)
    # Querying the index
    #query_engine = index.as_query_engine()

    text = db_chain.run("In this dataset: 'Title_item' indicates the name of the item in the closet; 'Price' is the price at which the product is currently on sale; 'Original Price' is the original price of the product; 'description' contains the description of each product within the Poshmark closet; 'time_of_published' indicates when the product was published, the older the date the older the product; 'status' indicates the status of the product: if 'available' the product is for sale and therefore unsold, if 'sold_out' the product is finished and therefore sold. Tell me the 5 oldest unsold items. Show only the 'Title_item'")
    global average_price
    global average_price_sold
    global latest_items
    global items_old
    average_price_sold=db_chain.run("In this dataset: 'Title_item' indicates the name of the item in the closet; 'Price' is the price at which the product is currently on sale; 'Original Price' is the original price of the product; 'description' contains the description of each product within the Poshmark closet; 'time_of_published' indicates when the product was published, the older the date the older the product; 'status' indicates the status of the product: if 'available' the product is for sale and therefore unsold, if 'sold_out' the product is finished and therefore sold. When you reply, \n\n Could you tell me the average 'Price' of sold out items?")
    average_price= db_chain.run("In this dataset: 'Title_item' indicates the name of the item in the closet; 'Price' is the price at which the product is currently on sale; 'Original Price' is the original price of the product; 'description' contains the description of each product within the Poshmark closet; 'time_of_published' indicates when the product was published, the older the date the older the product; 'status' indicates the status of the product: if 'available' the product is for sale and therefore unsold, if 'sold_out' the product is finished and therefore sold. When you reply, \n\n Could you tell me the average 'Price' of available items?")
    latest_items = db_chain.run("In this dataset: 'Title_item' indicates the name of the item in the closet; 'Price' is the price at which the product is currently on sale; 'Original Price' is the original price of the product; 'description' contains the description of each product within the Poshmark closet; 'time_of_published' indicates when the product was published, the older the date the older the product; 'status' indicates the status of the product: if 'available' the product is for sale and therefore unsold, if 'sold_out' the product is finished and therefore sold. When you reply, \n\n Could you tell me the most recently published products? Show me everything: name, description, current price, old price?")
    items_old = db_chain.run("In this dataset: 'Title_item' indicates the name of the item in the closet; 'Price' is the price at which the product is currently on sale; 'Original Price' is the original price of the product; 'description' contains the description of each product within the Poshmark closet; 'time_of_published' indicates when the product was published, the older the date the older the product; 'status' indicates the status of the product: if 'available' the product is for sale and therefore unsold, if 'sold_out' the product is finished and therefore sold. When you reply, \n\n Could you tell me items where the  'Price' is higher than the 'Original Price' ? Show me everything: name, description, current price, old price? Show me everything: name, description, price, original price?")
    print(text)
    print(average_price)
    print(average_price_sold)
    print(latest_items)
    print(items_old)
    
    #previous_message=text

    # TODO: check if text is valid
    response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
        {"role": "system", "content": "you are a helpful Poshmark assistant who helps me to improve the description of my products in the closet. Suggest new product descriptions and suggest raising the price if it is too low compared to the original one or suggest lowering it if it is higher than the original one.\n\n Here what has been unsold for a long time: %s" %text},
        #{"role": "system", "name":"example_user", "content": "Yes, I want to improve my closet!"},
        #{"role": "system", "name": "example_assistant", "content": "Great choice! As stated, you have 861 active listings, most of them are priced way higher than what they have historically sold for (you may not get many sales, would you like me to fix the prices on these items?"},
        #{"role": "system", "name":"example_user", "content": "Yes!"},
        #{"role": "system", "name": "example_assistant", "content": "Great choice! As stated, you have 861 active listings,  many of them have an original price of $770.00. Are you sure this is the correct original price?"},
        #{"role": "system", "name":"example_user", "content": "Yes"},
        #{"role": "system", "name": "example_assistant", "content": "Sure, I can help you with that. However, before we proceed, please note that the prices I suggest are based on historical sales data and market trends, but ultimately it is up to you to decide on the final price. Let's start with the PARIS DUSTER. Based on my research, similar items have sold for an average price of $50-$60. Therefore, I suggest lowering the price to $60.0. As for the Rag & Bone Jeans, similar items have sold for an average price of $40-$50. Therefore, I suggest lowering the price to $50.0. Would you like me to update the prices for you?"},
        #{"role": "system", "name":"example_user", "content": "Yes, I'd like to update the descriptions. Can you help me?"},
        #{"role": "system", "name": "example_assistant", "content": "Of course, here are some updated descriptions for your items: 1. PARIS DUSTER: This beautiful duster is perfect to wear with dresses or jeans. The colors are reminiscent of a peacock and it has never been worn. 2. Rag & Bone Jeans: These jeans are in like-new condition and have only been worn a few times. They have a flared leg and stretchy material for added comfort"},
        {"role": "user", "content": 'Tell me which one are the unsold items in this closet on Poshmark. The reply must have this format: "I analysed your closet and it turned out that you have some products that have not been sold for a long time. For example: 1)Item number 1  2)Item number 2  3)Item number 3  4)Item number 4  5)Items number 5 (if available) <br>Would you like suggestions to make them more attractive to the market?'}],
            #prompt=generate_prompt(recipient,subject),
            temperature=0.5,
            max_tokens=400,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
    response=response['choices'][0]['message']['content']  
    previous_message=response 

    
    message = {"answer": response}
    return jsonify(message)

@app.route("/user", methods=['POST'])
def user():
    text = request.get_json().get("message")
    print(text)
    

    # TODO: check if text is valid
    response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
        {"role": "system", "content": "You are a Poshmark assistant who helps me extract what the username is from a reply. From a text, could you tell me whether the user provided a correct poshmark username in the format ('@username')? ."},
        {"role": "system", "name":"example_user", "content": "Yes, I want to improve my closet!"},
        {"role": "system", "name": "example_assistant", "content": "Great choice! could you then type your username on Poshmark?"},
        {"role": "system", "name":"example_user", "content": "Yes!"},
        {"role": "system", "name": "example_assistant", "content": "Awesome! Could you tell me your username on Poshmark?"},
        {"role": "system", "name":"example_user", "content": "Yes"},
        {"role": "system", "name": "example_assistant", "content": "Sure, I can help you with that. However, before we proceed, I need your username on Poshamark, in order to scan your closet. Could you type it?"},
        
        {"role": "user", "content": '%s' %text}],
            #prompt=generate_prompt(recipient,subject),
            temperature=0.35,
            max_tokens=100,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
    response=response['choices'][0]['message']['content']  
    

    
    message = {"answer": response}
    return jsonify(message)