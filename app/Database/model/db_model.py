from sqlalchemy import Boolean, Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.Database.config import Base

class EmployeeCreate(Base):
    __tablename__ = "new_emp"

    Emp_id = Column(Integer, primary_key=True, index=True)
    Emp_email = Column(String(255), unique=True, nullable=False)
    hashed_pass = Column(String(255), nullable=False)

    details = relationship(
        "EmployeeDetailes",
        back_populates="employee",
        uselist=False,
        cascade="all, delete"
    )


class EmployeeDetailes(Base):
    __tablename__ = "emp_details"

    Emp_id = Column(
        Integer,
        ForeignKey("new_emp.Emp_id"),
        primary_key=True
    )

    Emp_name = Column(String(255), nullable=False)
    Emp_email = Column(String(255), index=True)  # optional
    Age = Column(Integer)
    User_Is_Active = Column(Boolean, default=True)

    employee = relationship(
        "EmployeeCreate",
        back_populates="details"
    )
