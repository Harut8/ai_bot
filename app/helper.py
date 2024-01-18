import numpy as np
from openai import OpenAI
from sqlalchemy import text, select
from app.db import DbHelper
from app.models import Embedding
from app.settings import settings

client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
)


async def add_content_to_db(content):
    session = await DbHelper.create_session_object()
    async with session() as session:
        embedding = Embedding(text=content, embedding=get_embeddings(content))
        session.add(embedding)
        await session.commit()


async def get_top3_similar_docs(query_embedding):
    embedding_array = np.array(query_embedding)
    session = await DbHelper.create_session_object()
    async with session() as session:
        res = await session.scalars(
            select(Embedding)
            .order_by(Embedding.embedding
            .l2_distance(embedding_array)).limit(3))
        top3_doc = res.all()
    return top3_doc


def get_completion_from_messages(messages, model="gpt-4-1106-preview", temperature=0, max_tokens=1000):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


def get_embeddings(text, model="text-embedding-ada-002"):
    embedding = client.embeddings.create(input=[text], model=model).data[0].embedding
    return embedding


async def process_input_with_retrieval(user_input):
    delimiter = "```"
    related_docs = await get_top3_similar_docs(get_embeddings(user_input))
    system_message = f"""
    You are a friendly chatbot. \
    You can answer questions, its features and its use cases. \
    You respond in a concise, technically credible tone. \
    REMEMBER: IF YOU DON'T HAVE KNOWLEDGE ABOUT QUESTION TOPIC, THEN ANSWER:
    'I DONT KNOW ABOUT THAT'
    IT'S IMPORTANT: IN CASE OF USER MESSAGE SEEMS THAT USER WANT TO EXIT, CLOSE CONVERSATION
    IF THAT ENDS THE CONVERSATION THAN ANSWER ONLY:
    'exit'
    """
    docs = [
        doc.text for doc in related_docs
    ]
    txt = delimiter.join(docs)
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"{delimiter}{user_input}{delimiter}"},
        {"role": "assistant",
         "content": f"Relevant 'ImeaSystems' case studies information: {txt}"}
    ]

    final_response = get_completion_from_messages(messages)
    return final_response
