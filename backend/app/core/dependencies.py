"""
Request-level dependencies — reusable pieces every protected route needs.

`get_current_user` is the single dependency that turns "this request has
an Authorization header" into "this request is authenticated as this
specific User row." Any router that wants protection just adds:

    current_user: User = Depends(get_current_user)

to its function signature. FastAPI runs this before the route body, and
if it raises, the route body never executes.
"""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database import get_db
from app.exceptions import UnauthorizedException
from app.models.user import User

# HTTPBearer expects "Authorization: Bearer <token>" — matches the
# header format specified in the API requirements. Using this (rather
# than OAuth2PasswordBearer, which assumes an OAuth2 form-based login
# flow) keeps Swagger's "Authorize" dialog a simple "paste your token"
# box, matching our plain JSON login endpoint.
#
# auto_error=False: by default, HTTPBearer raises its own 403 when the
# Authorization header is missing entirely, before our code runs. That
# conflates "no credentials provided" with "forbidden" — the correct
# status for missing/invalid credentials is 401, and 403 should be
# reserved for "authenticated, but not allowed" (e.g. a future
# non-admin role). Disabling auto_error lets us raise a consistent
# UnauthorizedException (-> 401) for every "not properly authenticated"
# case, whether the header is missing, malformed, or expired.
_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Decode the bearer token, look up the user it refers to, and return it.

    Raises UnauthorizedException (-> HTTP 401) if:
      - no Authorization header was provided at all
      - the token is missing/malformed/expired/signed with the wrong key
      - the token is valid but the user it refers to no longer exists
        (e.g. deleted after the token was issued)
    """
    if credentials is None:
        raise UnauthorizedException("Not authenticated")

    token = credentials.credentials

    try:
        payload = decode_access_token(token)
    except JWTError:
        raise UnauthorizedException("Invalid or expired token")

    username = payload.get("sub")
    if username is None:
        raise UnauthorizedException("Invalid token payload")

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise UnauthorizedException("User no longer exists")

    return user
