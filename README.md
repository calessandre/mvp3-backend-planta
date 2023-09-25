# Como executar a API pelo Docker

Clonar o repositório e acessar o diretório raiz (mvp3-backend-planta) pelo terminal para executar os comandos abaixo.

Ativar o docker:
```
sudo service docker start
```

Fazer o build da imagem:
```
docker build -t img-backend-planta .
```

Criar a rede para conexão dos dois containers (não é necessário fazer, caso tenha executado na configuração do outro container do mvp):
```
docker network create plnt_rede -d bridge
```

Executar o container (usar a porta 5000 e o nome indicado):
```
docker run -p 5000:5000 --name cntn-backend-planta --network plnt_rede img-backend-planta
```

Abrir http://localhost:5000/ no navegador para verificar o status da API em execução.

Deverá ser exibida a página inicial com a documentação em formato swagger da API com as rotas implementadas.

## API EXTERNA - detalhamento

No MVP, uma API externa foi utilizada para retornar a data e hora utilizadas para armazenamento de informações no banco de dados. Não há necessidade de cadastro prévio para uso.

* Chamada:
    * Método: GET
    * Rota: https://tools.aimylogic.com/api/now

* Parâmetros: 
    * tz:        fuso horário desejado
    * format:    formato em que a data deve ser retornada

* Retorno:
    * timezone:  fuso horário
    * formatted: data formatada
    * timestamp: timestamp
    * weekDay:   dia da semana
    * day:       dia
    * month:     mês
    * year:      ano    
    * hour:      hora
    * minute:    minuto

Mais informações: https://help.aimylogic.com/docs/en/how-to-create-a-script/current_datetime/
