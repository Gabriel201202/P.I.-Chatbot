# from flask import Flask, request, render_template, jsonify
# from haystack.document_stores import InMemoryDocumentStore
# from haystack.nodes import EmbeddingRetriever, FARMReader
# from haystack.pipelines import ExtractiveQAPipeline

# # Setup básico do Flask
# app = Flask(__name__)

# # Carrega o conteúdo
# with open("oketa.txt", "r", encoding="utf-8") as f:
#     texto_base = f.read()

# # Inicializa a base de conhecimento
# document_store = InMemoryDocumentStore(embedding_dim=384)
# document_store.write_documents([{"content": texto_base, "meta": {"name": "oketa"}}])

# retriever = EmbeddingRetriever(
#     document_store=document_store,
#     embedding_model="sentence-transformers/all-MiniLM-L6-v2"
# )

# document_store.update_embeddings(retriever)

# reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=False)

# pipeline = ExtractiveQAPipeline(reader, retriever)
# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/chat", methods=["POST"])
# def chat():
#     data = request.get_json()
#     pergunta = data.get("mensagem", "")
#     resposta = pipeline.run(query=pergunta, params={"Retriever": {"top_k": 3}, "Reader": {"top_k": 2}})

#     resposta_texto = resposta["answers"][0].answer
#     return jsonify({"resposta": resposta_texto})
  
# if __name__ == "__main__":
#     app.run(debug=True)

"""
from flask import Flask, request, render_template, jsonify
from sentence_transformers import SentenceTransformer, util
import torch

app = Flask(__name__)

# Carrega o modelo de IA leve
modelo = SentenceTransformer("all-MiniLM-L6-v2")

# Lê o FAQ estruturado
faq = []
with open("oketa_faq.txt", "r", encoding="utf-8") as f:
    bloco = f.read().split("\n\n")
    for item in bloco:
        if "Pergunta:" in item and "Resposta:" in item:
            pergunta = item.split("Pergunta:")[1].split("Resposta:")[0].strip()
            resposta = item.split("Resposta:")[1].strip()
            faq.append({"pergunta": pergunta, "resposta": resposta})

# Pré-processa todas as perguntas do FAQ
perguntas_faq = [item["pergunta"] for item in faq]
embeddings_faq = modelo.encode(perguntas_faq, convert_to_tensor=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    pergunta_usuario = data.get("mensagem", "")
    embedding_pergunta = modelo.encode(pergunta_usuario, convert_to_tensor=True)

    # Compara a pergunta do usuário com todas do FAQ
    similaridades = util.cos_sim(embedding_pergunta, embeddings_faq)
    indice_mais_proximo = torch.argmax(similaridades).item()

    resposta = faq[indice_mais_proximo]["resposta"]
    return jsonify({"resposta": resposta})

if __name__ == "__main__":
    app.run(debug=True)
"""

from flask import Flask, request, render_template, jsonify, session
from sentence_transformers import SentenceTransformer, util
import torch

app = Flask(__name__)
app.secret_key = 'chave-secreta'

modelo = SentenceTransformer("all-MiniLM-L6-v2")

faq = []
with open("oketa_faq.txt", "r", encoding="utf-8") as f:
    bloco = f.read().split("\n\n")
    for item in bloco:
        if "Pergunta:" in item and "Resposta:" in item:
            pergunta = item.split("Pergunta:")[1].split("Resposta:")[0].strip()
            resposta = item.split("Resposta:")[1].strip()
            faq.append({"pergunta": pergunta, "resposta": resposta})

perguntas_faq = [item["pergunta"] for item in faq]
embeddings_faq = modelo.encode(perguntas_faq, convert_to_tensor=True)

@app.route("/")
def index():
    session.clear()
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    pergunta_usuario = data.get("mensagem", "").strip().lower()

    if "historico" not in session:
        session["historico"] = []

    # Encerramento manual
    if pergunta_usuario in ["não", "nao", "não obrigado", "nao obrigado"]:
        resposta = "Tudo bem! Se quiser conversar mais sobre o projeto Oketá, estarei por aqui. 🌱"
        session["fim_conversa"] = True
        session["historico"].append({"pergunta": pergunta_usuario, "resposta": resposta})
        return jsonify({"resposta": resposta})

    # Continuação com "sim"
    if pergunta_usuario in ["sim", "claro", "pode ser", "sim por favor"]:
        if "ultimo_indice" in session:
            proximo_indice = session["ultimo_indice"] + 1
        else:
            proximo_indice = -1

        if proximo_indice == -1:
            resposta = "Desculpe, não consegui entender sua pergunta. Poderia reformular?"
        elif proximo_indice < len(faq):
            resposta = faq[proximo_indice]["resposta"]
            session["ultimo_indice"] = proximo_indice
        else:
            resposta = "Muito obrigado por consultar o projeto Oketá! 🌱 Ficamos felizes em ajudar. Até a próxima!"
            session["fim_conversa"] = True

    else:
        # Resposta baseada em similaridade
        embedding_pergunta = modelo.encode(pergunta_usuario, convert_to_tensor=True)
        similaridades = util.cos_sim(embedding_pergunta, embeddings_faq)
        max_similaridade, indice_mais_proximo = torch.max(similaridades, dim=1)

        if max_similaridade.item() < 0.5:
            resposta = "Desculpe, só posso responder perguntas relacionadas ao projeto Oketá. 🌱"
        else:
            resposta = faq[indice_mais_proximo]["resposta"]
            session["ultimo_indice"] = indice_mais_proximo.item()

    session["historico"].append({"pergunta": pergunta_usuario, "resposta": resposta})
    return jsonify({"resposta": resposta})

if __name__ == "__main__":
    app.run(debug=True)