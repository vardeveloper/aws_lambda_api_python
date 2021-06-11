from datetime import datetime, timedelta
from sqlalchemy import Column, String, Integer, JSON, Date

from models.base import Base, engine, Session

Base.metadata.create_all(engine)
session = Session()


class Preference(Base):
    __tablename__ = 'preferences'

    id = Column(Integer, primary_key=True)
    uuid = Column(String)
    email = Column(String)
    brand = Column(String)
    type_events = Column(String)
    valor = Column(JSON)
    date_insert = Column(Date)
    date_update = Column(Date)

    def get_rows_by_brand(self, brand, days=None):
        """ Retorna la lista de los suscritos del día de ayer por marca """

        query = session.query(self.__class__)
        query = query.filter(self.__class__.brand == brand)
        query = query.filter(self.__class__.type_events == 'newsletter')

        if days is not None:
            _date = datetime.today().date() - timedelta(days=days)
            _date = _date.strftime('%Y-%m-%d')
            query = query.filter(self.__class__.date_update >= _date)

        instances = query.all()

        return list(map(lambda x: x.valor, instances))
