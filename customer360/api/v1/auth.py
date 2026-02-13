"""
Authentication Module - Refactored with OOP, Exception Handling, and Logging
Now using sessionStorage on client instead of cookies
"""

from ...utils.logger import logger
from datetime import timedelta
from typing import Annotated, Dict, Any
from ...utils.exceptions import TokenError
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...utils.exceptions import DatabaseError , EmployeeNotFoundError , InvalidCredentialsError ,TokenError , AuthenticationError
from ...Database.session import get_db
from ...schemas.model import CreateUserRequest, Token
from ...services import AuthenticationService , TokenService
from ..dependencies import get_auth_service , req_form , get_current_employee 



# ==================== Configuration ====================
class AuthConfig:
    """Authentication configuration settings"""
    ACCESS_TOKEN_EXPIRE_MINUTES = 20




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
    auth_service: Annotated[AuthenticationService, Depends(get_auth_service)]
) -> Dict[str, str]:
    """
    Authenticate employee and return access token.
    Client should store it in sessionStorage.
    """
    try:
        employee = auth_service.authenticate(
            form_data.username,
            form_data.password
        )

        access_token = TokenService.create_access_token(
            employee_email=employee.Emp_email,
            emp_id=employee.Emp_id,
            expires_delta=timedelta(minutes=AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

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
    current_emp: Annotated[Dict[str, Any], Depends(get_current_employee)]
) -> Dict[str, str]:
    """
    Logical logout endpoint.
    Client should remove token from sessionStorage.
    """
    try:
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
    try:
        logger.info(f"Retrieved info for employee: {current_emp['Emp_email']}")
        return current_emp

    except Exception as e:
        logger.error(f"Error retrieving user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user information"
        )