import datetime
import datetime as dt
import math
from zoneinfo import ZoneInfo

import jwt
from fastapi import Depends, HTTPException, Query

from helper import constants
from helper.constants import (ACCESS_TOKEN_EXPIRE_MINUTES,
                              REFRESH_TOKEN_EXPIRE_DAYS)


def datetimeToUTCLongJS(dt):
    # mtz = pytz.UTC
    # dt = mtz.normalize(mtz.localize(dt, is_dst=True))
    # dt = dt.replace(tzinfo=pytz.timezone('utc'))
    return int(dt.timestamp() * 1000)


def datetimeToLongJS(dt):
    return int(dt.timestamp() * 1000)


def tokenstr(token, env):
    if env == "DEV":
        token_str = "ut=" + str(token) + ";cross-site-cookie=bar; path=/"
    if env == "PROD":
        token_str = (
            "ut="
            + str(token)
            + ";cross-site-cookie=bar; SameSite=None; Secure; domain=.kejora.my.id; path=/"
        )

    return token_str


def headerstr(env):
    if env == "DEV":
        header_str = "cross-site-cookie=bar; path=/"
    if env == "PROD":
        header_str = (
            "cross-site-cookie=bar; SameSite=None; Secure; domain=.kejora.my.id; path=/"
        )

    return header_str


def response_cookies(env, token):
    if env == "DEV":
        headers = {
            "Set-Cookie": f"ut={str(token)};cross-site-cookie=bar; path=/; SameSite=None; Secure"
        }

    if env == "PROD":
        headers = {
            "Set-Cookie": f"ut={str(token)};cross-site-cookie=bar; SameSite=None; Secure; domain=.kejora.my.id; path=/"
        }

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


def create_access_token(
    data: dict, secret_key: str, expires_delta: dt.timedelta = None
):
    to_encode = data.copy()
    if expires_delta:
        expire = dt.datetime.utcnow() + expires_delta
    else:
        expire = dt.datetime.utcnow() + dt.timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")
    return encoded_jwt


def create_refresh_token(
    data: dict, secret_key: str, expires_delta: dt.timedelta = None
):
    to_encode = data.copy()
    if expires_delta:
        expire = dt.datetime.utcnow() + expires_delta
    else:
        expire = dt.datetime.utcnow() + dt.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")
    return encoded_jwt


def get_pagination(
    page: int = Query(1, alias="page", ge=1),
    per_page: int = Query(10, alias="per_page", ge=1, le=100),
):
    return {"page": page, "per_page": per_page}


def paginate(
    items: list,
    pagination: dict = Depends(get_pagination),
    status: str = constants.STATUS_SUCCESS,
    is_error: str = constants.NO,
):
    page = pagination.page
    per_page = pagination.per_page
    total_pages = math.ceil(len(items) / per_page)

    start = (page - 1) * per_page
    end = start + per_page
    total = len(items)

    if start >= total:
        return {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "data": [],
            "status": status,
            "isError": is_error,
        }

    paginated_items = items[start:end]
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "data": paginated_items,
        "status": status,
        "isError": is_error,
    }

def ensure_utc(dt: datetime) -> datetime:
    """Convert naive datetime to UTC if it has no timezone."""
    return dt.astimezone(ZoneInfo("Asia/Singapore"))  # Convert to UTC