from datetime import datetime

from sqlalchemy import UniqueConstraint

from extensions import db


class Contact(db.Model):
    __tablename__ = "contacts"
    __table_args__ = (UniqueConstraint("pt_id", "sender_id", name="uq_contact_pt_sender"),)

    id = db.Column(db.Integer, primary_key=True)
    pt_id = db.Column(db.Integer, db.ForeignKey("pts.id"), nullable=False)
    sender_id = db.Column(db.String, nullable=False)
    channel = db.Column(db.String, nullable=False, default="instagram")
    status = db.Column(db.String, nullable=False, default="in_progress")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    pt = db.relationship("PT", back_populates="contacts")
    messages = db.relationship("Message", back_populates="contact", lazy="dynamic")
