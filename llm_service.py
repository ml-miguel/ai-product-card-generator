import os
import json
import re
from langchain_gigachat import GigaChat
from schemas import ProductInput, ProductOutput
from dotenv import load_dotenv

load_dotenv()

# Инициализация клиента GigaChat
llm = GigaChat(
    credentials=os.getenv("GIGACHAT_CREDENTIALS"),
    scope="GIGACHAT_API_PERS",
    verify_ssl_certs=False,
    model="GigaChat-2-Max",
    timeout=120
)

# Функция для вытаскивания чистого JSON из ответа LLM (на случай markdown-разметки)
def extract_json(text: str) -> dict:
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    raise ValueError("LLM вернула невалидный JSON")

def generate_product_card(product: ProductInput) -> ProductOutput:
    # Формируем контекст. Если описания нет, явно указываем это.
    input_data = {
        "name": product.name,
        "manufacturer": product.manufacturer,
        "specs": product.specs,
        "description": product.description if product.description else "данных нет"
    }
    
    system_prompt = """Ты — профессиональный контент-менеджер B2B-магазина измерительных приборов. 
Твоя задача: создать черновик карточки товара на основе предоставленного JSON.

ЖЕСТКИЕ ПРАВИЛА:
1. Используй ТОЛЬКО те технические характеристики, которые переданы во входном JSON. КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО выдумывать или добавлять характеристики, которых нет во входных данных.
2. Если каких-то данных не хватает (например, нет описания), пиши «данных нет».
3. Верни ответ СТРОГО в формате валидного JSON (без markdown-разметки ```json), с ключами:
   - "seo_title": строка (SEO-заголовок до 70 символов, включая название и производителя)
   - "seo_description": строка (РАЗВЕРНУТОЕ SEO-описание строго от 800 до 1200 символов! Обязательно используй 3-4 абзаца: начни с общего назначения прибора, затем подробно опиши его технические преимущества на основе specs, а в конце опиши сферы применения. Не пиши слишком коротко.)
   - "key_specs": объект (словарь с ключевыми характеристиками, строго из входных данных)
   - "search_queries": массив строк (3-5 поисковых запросов, по которым товар будут искать)
   - "commercial_block": строка (краткий блок для менеджера: кому подходит и какие задачи решает)

Входные данные о товаре:
"""

    user_prompt = json.dumps(input_data, ensure_ascii=False)
    
    try:
        response = llm.invoke(system_prompt + user_prompt)
        parsed_data = extract_json(response.content)
        
        # Валидируем ответ через Pydantic (если LLM что-то пропустит — упадем с ошибкой)
        return ProductOutput(**parsed_data)
        
    except Exception as e:
        # Пробрасываем ошибку выше, чтобы FastAPI вернул 500
        raise RuntimeError(f"Ошибка генерации карточки: {str(e)}")
