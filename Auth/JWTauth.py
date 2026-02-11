import bcrypt

from datetime import timedelta, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status , Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError

from sqlalchemy.orm import Session

from Database.init_db import get_db
from Database.model import CreateUserRequest, Token
from Database.db_model import EmployeeCreate
from .hasher import Hashing
from Secret import Setting

router = APIRouter(
    prefix="/auth",
    tags=['auth']
)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

db_dependency = Annotated[Session, Depends(get_db)]
req_form = Annotated[OAuth2PasswordRequestForm, Depends()]

ACCESS_TOKEN_EXPIRE_MINUTES = 20 #Minutes
REFRESH_TOKEN_EXPIRE_DAYS = 7 #Days


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_employee(
    db: db_dependency,
    create_emp_req: CreateUserRequest
):

    # Hash the password
    hashed_password = Hashing.hash_password(create_emp_req.password)

    employee = EmployeeCreate(
        Emp_email=create_emp_req.Emp_email,
        hashed_pass=hashed_password
    )

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return {"message": "Employee created successfully"}


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: req_form,
    db: db_dependency,
    response: Response,
):
    emp = authenticate_emp(form_data.username, form_data.password, db)

    if not emp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate Employee."
        )

    access_token = create_access_token(
        employee=emp.Emp_email,
        emp_id=emp.Emp_id,
        expires_delta=timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,               # ← Change to True in production!
        samesite="lax",
        max_age=20 * 60,
        path="/",
    )

    return {"access_token": access_token, "token_type": "bearer"}

def authenticate_emp(Emp_email: str, password: str, db):

    emp = db.query(EmployeeCreate).filter(
        EmployeeCreate.Emp_email == Emp_email).first()

    if not emp:
        return False
    if not Hashing.verify_password(password, emp.hashed_pass):
        return False

    return emp


def create_access_token(employee: str, emp_id: int, expires_delta: timedelta):

    encode = {'sub': employee, 'id': emp_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})

    return jwt.encode(encode, Setting.SECRET_KEY, algorithm=Setting.ALGORITHM)





async def get_current_emp(token: Annotated[str, Depends(oauth2_bearer)]):
    
    try:
        payload = jwt.decode(token, Setting.SECRET_KEY,
                             algorithms=[Setting.ALGORITHM])
        
        username: str = payload.get('sub')
        emp_id: int = payload.get('id')

        if username is None or emp_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate employee")

        return {'Emp_email': username, 'Emp_id': emp_id}
    
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate employee")
