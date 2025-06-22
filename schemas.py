from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class BrokerBase(BaseModel):
    name: str
    image_url: str
    qr_code_url: str

class BrokerCreate(BrokerBase):
    pass

class Broker(BrokerBase):
    id: int
    score: int

    class Config:
        from_attributes = True

class ReferralBase(BaseModel):
    broker_id: int
    customer_email: str
    customer_name: str

class ReferralCreate(ReferralBase):
    pass

class Referral(ReferralBase):
    id: int
    referral_date: datetime

    class Config:
        from_attributes = True

class BrokerWithReferrals(Broker):
    referrals: List[Referral] = [] 