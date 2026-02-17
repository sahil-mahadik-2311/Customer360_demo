from ...utils.exceptions import CalculationError
from ...utils.logger import logger
from ...core.config import Setting
import json
from typing import List, Dict, Any, Optional


class CustomerListService:
    
    def _load_customers(self) -> List[Dict[str, Any]]:
        """Load customer data from JSON file (only customer details)"""
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
            logger.debug(f"Loaded {len(data)} customers")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to load customers: {e}", exc_info=True)
            return []

    def get_customers(
        self,
        search: Optional[str] = None,  # free text: name, id, mobile, email, pan
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Fetch paginated list of customers (only basic details)
        - search: partial match on name, customer_id, mobile, email, pan
        - limit/offset: pagination (max 100 per page)
        Returns: customers list + total count
        """
        try:
            all_customers = self._load_customers()
            if not all_customers:
                return {"customers": [], "total": 0}

            filtered = []
            search_lower = search.lower().strip() if search else None

            for cust in all_customers:
                if search_lower:
                    name = cust.get("name", "").lower()
                    cust_id = cust.get("customer_id", "").lower()
                    mobile = cust.get("mobile", "").replace(" ", "").lower()
                    email = cust.get("email", "").lower()
                    pan = cust.get("pan", "").lower()

                    if not any([
                        search_lower in name,
                        search_lower in cust_id,
                        search_lower in mobile,
                        search_lower in email,
                        search_lower in pan
                    ]):
                        continue

                filtered.append({
                    "name": cust.get("name", ""),
                    "customer_id": cust.get("customer_id", ""),
                    "ucic_id": cust.get("ucic_id", ""),
                    "mobile": cust.get("mobile", ""),
                    "email": cust.get("email", ""),
                    "pan": cust.get("pan", ""),
                    "branch": cust.get("branch", ""),
                    "risk": cust.get("risk", "Low")
                })

            total = len(filtered)
            paginated = filtered[offset : offset + limit]

            logger.info(f"Fetched {len(paginated)} customers (total: {total}, search: '{search}')")
            return {
                "customers": paginated,
                "total": total,
                "limit": limit,
                "offset": offset
            }

        except Exception as e:
            logger.error(f"Customer list fetch failed: {e}", exc_info=True)
            raise CalculationError(f"Failed to fetch customers: {str(e)}")


def get_customer_list_service() -> CustomerListService:
    return CustomerListService()