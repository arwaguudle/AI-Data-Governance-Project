from enum import Enum

from pydantic import BaseModel


class Consumer(BaseModel):
    teamId: str
    data_application_name: str
    data_application_description: str


class ExpectedDecision(Enum):
    ACCEPT = "accept"
    REJECT = "reject"


class Provider(BaseModel):
    dataProductId: str
    outputPortId: str


class AccessRequest(BaseModel):
    title: str
    purpose: str
    provider: Provider
    consumer: Consumer
    expected_decision: ExpectedDecision


class Requests(BaseModel):
    requests: list[AccessRequest]
