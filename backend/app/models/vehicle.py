"""车辆档案 + 车位 + 进出记录 + 月卡"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Vehicle(BaseModel):
    """车辆档案"""
    __tablename__ = "biz_vehicle"

    plate_number = Column(String(20), unique=True, index=True, nullable=False, comment="车牌号")
    owner_name = Column(String(64), comment="车主姓名")
    owner_id = Column(Integer, ForeignKey("sys_user.id"), comment="车主用户ID")
    vehicle_type = Column(String(32), default="小型汽车", comment="车辆类型")
    color = Column(String(16), comment="颜色")
    is_monthly = Column(Boolean, default=False, comment="是否月卡车辆")
    status = Column(Integer, default=1, comment="状态 1正常 0禁用")


class ParkingSpot(BaseModel):
    """车位"""
    __tablename__ = "biz_parking_spot"

    spot_code = Column(String(32), unique=True, nullable=False, comment="车位编号")
    area = Column(String(64), comment="区域")
    status = Column(Integer, default=0, comment="状态 0空闲 1占用 2维护")
    vehicle_id = Column(Integer, ForeignKey("biz_vehicle.id"), comment="占用车辆ID")


class VehicleAccessRecord(BaseModel):
    """车辆进出记录"""
    __tablename__ = "biz_vehicle_access_record"

    plate_number = Column(String(20), index=True, nullable=False, comment="车牌号")
    vehicle_id = Column(Integer, ForeignKey("biz_vehicle.id"), comment="车辆ID")
    direction = Column(String(8), nullable=False, comment="方向 in入场 out出场")
    spot_id = Column(Integer, ForeignKey("biz_parking_spot.id"), comment="车位ID")
    image_url = Column(String(255), comment="抓拍图片")
    access_time = Column(DateTime, comment="进出时间")


class MonthlyCard(BaseModel):
    """月卡白名单"""
    __tablename__ = "biz_monthly_card"

    vehicle_id = Column(Integer, ForeignKey("biz_vehicle.id"), nullable=False, comment="车辆ID")
    plate_number = Column(String(20), index=True, comment="车牌号")
    start_date = Column(DateTime, comment="生效日期")
    end_date = Column(DateTime, comment="到期日期")
    status = Column(Integer, default=1, comment="状态 1有效 0过期")
