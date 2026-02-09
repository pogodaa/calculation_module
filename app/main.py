

# cd calculation_module
# uvicorn app.main:app --reload --port 8000


from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
import csv
import io
from datetime import datetime

from app.models import Indicator, CalculationInput, CalculationResult
from app.calculator import MetricsCalculator

app = FastAPI(
    title="Модуль расчёта показателей",
    description="Учебный модуль для расчёта статистических показателей (ПМ.01)",
    version="1.0.0"
)

# Подключение шаблонов и статики
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# Модели для API
class IndicatorRequest(BaseModel):
    id: str
    value: float
    weight: Optional[float] = 1.0
    unit: Optional[str] = ""


class CalculationRequest(BaseModel):
    indicators: List[IndicatorRequest]
    coefficients: Optional[Dict[str, float]] = {}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Главная страница"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """Страница о проекте"""
    return templates.TemplateResponse("about.html", {"request": request})


@app.post("/calculate", response_class=HTMLResponse)
async def calculate(
    request: Request,
    indicators_json: str = Form(...),
    previous_value: Optional[float] = Form(None),
    output_value: Optional[float] = Form(None),
    input_value: Optional[float] = Form(None)
):
    """Выполнение расчётов и отображение результатов"""
    try:
        # Парсинг данных
        indicators_data = json.loads(indicators_json)
        
        # Создание показателей
        indicators = [
            Indicator(
                id=item['id'],
                value=float(item['value']),
                weight=float(item.get('weight', 1.0)),
                unit=item.get('unit', '')
            )
            for item in indicators_data
        ]
        
        # Формирование коэффициентов
        coefficients = {}
        if previous_value is not None:
            coefficients['previous_period_value'] = previous_value
        if output_value is not None:
            coefficients['output_value'] = output_value
        if input_value is not None:
            coefficients['input_value'] = input_value
        
        # Создание входных данных
        input_data = CalculationInput(
            indicators=indicators,
            coefficients=coefficients
        )
        
        # Выполнение расчётов
        result = MetricsCalculator.calculate_all_metrics(input_data)
        
        # Форматирование результатов для отображения
        formatted_results = {}
        for key, value in result.data.items():
            if key == 'count':
                formatted_results[key] = int(value)
            elif isinstance(value, float):
                formatted_results[key] = round(value, 4)
            else:
                formatted_results[key] = value
        
        # Возврат страницы с результатами
        return templates.TemplateResponse("results.html", {
            "request": request,
            "result": result,
            "formatted_results": formatted_results,
            "indicators": indicators,
            "coefficients": coefficients
        })
        
    except Exception as e:
        return templates.TemplateResponse("results.html", {
            "request": request,
            "result": CalculationResult(
                success=False,
                data={},
                errors=[f"Ошибка расчёта: {str(e)}"]
            ),
            "formatted_results": {},
            "indicators": [],
            "coefficients": {}
        })


@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """Загрузка файла с данными"""
    try:
        content = await file.read()
        
        if file.filename.endswith('.json'):
            data = json.loads(content.decode('utf-8'))
            indicators = data.get('indicators', [])
            
        elif file.filename.endswith('.csv'):
            content_str = content.decode('utf-8')
            reader = csv.DictReader(io.StringIO(content_str))
            indicators = []
            
            for row in reader:
                indicators.append({
                    'id': row.get('id', ''),
                    'value': float(row.get('value', 0)),
                    'weight': float(row.get('weight', 1.0)),
                    'unit': row.get('unit', '')
                })
        
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Поддерживаются только JSON и CSV файлы"}
            )
        
        return {
            "success": True,
            "indicators": indicators,
            "filename": file.filename
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": f"Ошибка обработки файла: {str(e)}"}
        )


@app.get("/api/health")
async def health_check():
    """Проверка работоспособности"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.post("/api/calculate")
async def api_calculate(request: CalculationRequest):
    """API для расчёта показателей"""
    try:
        # Преобразование в доменные модели
        indicators = [
            Indicator(
                id=ind.id,
                value=ind.value,
                weight=ind.weight,
                unit=ind.unit
            )
            for ind in request.indicators
        ]
        
        input_data = CalculationInput(
            indicators=indicators,
            coefficients=request.coefficients or {}
        )
        
        # Выполнение расчётов
        result = MetricsCalculator.calculate_all_metrics(input_data)
        
        return {
            "success": result.success,
            "data": result.data,
            "errors": result.errors,
            "warnings": result.warnings,
            "timestamp": result.timestamp
        }
        
    except Exception as e:
        return {
            "success": False,
            "data": {},
            "errors": [f"Ошибка расчёта: {str(e)}"],
            "warnings": [],
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)