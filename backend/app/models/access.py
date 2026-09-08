"""通行人员（人脸底库）+ 核验记录"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey

from pgvector.sqlalchemy import Vector

from app.models.base import BaseModel


class AccessPerson(BaseModel):
    """通行人员 - 人脸底库（只存特征向量，不存原图）"""
    __tablename__ = "biz_access_person"

    user_id = Column(Integer, ForeignKey("sys_user.id"), comment="关联用户ID")
    name = Column(String(64), nullable=False, comment="姓名")
    # 人脸特征向量（pgvector），提取后原图立即删除
    face_feature = Column(Vector(512), comment="人脸特征向量(512维)")
    face_image_url = Column(String(255), comment="人脸图片(仅临时，提取后删除)")
    status = Column(Integer, default=1, comment="状态 1启用 0禁用")


class VerifyRecord(BaseModel):
    """人脸核验记录"""
    __tablename__ = "biz_verify_record"

    person_id = Column(Integer, ForeignKey("biz_access_person.id"), comment="通行人员ID")
    name = Column(String(64), comment="姓名")
    similarity = Column(Float, comment="相似度")
    success = Column(Integer, default=0, comment="是否通过 1是 0否")
    device_id = Column(String(64), comment="设备编号")
    image_url = Column(String(255), comment="核验图片")
    verified_at = Column(DateTime, comment="核验时间")
