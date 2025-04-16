from flask import Flask, request, jsonify
import nltk
from nltk.tokenize import word_tokenize


nltk.download('punkt_tab')


app = Flask(__name__)


# Tópicos e respostas focados no tijolo ecológico
topicos_permitidos = ["tijolo", "ecológico", "produto", "sim", "comprar", "compra"]


respostas = {
    "tijolo": "Nosso tijolo ecológico é feito com resíduos de açaí e fibra de aninga. É resistente, sustentável e acessível!",
    "ecológico": "O tijolo ecológico é uma opção sustentável para construção civil, utilizando materiais naturais e renováveis.",
    "produto": "Estamos oferecendo o tijolo ecológico feito com açaí e fibra de aninga. Você gostaria de adquirir?",
    "sim": "Ótimo! Clique no botão abaixo para fazer seu pedido agora mesmo.",
    "comprar": "Ótimo! Clique no botão abaixo para fazer seu pedido agora mesmo.",
    "compra": "Você pode clicar no botão 'Adquirir Produto' para garantir seu tijolo ecológico!"
}


def verificar_contexto(pergunta):
    tokens = word_tokenize(pergunta.lower())
    for token in tokens:
        if token in topicos_permitidos:
            return token
    return None


@app.route("/")
def index():
    html = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
      <title>Chatbot Tijolo Ecológico</title>
      <style>
        body { font-family: Arial, sans-serif; }
        #chatbot-container {
          display: none;
          position: fixed;
          bottom: 80px;
          right: 20px;
          width: 300px;
          border: 1px solid #ccc;
          border-radius: 10px;
          padding: 10px;
          background-color: #f9f9f9;
          box-shadow: 0 0 10px rgba(0,0,0,0.2);
        }
        #mensagens {
          height: 200px;
          overflow-y: auto;
          margin-bottom: 10px;
        }
        #mensagens div {
          margin: 5px 0;
        }
        #chatbot-button {
          position: fixed;
          bottom: 20px;
          right: 20px;
          padding: 15px;
          border-radius: 50%;
          background-color: #4CAF50;
          color: white;
          font-size: 18px;
          border: none;
          cursor: pointer;
        }
      </style>
    </head>
    <body>
      <button id="chatbot-button">💬</button>


      <div id="chatbot-container">
        <div id="mensagens"></div>
        <input type="text" id="entrada" placeholder="Pergunte sobre o nosso tijolo ecológico..." />
        <button onclick="enviarMensagem()">Enviar</button>
        <div id="botao-compra" style="margin-top: 10px; display: none;">
          <a href="https://wa.me/5598999999999?text=Tenho%20interesse%20no%20tijolo%20ecol%C3%B3gico!" target="_blank">
            <button style="width: 100%; padding: 10px; background-color: #4CAF50; color: white; border: none; border-radius: 5px;">Adquirir Produto</button>
          </a>
        </div>
      </div>


      <script>
        const botao = document.getElementById("chatbot-button");
        const container = document.getElementById("chatbot-container");


        botao.addEventListener("click", () => {
          container.style.display = container.style.display === "none" ? "block" : "none";
        });


        async function enviarMensagem() {
          const entrada = document.getElementById("entrada");
          const mensagens = document.getElementById("mensagens");
          const botaoCompra = document.getElementById("botao-compra");


          const pergunta = entrada.value;
          if (!pergunta) return;


          mensagens.innerHTML += `<div><strong>Você:</strong> ${pergunta}</div>`;
          entrada.value = "";


          const resposta = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mensagem: pergunta })
          }).then(res => res.json());


          mensagens.innerHTML += `<div><strong>Bot:</strong> ${resposta.resposta}</div>`;
          mensagens.scrollTop = mensagens.scrollHeight;


          if (resposta.resposta.toLowerCase().includes("clique no botão")) {
            botaoCompra.style.display = "block";
          } else {
            botaoCompra.style.display = "none";
          }
        }
      </script>
    </body>
    </html>
    """
    return html


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    mensagem = data.get("mensagem", "")
    topico = verificar_contexto(mensagem)
    if topico:
        resposta = respostas[topico]
    else:
        resposta = "Desculpe, só posso responder perguntas sobre nosso produto: o tijolo ecológico feito com açaí e fibra de aninga."
    return jsonify({"resposta": resposta})


if __name__ == "__main__":
    app.run(debug=True)


