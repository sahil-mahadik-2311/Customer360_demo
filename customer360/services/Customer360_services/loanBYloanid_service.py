from ...utils.exceptions import CalculationError
from ...utils.logger import logger
from datetime import datetime, date
from ...core.config import Setting
import json
from typing import Dict, Any, List


class PaymentBehaviourService:
    
    def _load_customers(self) -> List[Dict[str, Any]]:
        path = Setting.BASE_DATA_PATH / "customers.json"
        if not path.is_file():
            logger.warning(f"Customers file not found: {path}")
            return []
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(f"Failed to load customers: {e}")
            return []

    def _load_loans(self) -> List[Dict[str, Any]]:
        path = Setting.BASE_DATA_PATH / "loans.json"
        if not path.is_file():
            logger.warning(f"Loans file not found: {path}")
            return []
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(f"Failed to load loans: {e}")
            return []

    def _load_payments(self) -> List[Dict[str, Any]]:
        path = Setting.BASE_DATA_PATH / "payments.json"
        if not path.is_file():
            logger.warning(f"Payments file not found: {path}")
            return []
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(f"Failed to load payments: {e}")
            return []

    def get_payment_behaviour(
        self,
        customer_id: str,
        lan: str
    ) -> Dict[str, Any]:

        cust_id_clean = customer_id.strip()
        lan_clean = lan.strip()

        if not cust_id_clean:
            raise ValueError("customer_id is required")
        if not lan_clean:
            raise ValueError("lan is required")

        try:
            customers = self._load_customers()
            loans     = self._load_loans()
            payments  = self._load_payments()

            # Find customer
            customer = next(
                (c for c in customers if c.get("customer_id") == cust_id_clean),
                None
            )
            if not customer:
                return {"customer": None, "loan": None, "payment_behaviour": {}}

            # Find the specific loan
            loan = next(
                (l for l in loans
                 if l.get("customer_id") == cust_id_clean and l.get("lan") == lan_clean),
                None
            )
            if not loan:
                return {
                    "customer": {
                        "name"       : customer.get("name", ""),
                        "customer_id": cust_id_clean,
                        "ucic_id"    : customer.get("ucic_id", ""),
                        "mobile"     : customer.get("mobile", ""),
                        "email"      : customer.get("email", ""),
                        "pan"        : customer.get("pan", ""),
                        "branch"     : customer.get("branch", ""),
                        "risk"       : customer.get("risk", "Low")
                    },
                    "loan": None,
                    "payment_behaviour": {}
                }

            expected_emi = loan.get("emi", 0.0)

            # Get payments for this loan
            # FIX: Don't filter by payment_date — missed payments have payment_date: null
            relevant_payments = [
                p for p in payments
                if p.get("customer_id") == cust_id_clean
                and p.get("lan") == lan_clean
            ]

            # Generate last 6 months (from current month backward)
            today = date.today()
            last_6_months = []
            missed_count  = 0
            current_month = today

            for i in range(6):
                month_key = current_month.strftime("%Y-%m")

                # FIX: Match payment by due_date month (not payment_date, which can be null)
                month_payment = next(
                    (
                        p for p in relevant_payments
                        if p.get("due_date") and
                        datetime.fromisoformat(p["due_date"]).strftime("%Y-%m") == month_key
                    ),
                    None
                )

                # FIX: Use status field directly from JSON
                if month_payment:
                    payment_status = month_payment.get("status", "").strip()  # "Paid" or "Missed"
                    amount_paid    = month_payment.get("amount_paid", 0.0)
                    amount_due     = month_payment.get("amount_due", expected_emi)
                    missed         = payment_status == "Missed"
                else:
                    # No payment record found for this month
                    month_date  = date(current_month.year, current_month.month, 1)
                    is_past     = month_date < date(today.year, today.month, 1)
                    payment_status = "Missed" if is_past else "Pending"
                    amount_paid    = 0.0
                    amount_due     = expected_emi
                    missed         = is_past  # only past months count as missed

                if missed:
                    missed_count += 1

                last_6_months.append({
                    "month"         : month_key,
                    "due_date"      : month_payment.get("due_date")      if month_payment else None,
                    "payment_date"  : month_payment.get("payment_date")  if month_payment else None,
                    "payment_method": month_payment.get("payment_method") if month_payment else None,
                    "emi_amount"    : amount_due,
                    "paid_amount"   : amount_paid,
                    "status"        : payment_status,
                    "missed"        : missed
                })

                # Move to previous month
                if current_month.month == 1:
                    current_month = current_month.replace(year=current_month.year - 1, month=12)
                else:
                    current_month = current_month.replace(month=current_month.month - 1)

            last_6_months.reverse()  # oldest → newest

            missed_note = f"{missed_count} missed payment{'s' if missed_count != 1 else ''} in last 6 months"

            result = {
                "customer": {
                    "name"       : customer.get("name", ""),
                    "customer_id": cust_id_clean,
                    "ucic_id"    : customer.get("ucic_id", ""),
                    "mobile"     : customer.get("mobile", ""),
                    "email"      : customer.get("email", ""),
                    "pan"        : customer.get("pan", ""),
                    "branch"     : customer.get("branch", ""),
                    "risk"       : customer.get("risk", "Low")
                },
                "loan": {
                    "type"       : loan.get("type", ""),
                    "lan"        : loan.get("lan", ""),
                    "zone"       : loan.get("zone", ""),
                    "status"     : loan.get("status", ""),
                    "outstanding": loan.get("outstanding", 0.0),
                    "emi"        : expected_emi,
                    "active"     : loan.get("active", True)
                },
                "payment_behaviour": {
                    "last_6_emis" : last_6_months,
                    "missed_count": missed_count,
                    "missed_note" : missed_note
                }
            }

            logger.info(
                f"Fetched payment behaviour for customer {cust_id_clean}, "
                f"loan {lan_clean} (missed: {missed_count})"
            )
            return result

        except ValueError as ve:
            logger.error(f"Invalid input: {ve}")
            raise CalculationError(str(ve))
        except Exception as e:
            logger.error(f"Critical error in payment_behaviour: {e}", exc_info=True)
            raise CalculationError(f"Failed to fetch payment behaviour: {str(e)}")


def get_payment_behaviour_service() -> PaymentBehaviourService:
    return PaymentBehaviourService()