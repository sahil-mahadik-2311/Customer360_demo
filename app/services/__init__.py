from .auth_service import AuthenticationService as ASer
from .token_service import TokenService as Ts
from .dashboard_services.message_service import MessageService as Ms



create_emp = ASer.create_employee
emp_email = ASer.get_employee_by_email
auth = ASer.authenticate

Auth = {"create_employee": create_emp(),
        "get_employee_by_email": emp_email(),
        "authenticate":auth()}



