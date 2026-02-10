from pydantic import BaseModel , EmailStr , field_validator


class CreateUserRequest(BaseModel):
    Emp_email: EmailStr
    password: str 

    @field_validator('password')
    def validate_password_length(cls, v):
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password cannot exceed 72 bytes')
        return v

class Token(BaseModel):

    access_token: str
    token_type: str