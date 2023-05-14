import datetime
import logging
from db import db
from sqlalchemy.exc import SQLAlchemyError


class CallSidModel(db.Model):
    __tablename__ = "CallSid"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    sid = db.Column(db.String(80), unique=True, nullable=False)
    phone_number = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    
    def __init__(self, name: str, sid: str, phone_number: str):
        self.name = name
        self.sid = sid
        self.phone_number = phone_number


    @staticmethod
    def create(name, sid, phone_number):  # create new user
        callSidInsertValue = CallSidModel(name, sid, phone_number)
        try:
            logging.info(f"Logging call sid before inserting into db with name:{name}, sid:{sid} and phone_number:{phone_number}")
            db.session.add(callSidInsertValue)
            db.session.commit()
        except SQLAlchemyError as e: 
            logging.error(f'Error inserting data into db...{e}')