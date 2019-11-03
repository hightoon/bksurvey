from flask import Flask
from survey import Survey

app = Flask(__name__)


@app.route('/')
def hello():
    return "Hello World!"

@app.route('/bk/<code>')
def bk(code):
    q = Survey('https://tellburgerking.com.cn/', code)
    try:
        q.setup_session()
        q.submit_cn()
    except Exception as e:
        print('failed to setup survey session')
        return 'failed to setup session err %s,<h>pls check your survey code</h>'%(e,)
    for i in range(28):
        q.submit_data()
        if q.done:
            return q.resptext
    return 'nothing here..'
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
