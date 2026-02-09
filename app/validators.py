from typing import List
from .models import Indicator, CalculationInput


class ValidationError(Exception):
    """Ошибка валидации данных"""
    pass


class ZeroDivisionError(Exception):
    """Ошибка деления на ноль"""
    pass


def validate_indicator(indicator: Indicator) -> List[str]:
    """Валидация одного показателя"""
    errors = []
    
    if not indicator.id or not isinstance(indicator.id, str):
        errors.append(f"Некорректный идентификатор: {indicator.id}")
    
    if not isinstance(indicator.value, (int, float)):
        errors.append(f"Некорректное значение для {indicator.id}: {indicator.value}")
    
    if indicator.weight is not None and indicator.weight < 0:
        errors.append(f"Вес {indicator.id} не может быть отрицательным")
    
    return errors


def validate_input_data(data: CalculationInput) -> None:
    """Валидация всех входных данных"""
    if not data.indicators:
        raise ValidationError("Список показателей пуст")
    
    all_errors = []
    
    # Валидация каждого показателя
    for indicator in data.indicators:
        errors = validate_indicator(indicator)
        all_errors.extend(errors)
    
    # Проверка уникальности идентификаторов
    ids = [ind.id for ind in data.indicators]
    if len(ids) != len(set(ids)):
        all_errors.append("Идентификаторы показателей должны быть уникальными")
    
    # Проверка коэффициентов
    for key, value in data.coefficients.items():
        if not isinstance(value, (int, float)):
            all_errors.append(f"Коэффициент {key} должен быть числом")
    
    if all_errors:
        raise ValidationError("\n".join(all_errors))