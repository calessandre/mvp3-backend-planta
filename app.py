from flask_openapi3 import OpenAPI, Info, Tag
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS
from flask import redirect
from model import Session, Planta, Luminosidade
from schemas import *
import requests, json
from datetime import datetime

info = Info(title="API para gerenciamento de coleção de plantas", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# Definindo tags
home_tag = Tag(name="Documentação", description="Documentação da API.")
planta_tag = Tag(name="API", description="Adição, visualização e remoção de plantas.")

# Implementando as rotas

# Rota para documentação swagger
@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi/swagger - abre a documentação swagger da API proposta.
    """
    return redirect('/openapi/swagger')

# Rota para adicionar planta (POST)
@app.post('/planta', tags=[planta_tag],
          responses={"200": PlantaViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_planta(form: PlantaSchema):
    """Adiciona uma nova planta e retorna uma representação da planta.
    """

    nome_da_planta = form.nome

    # Chamada ao serviço externo (API) para obter a data e hora atuais para armazenamento no banco de dados
    response_api_ext = requests.get('https://tools.aimylogic.com/api/now?tz=America/Sao_Paulo&format=dd/MM/yyyy%20HH:mm')
    resposta = json.loads(response_api_ext.content)
    data_formatada = resposta['formatted']
    data_e_hora = datetime.strptime(data_formatada, "%d/%m/%Y %H:%M")

    # Chamada ao serviço interno (API) para obter os dados adicionais da planta informada
    
    # Caso execute na maquina local, descomentar a linha que contem localhost e comentar a outra. Se executar no
    # Docker, faça o contrário
    
    response_api_int = requests.get('http://cntn-backend-biblioteca:5001/bibplanta?planta_nome='+nome_da_planta)
    #response_api_int = requests.get('http://localhost:5001/bibplanta?planta_nome='+nome_da_planta)
    
    #print(response_api_int.text)
    #print(response_api_int.status_code)

    try:
        # criando conexão com a base de dados
        session = Session()
    except Exception as e:
        # caso ocorra um erro
        error_msg = "Não foi possível conectar ao banco de dados."
        return {"message": error_msg}, 400

    if response_api_int.status_code == 200:
        resposta_api_int = json.loads(response_api_int.content)
        api_nome_cientifico = resposta_api_int['nome_cientifico']
        api_luminosidade = resposta_api_int['luminosidade']
        api_porte = resposta_api_int['altura']

        #session = Session()
        
        # fazendo a busca da luminosidade na tabela
        lum_busca = session.query(Luminosidade).filter(Luminosidade.lum_nome == api_luminosidade).first()

        if not lum_busca:
            # se a luminosidade não foi encontrada, insere
            #print(api_luminosidade)
            luminosidade = Luminosidade(lum_nome=api_luminosidade)
            session.add(luminosidade)
            lum_busca = session.query(Luminosidade).filter(Luminosidade.lum_nome == api_luminosidade).first()
            #print ('ID da luminosidade inserida: '+str(lum_busca.id))
            session.commit()
            id_luminosidade = lum_busca.id
        else:
            #print('ID da luminosidade encontrada: '+str(lum_busca.id))    
            id_luminosidade = lum_busca.id

    else:
        api_nome_cientifico = "nao encontrado"
        #api_luminosidade = "nao encontrada"
        api_porte = "nao encontrado"
        id_luminosidade = None

    planta = Planta(
        nome=form.nome,
        quantidade=form.quantidade,
        forma_aquisicao=form.forma_aquisicao,
        observacao=form.observacao,
        nome_cientifico=api_nome_cientifico,
        porte=api_porte,
        luminosidade_id=id_luminosidade,
        usuario=form.usuario,
        data_insercao=data_e_hora
        )

    try:
        # criando conexão com a base de dados
        #session = Session()
        # adicionando planta
        session.add(planta)
        # efetivando o comando de inclusão de nova planta na tabela
        session.commit()
        return apresenta_planta_insert(planta), 200

    except IntegrityError as e:
        # retorna erro caso já haja planta com mesmo nome cadastrada na tabela ou outro erro de integridade
        error_msg = "Planta de mesmo nome já salva na base."
        return {"message": error_msg}, 409

    except Exception as e:
        # caso ocorra um erro diferente dos anteriores
        error_msg = "Não foi possível salvar novo item."
        return {"message": error_msg}, 400


# Rota para buscar todas as plantas cadastradas para um usuario (GET)
@app.get('/plantas', tags=[planta_tag],
         responses={"200": ListagemPlantasSchema, "404": ErrorSchema})
def get_plantas(query: PlantasUsuarioBuscaSchema):
    """Faz a busca por todos as plantas cadastradas e retorna uma representação da listagem de plantas.
    """
    usuario = query.usuario

    # criando conexão com a base
    session = Session()
    
    # fazendo a busca
    plantas = session.query(Planta, Luminosidade).outerjoin(Luminosidade, 
                    Planta.luminosidade_id == Luminosidade.id).with_entities(Planta.quantidade, 
                                                                             Planta.forma_aquisicao, 
                                                                             Planta.id,
                                                                             Planta.luminosidade_id, 
                                                                             Planta.nome, 
                                                                             Luminosidade.lum_nome,
                                                                             Planta.nome_cientifico, 
                                                                             Planta.observacao, 
                                                                             Planta.porte,
                                                                             Planta.usuario).filter(Planta.usuario == usuario)
    if not plantas:
        # se não há plantas cadastradas
        return {"plantas": []}, 200
    else:
        # retorna a representação de planta
        return apresenta_plantas(plantas), 200


# Rota para apagar uma planta pelo id (DELETE).
@app.delete('/planta', tags=[planta_tag],
            responses={"200": PlantaDelSchema, "404": ErrorSchema})
def del_planta(query: PlantaBuscaSchema):
    """Deleta uma planta a partir do id informado e retorna uma mensagem de confirmação da remoção.
    """
    planta_id = query.planta_id

    # criando conexão com a base
    session = Session()
    # fazendo a remoção
    count = session.query(Planta).filter(Planta.id == planta_id).delete()
    session.commit()

    if count:
        # retorna a mensagem de confirmação e o id da planta removida
        return {"message": "Planta removida.", "id": planta_id}
    else:
        # se a planta não foi encontrada, retorna mensagem de erro
        error_msg = "Planta não encontrada na base."
        return {"message": error_msg}, 404

 #############################

# Rota para teste de CHAMADA DE API interna 
@app.get('/testeAPIInt', tags=[planta_tag])
def testeAPIInt():
    # Caso execute na maquina local, descomentar a linha que contem localhost e comentar a outra. Se executar no
    # Docker, faça o contrário
    response = requests.get('http://cntn-backend-biblioteca:5001/bibplanta?planta_nome=Anturio')
    #response = requests.get('http://localhost:5001/bibplanta?planta_nome=Anturio')

    #print (response.text)
    #print (response.status_code)
    #print (response.content)
   
    return (response.content)

# Rota para teste de CHAMADA DE API externa
@app.get('/testeAPIExt', tags=[planta_tag])
def testeAPIExt():
    response = requests.get('https://tools.aimylogic.com/api/now?tz=America/Sao_Paulo&format=dd/MM/yyyy%20HH:mm:ss')
    
    #print (response.text)
    #print (response.status_code)
    #print(response.content)
         
    return (response.content)
