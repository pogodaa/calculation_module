import math
from typing import List
from .models import Indicator, CalculationInput, CalculationResult
from .validators import validate_input_data, ValidationError


class MetricsCalculator:
    """Основной класс для расчёта показателей"""
    
    @staticmethod
    def calculate_arithmetic_mean(indicators: List[Indicator]) -> float:
        """
        Расчёт среднего арифметического.
        Формула: mean = (Σ values) / n
        """
        if not indicators:
            raise ValueError("Нет данных для расчёта среднего")
        values = [ind.value for ind in indicators]
        return sum(values) / len(values)
    
    @staticmethod
    def calculate_weighted_mean(indicators: List[Indicator]) -> float:
        """
        Расчёт средневзвешенного значения.
        Формула: weighted_mean = Σ(value_i * weight_i) / Σ(weight_i)
        """
        if not indicators:
            raise ValueError("Нет данных для расчёта взвешенного среднего")
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for indicator in indicators:
            weight = indicator.weight if indicator.weight is not None else 1.0
            weighted_sum += indicator.value * weight
            total_weight += weight
        
        if total_weight == 0:
            raise ValueError("Сумма весов равна нулю")
        
        return weighted_sum / total_weight
    
    @staticmethod
    def calculate_growth_rate(current: float, previous: float) -> float:
        """
        Расчёт темпа роста в процентах.
        Формула: growth_rate = ((current - previous) / previous) * 100
        """
        if previous == 0:
            raise ValueError("Предыдущее значение не может быть 0")
        return ((current - previous) / previous) * 100
    
    @staticmethod
    def calculate_efficiency_ratio(output: float, input_val: float) -> float:
        """
        Расчёт коэффициента эффективности.
        Формула: efficiency = output / input
        """
        if input_val == 0:
            raise ValueError("Входное значение не может быть 0")
        return output / input_val
    
    @staticmethod
    def calculate_standard_deviation(indicators: List[Indicator]) -> float:
        """
        Расчёт стандартного отклонения.
        Формула: σ = √(Σ(x_i - μ)² / n)
        """
        if len(indicators) < 2:
            raise ValueError("Требуется минимум 2 значения для расчёта отклонения")
        values = [ind.value for ind in indicators]
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)
    
    @staticmethod
    def calculate_median(indicators: List[Indicator]) -> float:
        """Расчёт медианы"""
        if not indicators:
            raise ValueError("Нет данных для расчёта медианы")
        values = sorted([ind.value for ind in indicators])
        n = len(values)
        return values[n // 2] if n % 2 == 1 else (values[n // 2 - 1] + values[n // 2]) / 2
    
    @staticmethod
    def calculate_variance(indicators: List[Indicator]) -> float:
        """Расчёт дисперсии"""
        if len(indicators) < 2:
            raise ValueError("Требуется минимум 2 значения для расчёта дисперсии")
        values = [ind.value for ind in indicators]
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)
    
    @staticmethod
    def calculate_range(indicators: List[Indicator]) -> dict:
        """Расчёт размаха"""
        if not indicators:
            raise ValueError("Нет данных для расчёта размаха")
        values = [ind.value for ind in indicators]
        return {
            'min': min(values),
            'max': max(values),
            'range': max(values) - min(values)
        }
    
    @staticmethod
    def calculate_all_metrics(input_data: CalculationInput) -> CalculationResult:
        """Выполнить все расчёты на основе входных данных"""
        results = {}
        errors = []
        warnings = []
        
        try:
            # Валидация входных данных
            validate_input_data(input_data)
            
            # Базовые статистические показатели
            try:
                results['mean'] = MetricsCalculator.calculate_arithmetic_mean(input_data.indicators)
            except ValueError as e:
                errors.append(f"Среднее арифметическое: {e}")
            
            try:
                results['weighted_mean'] = MetricsCalculator.calculate_weighted_mean(input_data.indicators)
            except ValueError as e:
                errors.append(f"Средневзвешенное: {e}")
            
            try:
                results['std_dev'] = MetricsCalculator.calculate_standard_deviation(input_data.indicators)
            except ValueError as e:
                warnings.append(f"Стандартное отклонение: {e}")
            
            try:
                results['median'] = MetricsCalculator.calculate_median(input_data.indicators)
            except ValueError as e:
                warnings.append(f"Медиана: {e}")
            
            try:
                results['variance'] = MetricsCalculator.calculate_variance(input_data.indicators)
            except ValueError as e:
                warnings.append(f"Дисперсия: {e}")
            
            try:
                range_vals = MetricsCalculator.calculate_range(input_data.indicators)
                results.update({
                    'min_value': range_vals['min'],
                    'max_value': range_vals['max'],
                    'value_range': range_vals['range']
                })
            except ValueError as e:
                warnings.append(f"Размах: {e}")
            
            # Расчёты на основе коэффициентов
            if 'previous_period_value' in input_data.coefficients:
                try:
                    current_mean = results.get('mean')
                    if current_mean is not None:
                        previous = input_data.coefficients['previous_period_value']
                        results['growth_rate'] = MetricsCalculator.calculate_growth_rate(
                            current_mean, previous
                        )
                except ValueError as e:
                    errors.append(f"Темп роста: {e}")
            
            if ('output_value' in input_data.coefficients and 
                'input_value' in input_data.coefficients):
                try:
                    output = input_data.coefficients['output_value']
                    input_val = input_data.coefficients['input_value']
                    results['efficiency_ratio'] = MetricsCalculator.calculate_efficiency_ratio(
                        output, input_val
                    )
                except ValueError as e:
                    errors.append(f"Коэффициент эффективности: {e}")
            
            # Дополнительные агрегаты
            if input_data.indicators:
                values = [ind.value for ind in input_data.indicators]
                results['sum'] = sum(values)
                results['count'] = len(values)
                if results.get('sum', 0) != 0:
                    results['avg_contribution'] = 100.0 / len(values)
            
            success = len(errors) == 0
            return CalculationResult(
                success=success,
                data=results,
                errors=errors,
                warnings=warnings
            )
            
        except ValidationError as e:
            return CalculationResult(
                success=False,
                data={},
                errors=[f"Ошибка валидации: {str(e)}"]
            )
        except Exception as e:
            return CalculationResult(
                success=False,
                data={},
                errors=[f"Системная ошибка: {str(e)}"]
            )