from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Union
from  model import Base

# Classe que representa a entidade Planta

class Planta(Base):
    __tablename__ = 'cad_planta'

    id = Column("pk_planta", Integer, primary_key=True)
    usuario = Column(String(20))
    nome = Column(String(60))
    nome_cientifico = Column(String(100))
    quantidade = Column(Integer)
    forma_aquisicao = Column(String(40))
    porte = Column(String(40))
    luminosidade_id = Column(Integer, ForeignKey("luminosidade.pk_luminosidade"))
    observacao = Column(String(200))
    data_insercao = Column(DateTime, default=datetime.now())

    # Criando um requisito de unicidade envolvendo as informações de nome e usuario da tabela
    __table_args__ = (UniqueConstraint("nome", "usuario", name="planta_usr_uniq_id"),)


    def __init__(self, nome:str, nome_cientifico: str, quantidade:int, forma_aquisicao: str, porte: str, 
                 observacao: str, luminosidade_id: int, usuario: str, data_insercao:Union[DateTime, None] = None):
        """
        Cria uma instância de planta

        Arguments:
            usuario: nome do usuario
            nome: nome da planta
            nome_cientifico: nome cientifico da planta
            quantidade: quantidade de exemplares da plantas
            forma_aquisicao: forma de aquisição da planta
            porte: porte da planta
            luminosidade: ID da luminosidade exigida pela planta
            observacao: observações adicionais sobre a planta
            data_insercao: data de inserção da planta no banco de dados
        """
        self.nome = nome
        self.nome_cientifico = nome_cientifico
        self.quantidade = quantidade
        self.forma_aquisicao = forma_aquisicao
        self.porte = porte
        self.luminosidade_id = luminosidade_id
        self.observacao = observacao
        self.usuario = usuario

        # se não for informada, será a data exata da inserção no banco
        if data_insercao:
            self.data_insercao = data_insercao
