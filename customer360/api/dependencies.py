from typing import Annotated , Dict , Any
from fastapi import Depends , HTTPException , status
from ..utils.logger import logger
from sqlalchemy.orm import Session
from ..Database.session import get_db
from ..services import AuthenticationService , TokenService 
from ..utils.exceptions import TokenError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from ..services import dashboard_services as dashservices
# ==================== Dependencies ====================



dash_act_esc = Annotated[dashservices.activate_escalation_service,Depends(dashservices.activate_escalation_service.get_active_escalations)]
dash_avg_res = Annotated[dashservices.average_resolution_service,Depends(dashservices.average_resolution_service.get_avg_resolution_time)]
dash_csat_score = Annotated[dashservices.csat_score_service,Depends(dashservices.csat_score_service.get_csat_score)]
dash_del_rate = Annotated[dashservices.delivery_rate_service,Depends(dashservices.delivery_rate_service.get_delivery_rate)]
dash_fail_msg = Annotated[dashservices.failed_message_service,Depends(dashservices.failed_message_service.get_failed_messages)]
dash_del_sta = Annotated[dashservices.delivery_status_service,Depends(dashservices.delivery_status_service.get_delivery_status)]

db_dependency = Annotated[Session, Depends(get_db)]

req_form = Annotated[OAuth2PasswordRequestForm, Depends()]
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='api/v1/auth/token')


def get_auth_service(db: db_dependency) -> AuthenticationService:
    """Dependency to get authentication service instance"""
    return AuthenticationService(db)


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

