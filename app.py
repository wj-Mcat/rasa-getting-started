from flask import Flask, jsonify

from flasgger import Swagger

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'My API',
    'uiversion': 3
}
swagger = Swagger(app, template_file='rasa-swagger.yml')


# open website: http://127.0.0.1:5004/apidocs
app.run(port=5004)