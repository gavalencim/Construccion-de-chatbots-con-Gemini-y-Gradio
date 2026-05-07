from pypdf import PdfReader
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import gradio as gr


# FUNCION PARA EXTRAER EL PDF:
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)

    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
    
    return full_text

def no_of_pages(pdf_path):
    reader = PdfReader(pdf_path)
    pagess = 0
    caracteres = ""

    for page in reader.pages:
        caracteres += (page.extract_text())
        pagess += 1


    return [pagess, len(caracteres)]

#print(extract_text_from_pdf("attention_is_all_you_need.pdf"))


# CONFIGURACION INICIALIZACION DE API KEY
load_dotenv()

if os.getenv("GEMINI_API_KEY"):
    print("Api key cargada correctamente :D")
else:
    print("Api key no hallada :(")    

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODELO = "gemini-2.5-flash-lite"

## 1RA LLAMADA A LA API
'''response = client.models.generate_content(
    model = MODELO,
    config = types.GenerateContentConfig(
        system_instruction = "Eres un asistente util",),
    contents = "Escribe una historia de una oración sobre un unicornio"    
)'''

# print(response.text)


# FUNCION PARA SYSTEM PROMPT
SYSTEM_PROMPT = """
Eres un asistente experto exclusivamente en el contenido del documento PDF proporcionado.

Tu función es:
- Analizar el contenido del PDF.
- Responder preguntas únicamente usando la información presente en el documento.
- Explicar conceptos del PDF de forma clara, precisa y estructurada.
- Si el documento contiene información técnica, debes actuar como un experto en ese tema.

Reglas importantes:
1. NO inventes información que no esté en el PDF.
2. Si la respuesta no aparece en el documento, responde:
"No encontré esa información en el PDF proporcionado."
3. No uses conocimiento externo, aunque conozcas la respuesta.
4. Cuando sea posible, cita o resume la sección relevante del documento.
5. Mantén respuestas claras y útiles para el usuario.
6. Si el usuario hace preguntas ambiguas, pide aclaración basada en el contenido del PDF.

Tu prioridad absoluta es mantener fidelidad al contenido del documento.
"""

def build_system_prompt(document_text):
    prompt = (SYSTEM_PROMPT + "\n El documento pdf es este: \n" + document_text)
    return prompt


# FUNCION PARA HISTORIAL
def get_text(content):
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        return content[0].get("text", "") if content else ""
    return str(content)

def chat_history(message: str, history: list):
    content_history = []

    for entry in history:
        if isinstance(entry, dict):
            role = "model" if entry["role"] == "assistant" else "user"
            content_history.append(
                types.Content(
                    role = role,
                    parts = [types.Part(text = get_text(entry["content"]))]  
                )
            )
        elif isinstance(entry, (list, tuple)) and len(entry) == 2:
            user_msg, assistant_msg = entry
            content_history.append(
                types.Content(
                    role = "user",
                    parts = [types.Part(text = get_text(user_msg))]
                )
            )
            content_history.append(
                types.Content(
                    role = "model",
                    parts = [types.Part(text = get_text(assistant_msg))]
                )
            )
    
    content_history.append(
        types.Content(
            role = "user",
            parts = [types.Part(text = message)]
        )
    )

    return content_history


# FUNCION PARA EL CHAT CON EL PDF
pdf_document = extract_text_from_pdf("attention_is_all_you_need.pdf")
prompt = build_system_prompt(pdf_document)
def chat_by_pdf(message: str, history) -> str:
    conversation = chat_history(message, history)
    response = client.models.generate_content(
        model = MODELO,
        config = types.GenerateContentConfig(
            system_instruction = prompt),
            contents = conversation)
    return response.text


# INTERFAZ DE CHAT
pages = no_of_pages("attention_is_all_you_need.pdf")[0]
caracteres = no_of_pages("attention_is_all_you_need.pdf")[1]

chat_bot = gr.ChatInterface(
    fn = chat_by_pdf,
    title = "Chatbot sobre el libro: Attention is all you need ",
    description = f"Haz preguntas sobre el libro y el chat responderá, el texto tiene {pages} paginas, y {caracteres} caracteres",
    flagging_mode = "never")

chat_bot.launch(
    server_name="0.0.0.0",
    server_port=8081,
    show_error=True)
