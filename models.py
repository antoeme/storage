from dataclasses import dataclass
from flask_sqlalchemy import SQLAlchemy

db: SQLAlchemy = SQLAlchemy()

class Storage(db.Model):

    __tablename__ = 'storage'

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String)
    temps = db.Column(db.String)
    status = db.Column(db.String)
    

    def __repr__(self) -> str:
        return f'Router(id={self.id!r}, hostname={self.hostname!r})'

    # def serialize(self) -> dict:
    #     return {
    #         'id': self.id,
    #         'data': self.data,
    #         'interfaces': [interface.serialize() for interface in self.interfaces],
    #         'temps': self.temps,
    #         'status' : self.status
    #     }