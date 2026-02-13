from Secret import Setting
from datetime import timedelta , datetime
from jose import jwt , JWTError
from ..utils.exceptions import DatabaseError , EmployeeNotFoundError , InvalidCredentialsError ,TokenError , AuthenticationError
from ..utils.logger import logger
from typing import Dict , Any

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

