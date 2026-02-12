
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


# ==================== Custom Exceptions ====================
class KPIError(Exception):
    """Base exception for KPI calculation errors"""
    pass


class DataLoadError(KPIError):
    """Raised when data loading fails"""
    pass


class CalculationError(KPIError):
    """Raised when KPI calculation fails"""
    pass

