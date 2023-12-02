#!/bin/python3
from http import HTTPStatus
import random
import requests
import json
import urllib
import pymysql

from flask import abort, Flask, make_response, render_template, Response, redirect, request, url_for

app = Flask(__name__)


naver_client_id = '7uuf9qK_4aGHWYLcK_PY'
naver_client_secret = '9Ssj480u5p'
naver_redirect_uri = 'http://60182225-lb-545786833.ap-northeast-2.elb.amazonaws.com/memo/token'
#naver_redirect_uri = 'http://52.79.148.250:8000/memo/token'
'''
  본인 app 의 것으로 교체할 것.
  여기 지정된 url 이 http://localhost:8000/auth 처럼 /auth 인 경우
  아래 onOAuthAuthorizationCodeRedirected() 에 @app.route('/auth') 태깅한 것처럼 해야 함
'''


@app.route('/')
def home():
    # 쿠기를 통해 이전에 로그인 한 적이 있는지를 확인한다.
    # 이 부분이 동작하기 위해서는 OAuth 에서 access token 을 얻어낸 뒤
    # user profile REST api 를 통해 유저 정보를 얻어낸 뒤 'userId' 라는 cookie 를 지정해야 된다.
    # (참고: 아래 onOAuthAuthorizationCodeRedirected() 마지막 부분 response.set_cookie('userId', user_id) 참고)
    userId = request.cookies.get('userId', default=None)
    name = None

    ####################################################
    # TODO: 아래 부분을 채워 넣으시오.
    #       userId 로부터 DB 에서 사용자 이름을 얻어오는 코드를 여기에 작성해야 함
    #con = pymysql.connect(host='127.0.0.1', user='root', password='1234', db='back', charset='utf8')
    con = pymysql.connect(host='3.36.97.36', user='root', passwd='1234', db='back', charset='utf8')
    cursor=con.cursor()
    
    if(userId != None):
        cursor.execute('select user_name from user where user_id=%s', (userId, ))

        #result=cursor.fetchall()
        result = cursor.fetchone()
    
        if(type(result) != None and result): 
            name = result[0]
    
        con.close()


    ####################################################


    # 이제 클라에게 전송해 줄 index.html 을 생성한다.
    # template 로부터 받아와서 name 변수 값만 교체해준다.
    return render_template('index.html', name=name)


# 로그인 버튼을 누른 경우 이 API 를 호출한다.
# OAuth flow 상 브라우저에서 해당 URL 을 바로 호출할 수도 있으나,
# 브라우저가 CORS (Cross-origin Resource Sharing) 제약 때문에 HTML 을 받아온 서버가 아닌 곳에
# HTTP request 를 보낼 수 없는 경우가 있다. (예: 크롬 브라우저)
# 이를 우회하기 위해서 브라우저가 호출할 URL 을 HTML 에 하드코딩하지 않고,
# 아래처럼 서버가 주는 URL 로 redirect 하는 것으로 처리한다.
#
# 주의! 아래 API 는 잘 동작하기 때문에 손대지 말 것
@app.route('/login')
def onLogin():
    params={
            'response_type': 'code',
            'client_id': naver_client_id,
            'redirect_uri': naver_redirect_uri,
            'state': random.randint(0, 10000)
        }
    urlencoded = urllib.parse.urlencode(params)
    url = f'https://nid.naver.com/oauth2.0/authorize?{urlencoded}'
    return redirect(url)

# 아래는 Redirect URI 로 등록된 경우 호출된다.
# 만일 본인의 Redirect URI 가 http://localhost:8000/auth 의 경우처럼 /auth 대신 다른 것을
# 사용한다면 아래 @app.route('/auth') 의 내용을 그 URL 로 바꿀 것
@app.route('/token')
def onOAuthAuthorizationCodeRedirected():
    # TODO: 아래 1 ~ 4 를 채워 넣으시오.

    # 1. redirect uri 를 호출한 request 로부터 authorization code 와 state 정보를 얻어낸다.
    state = int(request.args.get('state', 0))
    code = str(request.args.get('code', ''))

    # 2. authorization code 로부터 access token 을 얻어내는 네이버 API 를 호출한다.
    params={
            'grant_type': 'authorization_code',
            'client_id': naver_client_id,
            'client_secret': naver_client_secret,
            'redirect_uri': naver_redirect_uri,
            'code': code,
            'state': state
        }
    urlencoded = urllib.parse.urlencode(params)
    url = f'https://nid.naver.com/oauth2.0/token?{urlencoded}'

    response = requests.get(url)
    
    header = None

    if(response.status_code == 200):
        responseJson = json.loads(response.text)
        header = "Bearer " + responseJson['access_token']
    else:
        print(f'Request failed with status {response.status_code}')

    # 3. 얻어낸 access token 을 이용해서 프로필 정보를 반환하는 API 를 호출하고,
    #    유저의 고유 식별 번호를 얻어낸다.
    url = "https://openapi.naver.com/v1/nid/me"
    call = urllib.request.Request(url)
    call.add_header("Authorization", header)
    response = urllib.request.urlopen(call)
    rescode = response.getcode()
    
    userInfoJson = None
    
    if(rescode==200):
        response_body = response.read()
        userInfoJson = json.loads(response_body)
        
        print("userInfo: " ,userInfoJson)
    else:
        print("Error Code:" + rescode)

    # 4. 얻어낸 user id 와 name 을 DB 에 저장한다.
    if(userInfoJson != None):
        user_id = userInfoJson['response']['email']
        user_name = userInfoJson['response']['name']
        
        con = pymysql.connect(host='3.36.97.36', user='root', passwd='1234', db='back', charset='utf8')
        cursor=con.cursor()
        
        cursor.execute('insert into user(user_id, user_name) value (%s, %s)', (user_id, user_name))
        con.commit()
        
        con.close()
    else:
        print('Get Profile APi Response error')


    # 5. 첫 페이지로 redirect 하는데 로그인 쿠키를 설정하고 보내준다.
    if(user_id is not None and user_name is not None):
        response = redirect('/memo')
        response.set_cookie('userId', user_id)
        return response
    return redirect('/')


@app.route('/memo', methods=['GET'])
def get_memos():
    # 로그인이 안되어 있다면 로그인 하도록 첫 페이지로 redirect 해준다.
    userId = request.cookies.get('userId', default=None)
    if not userId:
        return redirect('/')

    # TODO: DB 에서 해당 userId 의 메모들을 읽어오도록 아래를 수정한다.
    result = []
    
    con = pymysql.connect(host='3.36.97.36', user='root', passwd='1234', db='back', charset='utf8')
    cursor=con.cursor()
    
    cursor.execute('select content from memo where user_id=%s', (userId, ))
    datas = cursor.fetchall()
            
    con.close()
    
    for data in datas:
        result.append({'text': data[0]})
    # memos라는 키 값으로 메모 목록 보내주기
    return {'memos': result}


@app.route('/memo', methods=['POST'])
def post_new_memo():
    # 로그인이 안되어 있다면 로그인 하도록 첫 페이지로 redirect 해준다.
    userId = request.cookies.get('userId', default=None)
    if not userId:
        return redirect('/')

    # 클라이언트로부터 JSON 을 받았어야 한다.
    if not request.is_json:
        abort(HTTPStatus.BAD_REQUEST)

    # TODO: 클라이언트로부터 받은 JSON 에서 메모 내용을 추출한 후 DB에 userId 의 메모로 추가한다.
    text = request.get_json()['text']
    
    con = pymysql.connect(host='3.36.97.36', user='root', passwd='1234', db='back', charset='utf8')
    cursor=con.cursor()
    
    cursor.execute('insert into memo(user_id, content) value (%s, %s)', (userId, text))
    con.commit()
    
    con.close()
    
    return '', HTTPStatus.OK

#delete cookie
@app.route('/delete')
def delete_cookie():
    resp = make_response(redirect('/'))
    resp.set_cookie('userId', '', expires=0)
    return resp


if __name__ == '__main__':
    app.run('0.0.0.0', port=10001, debug=True)
