# 관련 패키지 다운
```
$ pip install -r requirements.txt
$ pip install PyMYSQL
```

# 실행 예시
## 교수님이  세팅한 그대로 동작하도록 만들었습니다. 추가로 백그라운드로 이미 돌려놨습니다.
```
$ sudo systemctl uwsgi-app@memo.service
```

# 직접 실행
```
$ uwsgi --ini uwsgi.ini
```

# 확인 방법
## nginx 로 /memo url로 확인

# 실행 환경

## DB
- DB는 MYSQL latest 이미지를 사용했습니다. docker container를 사용해서 만들었습니다.
- user table => user(user_id varchar(50), user_name varchar(50);
- memo table => memo(memo_id int auto_increment, user_id varchar(50), content text, primary key(memo_id));
- user table은 따로 PK를 두지 않았습니다. 테스트 환경에서 중복 회원가입의 예외 케이스가 발생할 수도 있어서 두지 않았습니다.
- memo table은 memo_id라는 column을 PK로 두고 동일한 사용자가 동일한 값을 입력할 경우에 대한 처리를 하기 위해 했습니다.
- 
## uwsgi
- 교수님이 구축해 놓으신 uwsgi 환경 그대로를 쓸 수 있도록 맞춰놓았고 백그라운드로 돌아갈 수 있도록 실행해 놓은 상태입니다.

## 코드 설명
- table 생성은 초기에 해놔서 프로그램이 시작되더라도 exist 옵션으로 체크를 하고 생성하지 않아도 되도록 구현했습니다.
- home 함수에서는 cookie가 존재한다면cookie에 해당하는 user의 이름을 가져와서 저장하도록 하는 sql문을 실행하도록 했습니다.
- onLogin 함수에서는 네이버 로그인 요청하는 코드가 작성되어 있습니다.
- onOAuthAuthorizationCodeRedirected 함수에서는 url에서 state, code 값을 추출 후 access token을 받아오는 naver api를 호출하도록 했습니다. 그리고 받아온 access_token으로 사용자 정보를 받아오는 api를 호출 후 사용자 정보를 디비에 저장하도록 sql문을 작성했습니다.
- get_memo함수는 쿠키가 존재한다면 user_id에 해당하는 memo 값을 불러와 각 tuple을 키가 text인 json 형태로 배열을 만들어서 돌려줍니다.
- post_new_memo 함수는 사용자로부터 입력 받은 메모 내용을 디비에 저장하는 sql을 던지는 함수를 작성했습니다.
- delete_cookie 함수는 쿠키를 크롬 개발자 모드에서 지우는게 번거로워서 쿠키를 삭제하는 함수를 만들었습니다.
