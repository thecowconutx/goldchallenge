from flasgger import swag_from
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flask import request
import pandas as pd
from flask import Flask, jsonify
from function import full_clean
import sqlite3

# connect to sqlite
con = sqlite3.connect('api.db')
cur = con.cursor()

df_1 = pd.read_sql("SELECT Tweet from data", con)

con.close()


# Flask and Swagger UI
app = Flask(__name__)

app.json_encoder = LazyJSONEncoder
swagger_template = dict(
    info={
        'title': LazyString(lambda: 'Text Cleansing API Documentation'),
        'version': LazyString(lambda: '1.0.0'),
        'description': LazyString(lambda: 'API untuk membersihkan text data')
    },
    host=LazyString(lambda: request.host)
)
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json'
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template, config=swagger_config)

# First endpoint to process text input


@swag_from("docs/text_processing.yml", methods=['POST'])
@app.route('/text-processing', methods=['POST'])
def text_processing():

    text = request.form.get('text')

    json_response = {
        'status_code': 200,
        'description': "Original Teks",
        'data': full_clean(text)  # full clean function from function.py
    }

    response_data = jsonify(json_response)
    return response_data

# second endpoint to process file input


@swag_from('docs/file-processing.yaml', methods=['POST'])
@app.route('/file-processing', methods=['POST'])
# --- Define file processing function ---  
def file_processing():
    if "file" in request.files:
      file = request.files['file']
      # Save temporary file in server
      file.save("cleansing_file.csv")
      df = pd.read_csv("cleansing_file.csv",header=None)
      text = df.values.tolist()
      clean_text = []

      for i in text:
        clean_text.append(text_cleansing(i[0]))
        
        
      # Json response for successful request
      json_response = {
              'status_code': 200,
              'description': "Result from file cleansing, Successful response !!!",
              'data': clean_text,
          }

      response_data = jsonify(json_response)
      return response_data,200
    
    else:
      #Json response for unsuccessful request
      json_response = {
              'status_code': 400,
              'description': "No file inputed",
          }
    return jsonify(json_response),400

def database_txt(kolom1, kolom2):
    conn = sqlite3.connect ("challenge.db")
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS result_cleansing (input, output)""")
    cursor.execute("""INSERT INTO result_cleansing (input, output) VALUES (?,?)""",(kolom1, kolom2))

    conn.commit()
    cursor.close()
    conn.close()
  

def databse_csv(data):
    conn = sqlite3.connect("challenge.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS result_cleansing (input, output)""")
    data.to_sql ('result_cleansing', conn, if_exists = 'append', index = False)



if __name__ == '__main__':
    app.run(debug=True)