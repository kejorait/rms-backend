import datetime

import jwt
import pytz
def datetimeToUTCLongJS(dt):
    # mtz = pytz.UTC
    # dt = mtz.normalize(mtz.localize(dt, is_dst=True))
    # dt = dt.replace(tzinfo=pytz.timezone('utc'))
    return int(dt.timestamp() * 1000)

def datetimeToLongJS(dt):
    return int(dt.timestamp() * 1000)

def tokenstr(token, env):
    if env == 'DEV':
        token_str = 'ut='+str(token)+';cross-site-cookie=bar; path=/'
    if env == 'PROD':
        token_str = 'ut='+str(token)+';cross-site-cookie=bar; SameSite=None; Secure; domain=.kejora.my.id; path=/'

    return token_str

def headerstr(env):
    if env == 'DEV':
        header_str = 'cross-site-cookie=bar; path=/'
    if env == 'PROD':
        header_str = 'cross-site-cookie=bar; SameSite=None; Secure; domain=.kejora.my.id; path=/'

    return header_str

def response_cookies(env, token):
    if env == 'DEV':
        headers = {"Set-Cookie": f"ut={str(token)};cross-site-cookie=bar; path=/; SameSite=None; Secure"}
    
    if env == 'PROD':
        headers = {"Set-Cookie": f"ut={str(token)};cross-site-cookie=bar; SameSite=None; Secure; domain=.kejora.my.id; path=/"}
    
    return headers

def verify_token(token: str, role_list: list):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload["role_cd"] not in role_list:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Authentication token",
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

