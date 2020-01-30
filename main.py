from flask import Flask, request
from conf import auth
from handler import Message

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def token_handler():
	if request.method=='GET':
		if request.args.get('hub.verify_token')==auth.VERIFY_TOKEN:
			print('Got it')
			return request.args.get('hub.challenge')
		return 'Welcome to class captain facebook page.'
	else:
		output = request.get_json()
		Message().received(output)
		return 'success'



if __name__=="__main__":
	app.run(host='0.0.0.0', debug=True, port=3000)