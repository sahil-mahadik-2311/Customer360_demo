import bcrypt

from datetime import timedelta, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError

from sqlalchemy.orm import Session
from Database.init_db import get_db
from Database.model import CreateUserRequest, Token
from Database.db_model import EmployeeCreate


router = APIRouter(
    prefix="/auth",
    tags=['auth']
)

SECRET_KEY = 'a8e1b061b98c56f7147aa5762ff45d6bd54d3402315d6dd7a6ba0190e1f297a4'
ALGORITHM = 'HS256'

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_employee(
    db: db_dependency,
    create_emp_req: CreateUserRequest
):
    # Validate password length
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    # Hash the password
    hashed_password = hash_password(create_emp_req.password)

    employee = EmployeeCreate(
        Emp_email=create_emp_req.Emp_email,
        hashed_pass=hashed_password
    )

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return {"message": "Employee created successfully"}


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):

    emp = authenticate_emp(form_data.username, form_data.password, db)

    if not emp:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate Employee.")

    token = create_access_token(
        emp.Emp_email, emp.Emp_id, timedelta(minutes=20))

    return {"access_token": token, "token_type": "bearer"}


def authenticate_emp(Emp_email: str, password: str, db):

    emp = db.query(EmployeeCreate).filter(
        EmployeeCreate.Emp_email == Emp_email).first()

    if not emp:
        return False
    if not bcrypt.checkpw(password.encode('utf-8'), emp.hashed_pass.encode('utf-8')):
        return False

    return emp


def create_access_token(employee: str, emp_id: int, expires_delta: timedelta):
    encode = {'sub': employee, 'id': emp_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_emp(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        emp_id: int = payload.get('id')

        if username is None or emp_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate employee")

        return {'Emp_email': username, 'Emp_id': emp_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate employee")
