from typing import  Optional , Annotated 
from fastapi import Depends

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..utils.exceptions import DatabaseError , EmployeeNotFoundError , InvalidCredentialsError  , AuthenticationError
from ..Database.session import get_db
from ..schemas.model import CreateUserRequest
from ..Database.model.db_model import EmployeeCreate
from ..core.security import Hashing
from ..utils.logger import logger

db_dependency = Annotated[Session, Depends(get_db)]


# ==================== Authentication Service ====================
class AuthenticationService:
    """Handles authentication logic"""

    def __init__(self, db: Session):
        self.db = db

    def get_employee_by_email(self, email: str) -> Optional[EmployeeCreate]:
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
        try:
            employee = self.get_employee_by_email(email)

            if not employee:
                logger.warning(f"Authentication failed: Employee not found - {email}")
                raise EmployeeNotFoundError(f"No employee found with email: {email}")

            if not Hashing.verify_password(password, employee.hashed_pass):
                logger.warning(f"Authentication failed: Invalid password for {email}")
                raise InvalidCredentialsError("Invalid password")

            logger.info(f"Employee authenticated successfully: {email}")
            return employee

        except (EmployeeNotFoundError, InvalidCredentialsError):
            raise
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise AuthenticationError(f"Authentication failed: {str(e)}")



    def create_employee(self, employee_data: CreateUserRequest) -> EmployeeCreate:
        try:
            existing_emp = self.get_employee_by_email(employee_data.Emp_email)
            if existing_emp:
                logger.warning(f"Employee already exists: {employee_data.Emp_email}")
                raise DatabaseError("Employee with this email already exists")

            hashed_password = Hashing.hash_password(employee_data.password)

            employee = EmployeeCreate(
                Emp_email=employee_data.Emp_email,
                hashed_pass=hashed_password
            )

            self.db.add(employee)
            self.db.commit()
            self.db.refresh(employee)

            logger.info(f"Employee created successfully: {employee_data.Emp_email}")
            return employee

        except DatabaseError:
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error during employee creation: {str(e)}")
            raise DatabaseError(f"Failed to create employee: {str(e)}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error during employee creation: {str(e)}")
            raise DatabaseError(f"Employee creation failed: {str(e)}")



def get_auth_service(db: db_dependency) -> AuthenticationService:
        """Dependency to get authentication service instance"""
        return AuthenticationService(db)