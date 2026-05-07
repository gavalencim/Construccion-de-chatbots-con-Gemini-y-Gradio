# Chatbot PDF con Gemini y Gradio

## Introducción

En este trabajo se desarrolló un chatbot capaz de responder preguntas sobre un documento PDF utilizando Gemini como modelo de lenguaje y Gradio como interfaz web.

El sistema realiza las siguientes tareas:

- Extrae el texto completo de un documento PDF.
- Construye un *system prompt* especializado para que el modelo actúe como experto en el contenido del documento.
- Mantiene el historial conversacional utilizando el formato requerido por Gemini (`types.Content`).
- Permite realizar preguntas sobre el documento desde una interfaz web interactiva.
- Restringe las respuestas al contenido del PDF proporcionado.

El documento utilizado para las pruebas fue el paper **"Attention Is All You Need"**, relacionado con la arquitectura Transformer.

---

# Reflexión sobre la implementación

## ¿Cuál es la limitación principal de este enfoque? ¿Qué pasaría con un documento de 1000 páginas?

La principal limitación de este enfoque es que el documento completo se envía al modelo en cada consulta dentro del *system prompt*. Esto funciona con documentos pequeños o medianos, pero no escala correctamente para documentos muy grandes.

Con un documento de 1000 páginas aparecerían varios problemas:

- El texto podría superar el límite de tokens permitido por el modelo.
- Las respuestas serían mucho más lentas.
- El costo computacional aumentaría significativamente.
- El modelo tendría demasiada información en contexto, lo que podría disminuir la precisión de las respuestas.
- Cada nueva pregunta volvería a enviar el documento completo, generando redundancia e ineficiencia.

Por estas razones, este enfoque es útil como prototipo o solución inicial, pero no es adecuado para aplicaciones de gran escala.

---

## ¿Por qué existe RAG? ¿Cómo resolvería RAG el problema identificado?

RAG (*Retrieval-Augmented Generation*) existe para resolver el problema de enviar documentos completos al modelo.

En lugar de proporcionar todo el documento en cada consulta, RAG:

1. Divide el documento en fragmentos pequeños (*chunks*).
2. Genera embeddings para cada fragmento.
3. Almacena los embeddings en una base vectorial.
4. Cuando el usuario hace una pregunta, se buscan únicamente los fragmentos más relevantes.
5. Solo esos fragmentos relevantes se envían al modelo junto con la pregunta.

Esto permite:

- Trabajar con documentos muy grandes.
- Reducir el consumo de tokens.
- Mejorar la velocidad de respuesta.
- Disminuir costos.
- Aumentar la precisión al enviar únicamente contexto relevante.

Por esta razón, RAG es actualmente una de las arquitecturas más utilizadas para asistentes documentales y chatbots empresariales.

---

## ¿Qué información podría filtrarse aunque el system prompt diga que no?

Aunque el *system prompt* indique que el modelo solo debe responder usando el documento, el modelo ya posee conocimiento previo adquirido durante su entrenamiento.

Por ejemplo:

- Gemini probablemente ya conoce el paper *Attention Is All You Need*.
- Puede conocer explicaciones externas, resúmenes o análisis del documento.
- Puede completar información usando conocimiento aprendido previamente, incluso si esa información no aparece explícitamente en el PDF.

Esto significa que el modelo podría responder correctamente utilizando información externa y no necesariamente el contenido del documento proporcionado.

---

## ¿Cómo verificar que el modelo responde desde el documento y no desde su entrenamiento?

Existen varias estrategias para verificarlo:

- Solicitar citas textuales del documento.
- Verificar manualmente si la información realmente aparece en el PDF.
- Realizar preguntas sobre información externa que no esté presente en el documento.
- Utilizar RAG para enviar únicamente fragmentos específicos recuperados del documento.
- Incluir instrucciones estrictas como:

```text
"Si la información no aparece explícitamente en el documento, responde que no está disponible."
