from sqlalchemy import Column, String, Integer, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Union
from  model import Base

# Classe que representa a entidade Luminosidade

class Luminosidade(Base):
    __tablename__ = 'luminosidade'

    id = Column("pk_luminosidade", Integer, primary_key=True)
    lum_nome = Column(String(60), unique=True)
    data_insercao = Column(DateTime, default=datetime.now())

    def __init__(self, lum_nome: str, data_insercao:Union[DateTime, None] = None):
        """
        Cria uma instância de luminosidade possível para uma planta

        Arguments:
            lum_nome:      descrição do tipo de luminosidade
            data_insercao: data de inserção do dado de luminosidade no banco de dados
        """
        self.lum_nome = lum_nome
        
        # se não for informada, será a data exata da inserção no banco
        if data_insercao:
            self.data_insercao = data_insercao
