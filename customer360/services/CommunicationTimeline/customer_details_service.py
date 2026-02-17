"""
Customer Details Service - Final Fixed Version
Root cause: channel vs type field confusion + whitespace in JSON data
"""

from ...utils.exceptions import CalculationError
from ...utils.logger import logger
from ...core.config import Setting
import json
from typing import List, Dict, Any, Optional, Union


class CustomerDetailsService:

    def _load_data(self, filename: str) -> List[Dict[str, Any]]:
        """Load JSON data from file in the data/ directory."""
        try:
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

    def _normalize(self, value: Any) -> str:
        """Safely strip and normalize any string value"""
        if value is None:
            return ""
        return str(value).strip()

    def _find_customer(
        self,
        customers: List[Dict[str, Any]],
        customer_id: Optional[str] = None,
        name: Optional[str] = None,
        mobile: Optional[str] = None,
        email: Optional[str] = None,
        pan: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Find first matching customer (case-insensitive & partial for name/email)"""
        name_lower  = name.lower().strip()  if name  else None
        email_lower = email.lower().strip() if email else None

        for cust in customers:
            if customer_id and self._normalize(cust.get("customer_id")) == self._normalize(customer_id):
                return cust
            if pan and self._normalize(cust.get("pan")) == self._normalize(pan):
                return cust
            if mobile:
                mob         = self._normalize(cust.get("mobile")).replace("+91", "").replace(" ", "")
                search_mob  = self._normalize(mobile).replace("+91", "").replace(" ", "")
                if mob == search_mob:
                    return cust
            if name_lower and name_lower in self._normalize(cust.get("name")).lower():
                return cust
            if email_lower and email_lower in self._normalize(cust.get("email")).lower():
                return cust

        return None

    def _get_loans_for_customer(
        self,
        loans: List[Dict[str, Any]],
        customer_id: str
    ) -> List[Dict[str, Any]]:
        """Get all loans linked to customer_id"""
        matched = []
        for l in loans:
            loan_cust_id = self._normalize(l.get("customer_id"))
            if loan_cust_id == customer_id:
                matched.append({
                    "type"       : self._normalize(l.get("type")),
                    "lan"        : self._normalize(l.get("lan")),
                    "zone"       : self._normalize(l.get("zone")),
                    "status"     : self._normalize(l.get("status")),
                    "outstanding": l.get("outstanding", 0.0),
                    "emi"        : l.get("emi", 0.0),
                    "active"     : l.get("active", True)
                })

        logger.debug(f"Found {len(matched)} loans for customer_id='{customer_id}'")
        return matched

    def _get_communications(
        self,
        communications: List[Dict[str, Any]],
        customer_id: str,
        allowed_lans: Optional[set] = None,
        filter_type: str = "ALL"
    ) -> List[Dict[str, Any]]:
        """Get filtered communications for a customer"""
        valid_types = {"ALL", "Email", "SMS", "WhatsApp", "Post", "IVR", "Failed", "Delivered"}
        if filter_type not in valid_types:
            raise ValueError(f"Invalid filter_type: '{filter_type}'. Must be one of {valid_types}")

        filtered = []

        for comm in communications:
            # ── Step 1: Match customer_id exactly ──────────────────────────────
            comm_cust_id = self._normalize(comm.get("customer_id"))
            if comm_cust_id != customer_id:
                logger.debug(f"Skipping comm {comm.get('id')}: customer_id mismatch "
                             f"('{comm_cust_id}' != '{customer_id}')")
                continue

            # ── Step 2: Match LAN if filter is active ─────────────────────────
            comm_lan = self._normalize(comm.get("lan"))
            if allowed_lans is not None and comm_lan not in allowed_lans:
                logger.debug(f"Skipping comm {comm.get('id')}: LAN '{comm_lan}' "
                             f"not in allowed {allowed_lans}")
                continue

            # ── Step 3: Get channel (your JSON uses 'channel' not 'type') ──────
            # Your JSON: "channel": "SMS", "type": "Outbound"
            # channel = communication medium (SMS/Email/WhatsApp)
            # type    = direction (Inbound/Outbound)
            comm_channel = self._normalize(comm.get("channel"))   # SMS, Email, WhatsApp
            comm_status  = self._normalize(comm.get("status"))    # Delivered, Failed

            # ── Step 4: Apply filter_type ──────────────────────────────────────
            if filter_type != "ALL":
                # filter_type can match channel (SMS) or status (Delivered/Failed)
                if comm_channel != filter_type and comm_status != filter_type:
                    continue

            # ── Step 5: Build communication record ────────────────────────────
            filtered.append({
                "id"             : self._normalize(comm.get("id")),
                "lan"            : comm_lan,
                "channel"        : comm_channel,
                "direction"      : self._normalize(comm.get("type")),  # Inbound/Outbound
                "status"         : comm_status,
                "message"        : comm.get("message") or "",
                "sent_time"      : comm.get("sent_time") or "",
                "delivered_time" : comm.get("delivered_time") or "",
                "template"       : comm.get("template") or "",
                "issue_type"     : comm.get("issue_type") or None,
            })

        logger.debug(
            f"_get_communications result: {len(filtered)} records | "
            f"customer='{customer_id}' | lans={allowed_lans or 'ALL'} | filter='{filter_type}'"
        )
        return filtered

    def get_customer_details(
        self,
        customer_id: Optional[str] = None,
        name: Optional[str] = None,
        mobile: Optional[str] = None,
        email: Optional[str] = None,
        pan: Optional[str] = None,
        lan: Optional[Union[str, List[str]]] = None,
        filter_type: str = "ALL"
    ) -> Dict[str, Any]:
        """
        Main method to get customer details with loans and communications.

        - Always returns ALL loans (for dropdown)
        - lan=None  → communications across ALL loans
        - lan=str   → communications for that single loan only
        - lan=list  → communications for those specific loans only
        """
        try:
            customers      = self._load_data("customers.json")
            loans_data     = self._load_data("loans.json")
            communications = self._load_data("communications.json")

            # ── Step 1: Find customer ──────────────────────────────────────────
            customer = self._find_customer(customers, customer_id, name, mobile, email, pan)
            if not customer:
                logger.info(f"No customer found | search params: "
                            f"id={customer_id}, name={name}, mobile={mobile}, "
                            f"email={email}, pan={pan}")
                return {"customer": None, "loans": [], "total_communications": 0}

            cust_id = self._normalize(customer.get("customer_id"))
            if not cust_id:
                logger.error("Customer record found but customer_id is empty")
                return {"customer": None, "loans": [], "total_communications": 0}

            # ── Step 2: Get all loans ──────────────────────────────────────────
            cust_loans = self._get_loans_for_customer(loans_data, cust_id)

            # ── Step 3: Normalize lan → set or None ───────────────────────────
            allowed_lans: Optional[set] = None
            if isinstance(lan, str):
                lan_clean = lan.strip()
                if lan_clean:
                    allowed_lans = {lan_clean}
            elif isinstance(lan, list):
                cleaned = {l.strip() for l in lan if l and l.strip()}
                allowed_lans = cleaned if cleaned else None

            # ── Step 4: Fetch filtered communications ─────────────────────────
            all_comms = self._get_communications(
                communications, cust_id, allowed_lans, filter_type
            )

            # ── Step 5: Group communications by LAN ───────────────────────────
            comms_by_lan: Dict[str, List[Dict[str, Any]]] = {}
            for comm in all_comms:
                key = comm["lan"]
                comms_by_lan.setdefault(key, []).append(comm)

            logger.debug(
                f"Comms grouped by LAN: { {k: len(v) for k, v in comms_by_lan.items()} }"
            )

            # ── Step 6: Attach communications to each loan ────────────────────
            enriched_loans = []
            for loan in cust_loans:
                loan_lan = loan["lan"]

                # FIX: If specific LANs requested, skip loans that don't match
                if allowed_lans is not None and loan_lan not in allowed_lans:
                    continue  # ← skip other loans entirely

                loan["communications"] = comms_by_lan.get(loan_lan, [])
                enriched_loans.append(loan)
                
            # ── Step 7: Build final response ──────────────────────────────────
            result = {
                "customer": {
                    "name"       : customer.get("name", ""),
                    "customer_id": cust_id,
                    "ucic_id"    : customer.get("ucic_id", ""),
                    "mobile"     : customer.get("mobile", ""),
                    "email"      : customer.get("email", ""),
                    "pan"        : customer.get("pan", ""),
                    "branch"     : customer.get("branch", ""),
                    "risk"       : customer.get("risk", "Low")
                },
                "loans"               : enriched_loans,
                "total_communications": len(all_comms),
                "filtered_by_lan"     : list(allowed_lans) if allowed_lans else "ALL",
                "filter_type"         : filter_type
            }

            logger.info(
                f"customer-details success | customer='{cust_id}' | "
                f"loans={len(enriched_loans)} | comms={len(all_comms)} | "
                f"lan_filter={allowed_lans or 'ALL'} | type_filter='{filter_type}'"
            )
            return result

        except ValueError as ve:
            logger.error(f"Invalid input in get_customer_details: {ve}")
            raise CalculationError(str(ve))
        except Exception as e:
            logger.error(f"Critical error in get_customer_details: {e}", exc_info=True)
            raise CalculationError(f"Failed to fetch customer details: {str(e)}")


def get_customer_details_service() -> CustomerDetailsService:
    return CustomerDetailsService()