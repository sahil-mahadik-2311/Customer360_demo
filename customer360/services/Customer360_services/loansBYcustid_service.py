from ...utils.exceptions import CalculationError
from ...utils.logger import logger
from ...core.config import Setting
import json
from typing import Dict, Any, Optional, List


class CustomerByIdService:
    
    def _load_customers(self) -> List[Dict[str, Any]]:
        """Load customers from JSON file"""
        path = Setting.BASE_DATA_PATH / "customers.json"
        if not path.is_file():
            logger.warning(f"Customers file not found: {path}")
            return []
        
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                logger.error("Customers data is not a list")
                return []
            return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in customers.json: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to load customers: {e}", exc_info=True)
            return []

    def _load_loans(self) -> List[Dict[str, Any]]:
        """Load loans from JSON file"""
        path = Setting.BASE_DATA_PATH / "loans.json"
        if not path.is_file():
            logger.warning(f"Loans file not found: {path}")
            return []
        
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                logger.error("Loans data is not a list")
                return []
            return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in loans.json: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to load loans: {e}", exc_info=True)
            return []

    def get_customer_by_id(self, customer_id: str) -> Dict[str, Any]:
        """
        Fetch full customer details by customer_id:
        - Customer profile
        - All loans associated with this customer
        """
        if not customer_id or not customer_id.strip():
            raise ValueError("customer_id is required and cannot be empty")

        try:
            customers = self._load_customers()
            loans = self._load_loans()

            if not customers:
                logger.info("No customers found in file")
                return {"customer": None, "loans": []}

            # Find customer by exact ID
            customer = None
            for cust in customers:
                if cust.get("customer_id") == customer_id.strip():
                    customer = cust
                    break

            if not customer:
                logger.info(f"No customer found with ID: {customer_id}")
                return {"customer": None, "loans": []}

            # Get all loans for this customer
            cust_loans = [
                {
                    "type": l.get("type", ""),
                    "lan": l.get("lan", ""),
                    "zone": l.get("zone", ""),
                    "status": l.get("status", ""),
                    "outstanding": l.get("outstanding", 0.0),
                    "emi": l.get("emi", 0.0),
                    "active": l.get("active", True)
                }
                for l in loans
                if l.get("customer_id") == customer_id
            ]

            result = {
                "customer": {
                    "name": customer.get("name", ""),
                    "customer_id": customer.get("customer_id", ""),
                    "ucic_id": customer.get("ucic_id", ""),
                    "mobile": customer.get("mobile", ""),
                    "email": customer.get("email", ""),
                    "pan": customer.get("pan", ""),
                    "branch": customer.get("branch", ""),
                    "risk": customer.get("risk", "Low")
                },
                "loans": cust_loans,
                "total_loans": len(cust_loans)
            }

            logger.info(f"Successfully fetched customer {customer_id} with {len(cust_loans)} loans")
            return result

        except ValueError as ve:
            logger.error(f"Invalid input in get_customer_by_id: {ve}")
            raise CalculationError(str(ve))
        except Exception as e:
            logger.error(f"Critical error in get_customer_by_id: {e}", exc_info=True)
            raise CalculationError(f"Failed to fetch customer details: {str(e)}")


def get_customer_by_id_service() -> CustomerByIdService:
    return CustomerByIdService()