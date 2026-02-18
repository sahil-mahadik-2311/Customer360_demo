from typing import Annotated , Dict , Any
from fastapi import Depends , HTTPException , status
from ..utils.logger import logger
from sqlalchemy.orm import Session
from ..Database.session import get_db
from ..services import AuthenticationService , TokenService 
from ..utils.exceptions import TokenError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from ..services.auth_service import get_auth_service
# ==================== Dependencies ====================



db_dependency = Annotated[Session, Depends(get_db)]
req_form = Annotated[OAuth2PasswordRequestForm, Depends()]
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='api/v1/auth/token')




async def get_current_employee(
    token: Annotated[str, Depends(oauth2_bearer)]
) -> Dict[str, Any]:
    """
    Dependency to get current authenticated employee from Bearer token
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

emp_dependency = Annotated[dict, Depends(get_current_employee)]

