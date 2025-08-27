import os
import json  # Importe a biblioteca 'json' para lidar com o JSON
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

# Carrega a chave da API do arquivo .env
load_dotenv()

# Inicializa o Flask
app = Flask(__name__)

# Configura a chave da API da Google Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("A chave da API da Google Gemini não foi encontrada. Verifique o arquivo .env.")
genai.configure(api_key=api_key)

def classificar_e_responder_email(texto_email):
    """
    Função que usa a API da Google Gemini para classificar e gerar uma resposta para um email.
    """
    # Usamos o modelo Gemini 1.5 Pro por sua capacidade de processar JSON
    model = genai.GenerativeModel('gemini-1.5-pro-latest')

    # O prompt é o mesmo, a única diferença é que pedimos para o modelo retornar APENAS o JSON
    prompt = f"""
    Você é um assistente de IA especializado em analisar e responder emails. Sua tarefa é ler o email abaixo, classificá-lo em uma das duas categorias (Produtivo ou Improdutivo) e, em seguida, sugerir uma resposta automática adequada.

    A categoria "Produtivo" refere-se a emails que contêm solicitações, perguntas ou informações importantes relacionadas a negócios, projetos ou tarefas que exigem uma ação ou acompanhamento.
    A categoria "Improdutivo" refere-se a emails que não exigem uma ação ou acompanhamento, como mensagens de feliz feriado, mensagens de "ok, obrigado" ou e-mails de notificação geral sem solicitação explícita.

    Email para análise:
    "{texto_email}"

    Siga estas instruções rigorosamente para a sua resposta:
    1. A sua resposta deve ser um objeto JSON válido.
    2. O objeto JSON deve ter duas chaves: "categoria" e "resposta_sugerida".
    3. A chave "categoria" deve conter apenas uma das duas palavras: "Produtivo" ou "Improdutivo".
    4. A chave "resposta_sugerida" deve conter o texto da resposta que você criou.

    Exemplo de formato da sua resposta JSON:
    {{
      "categoria": "Produtivo",
      "resposta_sugerida": "Olá, sua solicitação foi recebida e será processada em breve. Obrigado pelo contato."
    }}
    """
    
    try:
        # A chamada à API da Google é diferente da da OpenAI
        response = model.generate_content(
            prompt,
            # A instrução de retorno em JSON é enviada aqui, em vez de no prompt
            generation_config={"response_mime_type": "application/json"}
        )
        
        # O resultado é um objeto, então acessamos o texto do conteúdo
        response_json_string = response.text
        
        # Convertemos a string JSON em um objeto Python e retornamos
        return jsonify(json.loads(response_json_string))
        
    except Exception as e:
        print(f"Erro ao chamar a API da Google Gemini: {e}")
        return jsonify({
            "categoria": "Erro",
            "resposta_sugerida": "Não foi possível processar o email. Por favor, tente novamente."
        })

# As rotas Flask permanecem as mesmas
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def processar_email():
    data = request.get_json()
    texto_email = data.get('email_text')
    
    if not texto_email:
        return jsonify({"error": "Nenhum texto de email foi fornecido."}), 400

    response_from_ai = classificar_e_responder_email(texto_email)
    
    return response_from_ai

if __name__ == '__main__':
    app.run(debug=True)