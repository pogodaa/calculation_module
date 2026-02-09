"""
Тесты для модуля расчёта показателей
"""
import pytest
from app.calculator import MetricsCalculator
from app.models import Indicator, CalculationInput
from app.validators import ValidationError


def test_arithmetic_mean():
    """Тест расчёта среднего арифметического"""
    indicators = [
        Indicator(id="test1", value=10.0),
        Indicator(id="test2", value=20.0),
        Indicator(id="test3", value=30.0)
    ]
    result = MetricsCalculator.calculate_arithmetic_mean(indicators)
    assert result == 20.0


def test_weighted_mean():
    """Тест расчёта средневзвешенного значения"""
    indicators = [
        Indicator(id="test1", value=10.0, weight=1.0),
        Indicator(id="test2", value=20.0, weight=2.0),
        Indicator(id="test3", value=30.0, weight=3.0)
    ]
    result = MetricsCalculator.calculate_weighted_mean(indicators)
    expected = (10*1 + 20*2 + 30*3) / (1+2+3)
    assert abs(result - expected) < 0.001


def test_growth_rate():
    """Тест расчёта темпа роста"""
    result = MetricsCalculator.calculate_growth_rate(150.0, 100.0)
    assert result == 50.0


def test_zero_division_growth():
    """Тест обработки деления на ноль в темпе роста"""
    from app.validators import ZeroDivisionError
    with pytest.raises(ZeroDivisionError):
        MetricsCalculator.calculate_growth_rate(100.0, 0.0)


def test_efficiency_ratio():
    """Тест расчёта коэффициента эффективности"""
    result = MetricsCalculator.calculate_efficiency_ratio(540000.0, 180000.0)
    assert result == 3.0


def test_full_calculation():
    """Тест полного расчёта всех показателей"""
    indicators = [
        Indicator(id="i1", value=100.0, weight=1.0),
        Indicator(id="i2", value=200.0, weight=2.0),
        Indicator(id="i3", value=150.0, weight=1.5)
    ]
    input_data = CalculationInput(
        indicators=indicators,
        coefficients={
            'previous_period_value': 120.0,
            'output_value': 450.0,
            'input_value': 150.0
        }
    )
    result = MetricsCalculator.calculate_all_metrics(input_data)
    assert result.success == True
    assert 'Среднее арифметическое' in result.data
    assert 'Темп роста, %' in result.data
    assert 'Коэффициент эффективности' in result.data


def test_validation_error():
    """Тест валидации некорректных данных"""
    # Пустой список показателей
    input_data = CalculationInput(indicators=[])
    result = MetricsCalculator.calculate_all_metrics(input_data)
    assert result.success == False
    assert len(result.errors) > 0


def test_median_calculation():
    """Тест расчёта медианы"""
    # Нечётное количество
    indicators1 = [
        Indicator(id="a", value=10.0),
        Indicator(id="b", value=20.0),
        Indicator(id="c", value=30.0)
    ]
    result1 = MetricsCalculator.calculate_median(indicators1)
    assert result1 == 20.0
    
    # Чётное количество
    indicators2 = [
        Indicator(id="a", value=10.0),
        Indicator(id="b", value=20.0),
        Indicator(id="c", value=30.0),
        Indicator(id="d", value=40.0)
    ]
    result2 = MetricsCalculator.calculate_median(indicators2)
    assert result2 == 25.0


def test_standard_deviation():
    """Тест расчёта стандартного отклонения"""
    indicators = [
        Indicator(id="a", value=10.0),
        Indicator(id="b", value=20.0),
        Indicator(id="c", value=30.0)
    ]
    result = MetricsCalculator.calculate_standard_deviation(indicators)
    # Среднее = 20, дисперсия = ((10-20)² + (20-20)² + (30-20)²) / 3 = 200/3
    # Стандартное отклонение = √(200/3) ≈ 8.165
    assert abs(result - 8.1649658) < 0.001