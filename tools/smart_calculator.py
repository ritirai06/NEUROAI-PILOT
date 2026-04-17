"""
Smart Calculator - Simple math evaluation with safety checks.
"""
import re
import math
import operator
from typing import Union


def calculate(expression: str) -> str:
    """
    Safely evaluate mathematical expressions.
    
    Args:
        expression: Mathematical expression as string
        
    Returns:
        Result as string
    """
    try:
        # Clean the expression
        expr = expression.strip().lower()
        
        # Remove common prefixes
        prefixes = ['calculate', 'compute', 'what is', "what's", 'solve', 'find']
        for prefix in prefixes:
            if expr.startswith(prefix):
                expr = expr[len(prefix):].strip()
        
        # Replace word operators
        replacements = {
            ' plus ': ' + ',
            ' add ': ' + ',
            ' and ': ' + ',
            ' minus ': ' - ',
            ' subtract ': ' - ',
            ' times ': ' * ',
            ' multiply ': ' * ',
            ' multiplied by ': ' * ',
            ' x ': ' * ',
            ' divide ': ' / ',
            ' divided by ': ' / ',
            ' over ': ' / ',
            ' percent ': ' % ',
            ' mod ': ' % ',
            ' modulo ': ' % ',
        }
        
        for word, symbol in replacements.items():
            expr = expr.replace(word, symbol)
        
        # Clean up extra spaces
        expr = re.sub(r'\s+', ' ', expr).strip()
        
        # Safety check - only allow numbers, operators, parentheses, and spaces
        if not re.match(r'^[0-9+\-*/().\s%]+$', expr):
            return f"❌ Invalid characters in expression: {expression}"
        
        # Evaluate safely
        result = eval(expr, {"__builtins__": {}}, {})
        
        # Format result
        if isinstance(result, float):
            if result.is_integer():
                result = int(result)
            else:
                result = round(result, 6)
        
        return f"Calculate: {expression} = {result}"
        
    except ZeroDivisionError:
        return f"❌ Division by zero in: {expression}"
    except SyntaxError:
        return f"❌ Invalid syntax in: {expression}"
    except Exception as e:
        return f"❌ Error calculating '{expression}': {str(e)}"


def smart_calculate(expression: str) -> str:
    """Alias for calculate function."""
    return calculate(expression)


# Advanced calculator functions
def factorial(n: int) -> int:
    """Calculate factorial of n."""
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    if n > 20:
        raise ValueError("Factorial too large (max 20)")
    return math.factorial(n)


def power(base: float, exponent: float) -> float:
    """Calculate base^exponent."""
    return base ** exponent


def sqrt(n: float) -> float:
    """Calculate square root."""
    if n < 0:
        raise ValueError("Square root of negative number")
    return math.sqrt(n)


def percentage(value: float, percent: float) -> float:
    """Calculate percentage of value."""
    return (value * percent) / 100


# Test function
if __name__ == "__main__":
    test_cases = [
        "5 + 6 + 2 + 3 + 2 + 1",
        "10 times 5",
        "100 divided by 4",
        "calculate 25 minus 7",
        "what is 3.5 times 2",
        "50 percent of 200",
    ]
    
    for test in test_cases:
        result = calculate(test)
        print(f"{test} → {result}")