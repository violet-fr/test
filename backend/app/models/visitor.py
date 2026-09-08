"""访客管理三表：邀请 -> 预约 -> 到访记录

业务流程：
1. 员工在小程序发起邀请(VisitorInvitation)，生成预约码
2. 访客收到预约码，到访时扫码触发审批或直接核验
3. 审批通过后生成预约(VisitorAppointment)
4. 访客到场扫码 -> 到访记录(VisitRecord) check_in
5. 访客离场 -> check_out，全流程闭环
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey

from app.models.base import BaseModel


class VisitorInvitation(BaseModel):
    """访客邀请（员工发起）

    appointment_code 为唯一预约码，访客凭此码到访核验。
    """
    __tablename__ = "biz_visitor_invitation"

    inviter_id = Column(Integer, ForeignKey("sys_user.id"), nullable=False, comment="邀请人ID")
    visitor_name = Column(String(64), nullable=False, comment="访客姓名")
    visitor_phone = Column(String(20), nullable=False, comment="访客手机号")
    visit_date = Column(DateTime, nullable=False, comment="到访日期")
    visit_purpose = Column(String(255), comment="来访事由")
    visit_duration = Column(Integer, default=2, comment="预计时长(小时)")
    appointment_code = Column(String(64), unique=True, index=True, comment="预约码")
    status = Column(Integer, default=0, comment="状态 0待审批 1已通过 2已驳回 3已到访 4已离场 5已取消")


class VisitorAppointment(BaseModel):
    """访客预约"""
    __tablename__ = "biz_visitor_appointment"

    invitation_id = Column(Integer, ForeignKey("biz_visitor_invitation.id"), comment="关联邀请ID")
    visitor_name = Column(String(64), nullable=False, comment="访客姓名")
    visitor_phone = Column(String(20), comment="访客手机号")
    visit_date = Column(DateTime, comment="到访日期")
    visit_purpose = Column(String(255), comment="来访事由")
    approver_id = Column(Integer, ForeignKey("sys_user.id"), comment="审批人ID")
    approve_time = Column(DateTime, comment="审批时间")
    status = Column(Integer, default=0, comment="状态 0待审批 1已通过 2已驳回 3已到访 4已离场")


class VisitRecord(BaseModel):
    """到访记录"""
    __tablename__ = "biz_visit_record"

    appointment_id = Column(Integer, ForeignKey("biz_visitor_appointment.id"), comment="预约ID")
    visitor_name = Column(String(64), comment="访客姓名")
    check_in_time = Column(DateTime, comment="到访时间")
    check_out_time = Column(DateTime, comment="离场时间")
    status = Column(Integer, default=1, comment="状态 1到访中 2已离场")
