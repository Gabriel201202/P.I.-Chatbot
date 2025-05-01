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
