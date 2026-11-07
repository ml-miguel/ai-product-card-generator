from fastapi import FastAPI, HTTPException
from schemas import ProductInput, ProductOutput
from llm_service import generate_product_card

app = FastAPI(
    title="AI-помощник для карточек товаров",
    description="Прототип сервиса для генерации контента B2B-магазина"
)

@app.post("/generate_card", response_model=ProductOutput, summary="Сгенерировать карточку товара")
async def generate_card(product: ProductInput):
    """
    Принимает данные о приборе и возвращает черновик карточки товара.
    """
    try:
        # Вызываем наш сервис (он синхронный, но FastAPI справится)
        result = generate_product_card(product)
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")