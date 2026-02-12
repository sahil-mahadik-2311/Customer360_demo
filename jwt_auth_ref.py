"""
Authentication Module - Refactored with OOP, Exception Handling, and Logging
"""

import bcrypt
import logging
from datetime import timedelta, datetime
from typing import Annotated, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Response , Cookie
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.Database.session import get_db
from Database.model import CreateUserRequest, Token
from app.Database.model.db_model import EmployeeCreate
from .hasher import Hashing
from Secret import Setting

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== Custom Exceptions ====================
class AuthenticationError(Exception):
    """Base exception for authentication errors"""
    pass


class EmployeeNotFoundError(AuthenticationError):
    """Raised when employee is not found"""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Raised when credentials are invalid"""
    pass


class TokenError(AuthenticationError):
    """Raised when token operations fail"""
    pass


class DatabaseError(Exception):
    """Raised when database operations fail"""
    pass


# ==================== Configuration ====================
class AuthConfig:
    """Authentication configuration settings"""
    ACCESS_TOKEN_EXPIRE_MINUTES = 20
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    COOKIE_NAME = "access_token"
    COOKIE_SECURE = False  # Set to True in production
    COOKIE_HTTPONLY = True
    COOKIE_SAMESITE = "lax"
    COOKIE_PATH = "/"


# ==================== Token Service ====================
class TokenService:
    """Handles all token-related operations"""

    @staticmethod
    def create_access_token(
        employee_email: str,
        emp_id: int,
        expires_delta: timedelta
    ) -> str:
        """
        Create a JWT access token

        Args:
            employee_email: Employee's email address
            emp_id: Employee's ID
            expires_delta: Token expiration time

        Returns:
            Encoded JWT token

        Raises:
            TokenError: If token creation fails
        """
        try:
            payload = {
                'sub': employee_email,
                'id': emp_id,
                'exp': datetime.utcnow() + expires_delta,
                'iat': datetime.utcnow()
            }

            token = jwt.encode(
                payload,
                Setting.SECRET_KEY,
                algorithm=Setting.ALGORITHM
            )

            logger.info(f"Access token created for employee: {employee_email}")
            return token

        except Exception as e:
            logger.error(f"Failed to create access token: {str(e)}")
            raise TokenError(f"Token creation failed: {str(e)}")

    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """
        Decode and validate JWT token

        Args:
            token: JWT token string

        Returns:
            Decoded token payload

        Raises:
            TokenError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                Setting.SECRET_KEY,
                algorithms=[Setting.ALGORITHM]
            )

            username = payload.get('sub')
            emp_id = payload.get('id')

            if username is None or emp_id is None:
                raise TokenError("Invalid token payload")

            return {'Emp_email': username, 'Emp_id': emp_id}

        except JWTError as e:
            logger.warning(f"JWT validation failed: {str(e)}")
            raise TokenError(f"Invalid token: {str(e)}")
        except Exception as e:
            logger.error(f"Token decoding error: {str(e)}")
            raise TokenError(f"Token decoding failed: {str(e)}")


# ==================== Authentication Service ====================
class AuthenticationService:
    """Handles authentication logic"""

    def __init__(self, db: Session):
        self.db = db

    def get_employee_by_email(self, email: str) -> Optional[EmployeeCreate]:
        """
        Retrieve employee by email

        Args:
            email: Employee's email address

        Returns:
            Employee object or None

        Raises:
            DatabaseError: If database query fails
        """
        try:
            employee = self.db.query(EmployeeCreate).filter(
                EmployeeCreate.Emp_email == email
            ).first()

            if employee:
                logger.info(f"Employee found: {email}")
            else:
                logger.warning(f"Employee not found: {email}")

            return employee

        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching employee: {str(e)}")
            raise DatabaseError(f"Failed to retrieve employee: {str(e)}")

    def authenticate(self, email: str, password: str) -> EmployeeCreate:
        """
        Authenticate employee with email and password

        Args:
            email: Employee's email
            password: Plain text password

        Returns:
            Authenticated employee object

        Raises:
            EmployeeNotFoundError: If employee doesn't exist
            InvalidCredentialsError: If password is incorrect
        """
        try:
            employee = self.get_employee_by_email(email)

            if not employee:
                logger.warning(
                    f"Authentication failed: Employee not found - {email}")
                raise EmployeeNotFoundError(
                    f"No employee found with email: {email}")

            if not Hashing.verify_password(password, employee.hashed_pass):
                logger.warning(
                    f"Authentication failed: Invalid password for {email}")
                raise InvalidCredentialsError("Invalid password")

            logger.info(f"Employee authenticated successfully: {email}")
            return employee

        except (EmployeeNotFoundError, InvalidCredentialsError):
            raise
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise AuthenticationError(f"Authentication failed: {str(e)}")

    def create_employee(self, employee_data: CreateUserRequest) -> EmployeeCreate:
        """
        Create a new employee

        Args:
            employee_data: Employee creation request data

        Returns:
            Created employee object

        Raises:
            DatabaseError: If employee creation fails
        """
        try:
            # Check if employee already exists
            existing_emp = self.get_employee_by_email(employee_data.Emp_email)
            if existing_emp:
                logger.warning(
                    f"Employee already exists: {employee_data.Emp_email}")
                raise DatabaseError("Employee with this email already exists")

            # Hash password
            hashed_password = Hashing.hash_password(employee_data.password)

            # Create employee instance
            employee = EmployeeCreate(
                Emp_email=employee_data.Emp_email,
                hashed_pass=hashed_password
            )

            self.db.add(employee)
            self.db.commit()
            self.db.refresh(employee)

            logger.info(
                f"Employee created successfully: {employee_data.Emp_email}")
            return employee

        except DatabaseError:
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error during employee creation: {str(e)}")
            raise DatabaseError(f"Failed to create employee: {str(e)}")
        except Exception as e:
            self.db.rollback()
            logger.error(
                f"Unexpected error during employee creation: {str(e)}")
            raise DatabaseError(f"Employee creation failed: {str(e)}")


# ==================== Cookie Manager ====================
class CookieManager:
    """Handles cookie operations"""

    @staticmethod
    def set_auth_cookie(response: Response, token: str) -> None:
        """
        Set authentication cookie in response

        Args:
            response: FastAPI Response object
            token: JWT token to store
        """
        try:
            response.set_cookie(
                key=AuthConfig.COOKIE_NAME,
                value=token,
                httponly=AuthConfig.COOKIE_HTTPONLY,
                secure=AuthConfig.COOKIE_SECURE,
                samesite=AuthConfig.COOKIE_SAMESITE,
                max_age=AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                path=AuthConfig.COOKIE_PATH,
            )
            logger.info("Authentication cookie set successfully")

        except Exception as e:
            logger.error(f"Failed to set cookie: {str(e)}")
            raise

    @staticmethod
    def clear_auth_cookie(response: Response) -> None:
        """
        Clear authentication cookie from response

        Args:
            response: FastAPI Response object
        """
        try:
            response.delete_cookie(
                key=AuthConfig.COOKIE_NAME,
                path=AuthConfig.COOKIE_PATH
            )
            logger.info("Authentication cookie cleared")

        except Exception as e:
            logger.error(f"Failed to clear cookie: {str(e)}")
            raise


# ==================== Dependencies ====================
db_dependency = Annotated[Session, Depends(get_db)]
req_form = Annotated[OAuth2PasswordRequestForm, Depends()]
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


def get_auth_service(db: db_dependency) -> AuthenticationService:
    """Dependency to get authentication service instance"""
    return AuthenticationService(db)



# Add this new dependency function
async def get_token_from_cookie_or_header(
    token: Optional[str] = Depends(oauth2_bearer),
    access_token: Optional[str] = Cookie(default=None)
) -> str:
    """
    Get token from either Authorization header or cookie
    
    Args:
        token: Token from Authorization header
        access_token: Token from cookie
        
    Returns:
        JWT token string
        
    Raises:
        HTTPException: If no token found
    """
    if token:
        return token
    
    if access_token:
        return access_token
    
    logger.warning("No authentication token provided")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


# Update get_current_employee to use the new dependency
async def get_current_employee(
    token: Annotated[str, Depends(get_token_from_cookie_or_header)]
) -> Dict[str, Any]:
    """
    Dependency to get current authenticated employee from token
    """
    try:
        return TokenService.decode_token(token)
        
    except TokenError as e:
        logger.warning(f"Token validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    


# ==================== Router Setup ====================
router = APIRouter(
    prefix="/auth",
    tags=['auth']
)


# ==================== API Endpoints ====================
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_employee(
    create_emp_req: CreateUserRequest,
    auth_service: Annotated[AuthenticationService, Depends(get_auth_service)]
) -> Dict[str, str]:
    """
    Create a new employee account

    Args:
        create_emp_req: Employee creation request
        auth_service: Authentication service dependency

    Returns:
        Success message

    Raises:
        HTTPException: If employee creation fails
    """
    try:
        auth_service.create_employee(create_emp_req)
        return {"message": "Employee created successfully"}

    except DatabaseError as e:
        if "already exists" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in create_employee endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: req_form,
    response: Response,
    auth_service: Annotated[AuthenticationService, Depends(get_auth_service)]
) -> Dict[str, str]:
    """
    Authenticate employee and return access token

    Args:
        form_data: OAuth2 password request form
        response: FastAPI response object
        auth_service: Authentication service dependency

    Returns:
        Access token and token type

    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Authenticate employee
        employee = auth_service.authenticate(
            form_data.username,
            form_data.password
        )

        # Create access token
        access_token = TokenService.create_access_token(
            employee_email=employee.Emp_email,
            emp_id=employee.Emp_id,
            expires_delta=timedelta(
                minutes=AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        # Set cookie
        CookieManager.set_auth_cookie(response, access_token)

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except (EmployeeNotFoundError, InvalidCredentialsError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except TokenError as e:
        logger.error(f"Token creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create access token"
        )
    except Exception as e:
        logger.error(f"Unexpected error in login endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/logout")
async def logout(
    response: Response,
    current_emp: Annotated[Dict[str, Any], Depends(get_current_employee)]
) -> Dict[str, str]:
    """
    Logout current employee by clearing auth cookie

    Args:
        response: FastAPI response object
        current_emp: Current authenticated employee

    Returns:
        Success message
    """
    try:
        CookieManager.clear_auth_cookie(response)
        logger.info(f"Employee logged out: {current_emp['Emp_email']}")
        return {"message": "Successfully logged out"}

    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get("/me")
async def get_current_user_info(
    current_emp: Annotated[Dict[str, Any], Depends(get_current_employee)]
) -> Dict[str, Any]:
    """
    Get current authenticated employee information

    Args:
        current_emp: Current authenticated employee from token

    Returns:
        Employee information
    """
    try:
        logger.info(f"Retrieved info for employee: {current_emp['Emp_email']}")
        return current_emp

    except Exception as e:
        logger.error(f"Error retrieving user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user information"
        )

