"""通行人员（人脸底库）+ 核验记录

合规要点（《个人信息保护法》）：
- 人脸是敏感个人信息，**只存特征向量，不存原图**
- 采集前需用户单独授权同意
- 数据本地存储，不出园

face_feature 使用 pgvector 的 Vector(512) 类型，
比对时用 SQL 运算符 `<=>` 计算余弦距离，返回相似度最高的人员。
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey

from pgvector.sqlalchemy import Vector

from app.models.base import BaseModel


class AccessPerson(BaseModel):
    """通行人员 - 人脸底库

    人脸原图提取特征后**立即删除**，face_image_url 字段仅在提取过程中临时使用。
    底库规模千人以内时，pgvector 全表扫描性能足够（毫秒级）。
    """
    __tablename__ = "biz_access_person"

    user_id = Column(Integer, ForeignKey("sys_user.id"), comment="关联用户ID")
    name = Column(String(64), nullable=False, comment="姓名")
    # InsightFace buffalo_l 模型输出 512 维 float32 向量
    face_feature = Column(Vector(512), comment="人脸特征向量(512维)")
    face_image_url = Column(String(255), comment="人脸图片(仅临时，提取后删除)")
    status = Column(Integer, default=1, comment="状态 1启用 0禁用")


class VerifyRecord(BaseModel):
    """人脸核验记录

    每次闸机核验都留痕，用于追溯和异常分析。
    """
    __tablename__ = "biz_verify_record"

    person_id = Column(Integer, ForeignKey("biz_access_person.id"), comment="通行人员ID")
    name = Column(String(64), comment="姓名")
    similarity = Column(Float, comment="相似度(0-1)，超过阈值判定通过")
    success = Column(Integer, default=0, comment="是否通过 1是 0否")
    device_id = Column(String(64), comment="设备编号（对应闸机）")
    image_url = Column(String(255), comment="核验抓拍图")
    verified_at = Column(DateTime, comment="核验时间")
