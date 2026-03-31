from flask import Flask, jsonify, request
import random
import firebase_admin
from firebase_admin import credentials, firestore
from auth import token_obrigatorio, gerar_token
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json 

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
CORS(app, origins="*") 

ADM_USUARIO = os.getenv("ADM_USUARIO")
ADM_SENHA = os.getenv("ADM_SENHA")

if os.getenv("VERCEL"):
    # ONLINE NA VERCEL
    cred = credentials.Certificate(json.loads(os.getenv("FIREBASE_CREDENTIALS")))
else:
    # LOCAL
    cred = credentials.Certificate("firebase.json")

# carregar as credenciais do firebase
firebase_admin.initialize_app(cred)

#conectar ao firestore
db = firestore.client()


#rota de boas vindas
@app.route("/", methods=['GET'])
def root():
    return jsonify({
        "api": "charadas",
        "version":"1.0",
        "Author": "Lívia"
    }),200


#=================================
#         ROTA DE LOGIN
#=================================
@app.route("/login", methods=["POST"])
def login():
    dados = request.get_json()
    if not dados:
        return jsonify({"error":"Envie os dados para login"}), 400
   
    usuario = dados.get("usuario")
    senha = dados.get("senha")

    if not usuario or not senha:
        return jsonify({"error":"Usuário e senha obrigatórios!"}), 400
   
    if usuario == ADM_USUARIO and senha == ADM_SENHA:
        token = gerar_token(usuario)
        return jsonify({"message":"Login realizado com sucesso!", "token":token}), 200
    return jsonify({"error": "Usuário ou senha inválidos!"})

# rota 01- método get- todas as charadas
@app.route("/charadas", methods=['GET'])
def get_charadas():
    charadas = [] #lista vazia
    lista = db.collection('charadas').stream() #lista todos os documentos

    for item in lista:
        charadas.append(item.to_dict()) #transforma objeto do firestore em dicionário python
    return jsonify(charadas), 200



# rota 02- metodo get- charadas aleatórias
@app.route("/charadas/aleatorias", methods=['GET'])
def get_charadas_random():
    charadas = [] #lista vazia
    lista = db.collection('charadas').stream() #lista todos os documentos

    for item in lista:
        charadas.append(item.to_dict()) #transforma objeto do firestore em dicionário python

    return jsonify(random.choice(charadas)), 200  


#rota 3- metodo get- retorna a charada pelo id
@app.route("/charadas/<int:id>", methods=['GET'])
def get_charada_by_id(id):
    lista = db.collection('charadas').where('id', '==', id).stream()

    for item in lista:
        return jsonify(item.to_dict()),200
   
    return jsonify({"error": "Charada não encontrada"}), 404

#===========================================================
#ROTAS PRIVADAS
#==========================================================

# rota 4- metodo post- criar nova charada
@app.route("/charadas", methods=['POST'])
@token_obrigatorio
def post_charadas():
   
    dados = request.get_json()

    if not dados or "pergunta" not in dados or "resposta" not in dados:
        return jsonify({"error":"Dados inválidos ou incompleto!"}), 400
    try:  
        #busca pelo contador
        contador_ref = db.collection("contador").document("controle_id")
        contador_doc = contador_ref.get()
        ultimo_id = contador_doc.to_dict().get("ultimo_id")
        #somar 1 ao ultimo id
        novo_id = ultimo_id + 1
        #atualizar o id contador
        contador_ref.update({"ultimo_id":novo_id})

        #cadastrar a nova charada
        db.collection("charadas").add({
            "id": novo_id,
            "pergunta": dados["pergunta"],
            "resposta": dados["resposta"]
        })

        return jsonify({"message": "Charada criada com sucesso!"}), 201
    except:
        return jsonify({"error": "Falha ao criar!"}), 400
   

#rota 5 - método PUT- alteração total
@app.route("/charadas/<int:id>", methods=['PUT'])
@token_obrigatorio
def charadas_put(id):
   
    dados = request.get_json()

# PUT é necessário enviar pergunta e resposta
    if not dados or "pergunta" not in dados or "resposta" not in dados:
        return jsonify({"error":"Dados inválidos ou incompleto!"}), 400
   
    try:
        docs = db.collection("charadas").where("id","==",id).limit(1).get()
        if not docs:
            return jsonify({"error:" "Charada não encontrada!"}), 404
       
        #pega o 1º e unico documento da lista
        for doc in docs:
            doc_ref = db.collection("charadas").document(doc.id)
            doc_ref.update ({
                "pergunta": dados['pergunta'],
                "resposta": dados['resposta']
            })
        return jsonify({"message": "Charada alterada com sucesso!"}), 200
    except:
        return jsonify({"error": "Falha no envio da charada!"}), 400
   

#rota 6 - método Patch- alteração total    
@app.route("/charadas/<int:id>", methods=['PATCH'])
@token_obrigatorio
def charadas_patch(id):
   
    dados = request.get_json()

# PATCH é necessário enviar pergunta e resposta
    if not dados or "pergunta" not in dados or "resposta" not in dados:
        return jsonify({"error":"Dados inválidos ou incompleto!"}), 400
   
    try:
        docs = db.collection("charadas").where("id","==",id).limit(1).get()
        if not docs:
            return jsonify({"error:" "Charada não encontrada!"}), 404
       
        doc_ref = db.collection("charadas").document(docs[0].id)
        update_charada = {}
        if "pergunta" in dados:
            update_charada["pergunta"] = dados["pergunta"]

        if "resposta" in dados:
            update_charada["resposta"] = dados["resposta"]

        #atualizar o firestore
        doc_ref.update(update_charada)

        return jsonify({"message": "Charada alterada com sucesso!"}), 200
    except:
        return jsonify({"error": "Falha no envio da charada!"}), 400


# rota 7- DELETE - excluir charada
@app.route("/charadas/<int:id>", methods=['DELETE'])
@token_obrigatorio
def delete_charada(id):
    docs = db.collection("charadas").where("id","==",id).limit(1).get()

    if not docs:
        return jsonify({"error":"Charada não encontrada!"}), 404
   
    doc_ref = db.collection("charadas").document(docs[0].id)
    doc_ref.delete()
    return jsonify({"message":"Charada excluída com sucesso!"}), 200


#rotas de tratamento de erro
@app.errorhandler(404)
def erro404(error):
    return jsonify({"error":"Rota não encontrada"}),404

@app.errorhandler(500)
def erro500(error):
    return jsonify({"error":"Servidor interno com falhas!"}),500


if __name__ == "__main__":
    app.run(debug=True)