from dataclasses import dataclass

from flask_sqlalchemy import SQLAlchemy

db: SQLAlchemy = SQLAlchemy()

class Storage(db.Model):

    __tablename__ = 'storage'

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime)
    id_sens = db.Column(db.Integer)
    temp = db.Column(db.Float)
    status = db.Column(db.String)
    

    def __repr__(self) -> str:
        return f'(id={self.id!r}, data={self.data!r}, id_sens = {self.id_sens!r}, temp= {self.temp!r}, status= {self.status!r} )'

    # def serialize(self) -> dict:
    #     return {
    #         'id': self.id,
    #         'data': self.data,
    #         't1'  : self.t1,
    #         't2'  : self.t2,
    #         't3'  : self.t3,
    #         't4'  : self.t4,
    #         'status' : self.status
    #     }    

class Relays(db.Model):

    __tablename__ = 'relays'

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime)
    relay1 = db.Column(db.Integer)
    relay2 = db.Column(db.Integer)

    def __repr__(self) -> str:
        return f'(id={self.id!r}, data={self.data!r}, relay1 ={self.relay1!r}, relay2 = {self.relay2!r}) '

class Stats(db.Model):

    __tablename__ = 'statistiche'

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime)
    id_sens = db.Column(db.Integer)
    media = db.Column(db.Float)
    devs = db.Column(db.Float)
    min = db.Column(db.Float)
    max = db.Column(db.Float)

    def __repr__(self) -> str:
        return f'(id={self.id!r},data={self.data!r}, media={self.media!r}, devs= {self.devs!r}, min= {self.min!r}, max= {self.max!r} )'

    # def serialize(self) -> dict:
    #     return {
    #         'id': self.id,
    #         'data': self.data,
    #         'interfaces': [interface.serialize() for interface in self.interfaces],
    #         'temps': self.temps,
    #         'status' : self.status
    #     }