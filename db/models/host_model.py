from dataclasses import dataclass
from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


@dataclass
class HostInfo:
    id: int
    name: str
    ip_addr: str
    port: str
    user: str
    password: str
    mac_addr: str


class HostModel(Base):
    __tablename__ = "my_host"

    host_name = Column(String(), primary_key=True, nullable=False)
    ip_addr = Column(String(15), nullable=True)
    port = Column(String(5), nullable=True)
    user = Column(String(), nullable=True)
    password = Column(String(), nullable=True)
    mac_addr = Column(String(20), nullable=True)

    def __repr__(self):
        return (f"<HostModel(host_name={self.host_name}, ip_addr='{self.ip_addr}, port='{self.port}', "
                f"user='{self.user}, password='{self.password}, mac_addr='{self.mac_addr})>")
