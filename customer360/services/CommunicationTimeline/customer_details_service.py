from ...utils.exceptions import CalculationError
from ...utils.logger import logger
from datetime import datetime
from ...core.config import Setting
import json
from typing import List, Dict, Any, Optional


class CustomerDetailsService:
    
    def _load_data(self, filename: str) -> List[Dict[str, Any]]:
        """
        Load JSON data from file in the data/ directory.
        Uses Setting.BASE_DATA_PATH + filename (no leading /)
        """
        try:
            # IMPORTANT: no leading '/' — this is relative to BASE_DATA_PATH
            full_path = Setting.BASE_DATA_PATH / filename
            
            if not full_path.is_file():
                logger.warning(f"Data file not found: {full_path}")
                return []
            
            with full_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                logger.error(f"Data in {filename} is not a list")
                return []
                
            logger.debug(f"Loaded {len(data)} records from {filename}")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {filename}: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to load {filename}: {e}", exc_info=True)
            return []

    def _find_customer(
        self,
        customers: List[Dict[str, Any]],
        customer_id: Optional[str] = None,
        name: Optional[str] = None,
        mobile: Optional[str] = None,
        email: Optional[str] = None,
        pan: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Find first matching customer (case-insensitive for name/email)"""
        search_params = {
            "customer_id": customer_id,
            "name": name.lower() if name else None,
            "mobile": mobile,
            "email": email.lower() if email else None,
            "pan": pan,
        }

        for cust in customers:
            if search_params["customer_id"] and cust.get("customer_id") == search_params["customer_id"]:
                return cust
            if search_params["name"] and cust.get("name", "").lower() == search_params["name"]:
                return cust
            if search_params["mobile"] and cust.get("mobile") == search_params["mobile"]:
                return cust
            if search_params["email"] and cust.get("email", "").lower() == search_params["email"]:
                return cust
            if search_params["pan"] and cust.get("pan") == search_params["pan"]:
                return cust
        
        return None

    def _get_loans_for_customer(
        self,
        loans: List[Dict[str, Any]],
        customer_id: str
    ) -> List[Dict[str, Any]]:
        """Get all loans linked to customer_id"""
        return [
            {
                "type": l.get("type", ""),
                "lan": l.get("lan", ""),
                "zone": l.get("zone", ""),
                "status": l.get("status", ""),
                "outstanding": l.get("outstanding", 0.0),
                "emi": l.get("emi", 0.0)
            }
            for l in loans
            if l.get("customer_id") == customer_id
        ]

    def _get_communications_for_loan(
        self,
        communications: List[Dict[str, Any]],
        customer_id: str,
        lan: Optional[str] = None,
        filter_type: str = "ALL"
    ) -> List[Dict[str, Any]]:
        """Get filtered communications for customer + optional LAN"""
        valid_types = {"ALL", "Email", "SMS", "WhatsApp", "Post", "IVR", "Failed", "Delivered"}
        if filter_type not in valid_types:
            raise ValueError(f"Invalid filter_type: {filter_type}. Allowed: {valid_types}")

        filtered = []
        for comm in communications:
            if comm.get("customer_id") != customer_id:
                continue
            if lan and comm.get("lan") != lan:
                continue

            comm_type   = comm.get("channel") or comm.get("type", "")
            comm_status = comm.get("status", "")

            if filter_type == "ALL" or comm_type == filter_type or comm_status == filter_type:
                filtered.append({
                    "type": comm_type,
                    "status": comm_status,
                    "message": comm.get("message", ""),
                    "sent_time": comm.get("sent_time", ""),
                    "delivered_time": comm.get("delivered_time", ""),
                    "template": comm.get("template", ""),
                    "id": comm.get("id", ""),
                    "lan": comm.get("lan", "")
                })
        
        return filtered

    def get_customer_details(
        self,
        customer_id: Optional[str] = None,
        name: Optional[str] = None,
        mobile: Optional[str] = None,
        email: Optional[str] = None,
        pan: Optional[str] = None,
        lan: Optional[str] = None,
        filter_type: str = "ALL"
    ) -> Dict[str, Any]:
        """
        Main method: find customer → get loans → get filtered communications
        Returns dict with customer, loans list, communications list
        """
        try:
            # Load all three files (normalized form)
            customers     = self._load_data("customers.json")
            loans         = self._load_data("loans.json")
            communications = self._load_data("communications.json")

            # Find customer
            customer = self._find_customer(
                customers, customer_id, name, mobile, email, pan
            )
            if not customer:
                logger.info("No customer found for provided search criteria")
                return {"customer": None, "loans": [], "communications": []}

            cust_id = customer.get("customer_id")
            if not cust_id:
                logger.error("Customer found but missing customer_id")
                return {"customer": None, "loans": [], "communications": []}

            # Get related data
            cust_loans = self._get_loans_for_customer(loans, cust_id)
            comms = self._get_communications_for_loan(communications, cust_id, lan, filter_type)

            result = {
                "customer": {
                    "name": customer.get("name", ""),
                    "customer_id": cust_id,
                    "ucic_id": customer.get("ucic_id", ""),
                    "mobile": customer.get("mobile", ""),
                    "email": customer.get("email", ""),
                    "pan": customer.get("pan", ""),
                    "branch": customer.get("branch", ""),
                    "risk": customer.get("risk", "Low")
                },
                "loans": cust_loans,
                "communications": comms
            }

            logger.info(f"Successfully fetched details for customer {cust_id} "
                       f"(loans: {len(cust_loans)}, comms: {len(comms)})")
            return result

        except ValueError as ve:
            logger.error(f"Invalid input in customer-details: {ve}")
            raise CalculationError(str(ve))
        except Exception as e:
            logger.error(f"Critical error in get_customer_details: {e}", exc_info=True)
            raise CalculationError(f"Failed to fetch customer details: {str(e)}")


def get_customer_details_service() -> CustomerDetailsService:
    return CustomerDetailsService()