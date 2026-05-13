from enum import Enum

class MessageSource(str, Enum):
    WHATSAPP = "whatsapp"
    BOOKING_COM = "booking_com"
    AIRBNB = "airbnb"
    INSTAGRAM = "instagram"
    DIRECT = "direct"

class QueryType(str, Enum):
    PRE_SALES_AVAILABILITY = "pre_sales_availability"
    PRE_SALES_PRICING = "pre_sales_pricing"
    POST_SALES_CHECKIN = "post_sales_checkin"
    SPECIAL_REQUEST = "special_request"
    COMPLAINT = "complaint"
    GENERAL_ENQUIRY = "general_enquiry"

class ActionType(str, Enum):
    AUTO_SEND = "auto_send"
    AGENT_REVIEW = "agent_review"
    ESCALATE = "escalate"