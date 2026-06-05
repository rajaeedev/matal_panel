from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, Literal


class CreateUser(BaseModel):
    name: str = Field(min_length=3, max_length=10)
    total: Optional[float] = None
    used: Optional[float] = None
    expiry_date: date


class UpdateUser(BaseModel):
    name: str
    total: Optional[float] = None
    used: Optional[float] = None
    expiry_date: Optional[date]
    status: bool = True


class NodeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    address: str
    tunnel_address: Optional[str] = Field(default=None)
    protocol: Literal["tcp", "udp"] = Field(default="tcp")
    ovpn_port: int = Field(default=1194)
    port: int
    key: str = Field(min_length=10, max_length=128)
    status: bool = Field(default=True)
    set_new_setting: bool = Field(default=False)


class AdminCreate(BaseModel):
    username: str = Field(min_length=3, max_length=10)
    password: str = Field(min_length=6, max_length=20)
