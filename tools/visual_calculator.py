"""
Visual Step-by-Step Calculator System
Shows every input on screen with real button presses - NO instant computation.
"""
import time
import re
import pyautogui
from typing import List, Tuple
from tools.window_manager import WindowManager, launch_visible


class VisualCalculator:
    """Calculator that shows every step visually on screen."""
    
    # Operator mappings
    OPERATORS = {
        'plus': '+',
        'add': '+',
        'and': '+',
        'minus': '-',
        'subtract': '-',
        'take away': '-',
        'times': '*',
        'multiply': '*',
        'multiplied by': '*',
        'x': '*',
        'divide': '/',
        'divided by': '/',
        'over': '/',
        'percent': '%',
        'mod': '%',
        'modulo': '%',
    }
    
    # Key mappings for calculator
    KEY_MAP = {
        '0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
        '5': '5', '6': '6', '7': '7', '8': '8', '9': '9',
        '+': '+', '-': '-', '*': '*', '/': '/',
        '.': '.', '=': 'enter', '%': '%',
        '(': '(', ')': ')',
    }
    
    def __init__(self, step_delay: float = 0.3):
        """
        Initialize visual calculator.
        
        Args:
            step_delay: Delay between each key press (seconds)
        """
        self.step_delay = step_delay
        self.hwnd = None
    
    def parse_expression(self, text: str) -> List[str]:
        """
        Parse natural language into calculator tokens.
        
        Args:
            text: Natural language expression
            
        Returns:
            List of tokens (numbers and operators)
        """
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove common prefixes
        prefixes = ['calculate', 'compute', 'what is', 'what\'s', 'solve', 'find']
        for prefix in prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        
        # Replace word operators with symbols
        for word, symbol in self.OPERATORS.items():
            text = text.replace(f' {word} ', f' {symbol} ')
        
        # Handle special cases
        text = text.replace('x', '*')  # multiplication
        text = text.replace('×', '*')
        text = text.replace('÷', '/')
        
        # Split into tokens (numbers and operators)
        # Match: numbers (including decimals), operators, parentheses
        pattern = r'(\d+\.?\d*|[+\-*/()%])'
        tokens = re.findall(pattern, text)
        
        # Clean tokens
        tokens = [t.strip() for t in tokens if t.strip()]
        
        return tokens
    
    def open_calculator(self) -> bool:
        """
        Open Windows calculator and bring to foreground.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Launch calculator
            launch_visible("calc.exe", title_hint="Calculator", maximize=False)
            time.sleep(1.5)
            
            # Find calculator window
            self.hwnd = WindowManager.find_window_by_title("Calculator", timeout=3.0)
            
            if not self.hwnd:
                return False
            
            # Bring to front
            success = WindowManager.bring_to_front(self.hwnd)
            time.sleep(0.5)
            
            # Clear calculator (press Escape)
            pyautogui.press('escape')
            time.sleep(0.2)
            
            return success
            
        except Exception as e:
            print(f"Calculator open error: {e}")
            return False
    
    def focus_calculator(self) -> bool:
        """Ensure calculator has focus."""
        if not self.hwnd:
            return False
        
        try:
            WindowManager.bring_to_front(self.hwnd)
            time.sleep(0.2)
            return True
        except Exception:
            return False
    
    def press_key(self, key: str, description: str = None) -> None:
        """
        Press a key on calculator with visual feedback.
        
        Args:
            key: Key to press
            description: Human-readable description for logging
        """
        # Ensure calculator has focus
        self.focus_calculator()
        
        # Get the actual key to press
        actual_key = self.KEY_MAP.get(key, key)
        
        # Log what we're doing
        if description:
            print(f"  → {description}")
        else:
            print(f"  → Pressing: {key}")
        
        # Press the key
        pyautogui.press(actual_key)
        
        # Wait to show the visual change
        time.sleep(self.step_delay)
    
    def execute_step_by_step(self, tokens: List[str]) -> str:
        """
        Execute calculator operations step by step with visual feedback.
        
        Args:
            tokens: List of tokens (numbers and operators)
            
        Returns:
            Status message
        """
        if not tokens:
            return "No valid expression to calculate"
        
        print(f"\n🧮 Executing: {' '.join(tokens)}")
        print("=" * 50)
        
        # Open calculator
        if not self.open_calculator():
            return "❌ Failed to open calculator"
        
        # Execute each token
        for i, token in enumerate(tokens):
            # Determine description
            if token.isdigit() or '.' in token:
                desc = f"Number: {token}"
            elif token in ['+', '-', '*', '/', '%']:
                op_names = {'+': 'Plus', '-': 'Minus', '*': 'Times', '/': 'Divide', '%': 'Percent'}
                desc = f"Operator: {op_names.get(token, token)}"
            elif token in ['(', ')']:
                desc = f"Parenthesis: {token}"
            else:
                desc = f"Input: {token}"
            
            # For multi-digit numbers, press each digit
            if len(token) > 1 and token.replace('.', '').isdigit():
                for digit in token:
                    self.press_key(digit, f"Digit: {digit}")
            else:
                self.press_key(token, desc)
        
        # Press equals to get result
        print("\n  → Calculating result...")
        self.press_key('=', "Equals (=)")
        
        print("=" * 50)
        print("✅ Calculation complete! Check calculator window for result.\n")
        
        return f"✅ Calculated: {' '.join(tokens)} = (see calculator)"
    
    def calculate(self, expression: str) -> str:
        """
        Main entry point: parse and execute expression visually.
        
        Args:
            expression: Natural language or mathematical expression
            
        Returns:
            Result message
        """
        # Parse expression
        tokens = self.parse_expression(expression)
        
        if not tokens:
            return "❌ Could not parse expression"
        
        # Show what we parsed
        print(f"\n📝 Parsed expression: {' '.join(tokens)}")
        
        # Execute step by step
        return self.execute_step_by_step(tokens)


# Convenience function for integration
def visual_calculator_compute(expression: str, step_delay: float = 0.3) -> str:
    """
    Compute expression visually on calculator.
    
    Args:
        expression: Natural language or math expression
        step_delay: Delay between steps (seconds)
        
    Returns:
        Result message
    """
    calc = VisualCalculator(step_delay=step_delay)
    return calc.calculate(expression)


# Advanced version with voice feedback
class VoiceCalculator(VisualCalculator):
    """Calculator with voice feedback for each step."""
    
    def __init__(self, step_delay: float = 0.3, enable_voice: bool = True):
        super().__init__(step_delay)
        self.enable_voice = enable_voice
        self.tts_engine = None
        
        if enable_voice:
            try:
                import pyttsx3
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 150)
            except Exception:
                self.enable_voice = False
    
    def speak(self, text: str) -> None:
        """Speak text using TTS."""
        if self.enable_voice and self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception:
                pass
    
    def press_key(self, key: str, description: str = None) -> None:
        """Press key with voice feedback."""
        # Speak what we're doing
        if description and self.enable_voice:
            # Convert to speakable text
            speakable = description.replace('→', '').replace(':', '').strip()
            self.speak(speakable)
        
        # Call parent method
        super().press_key(key, description)
    
    def execute_step_by_step(self, tokens: List[str]) -> str:
        """Execute with voice feedback."""
        if self.enable_voice:
            self.speak("Opening calculator")
        
        result = super().execute_step_by_step(tokens)
        
        if self.enable_voice and "✅" in result:
            self.speak("Calculation complete")
        
        return result


def voice_calculator_compute(expression: str, step_delay: float = 0.3) -> str:
    """
    Compute expression visually with voice feedback.
    
    Args:
        expression: Natural language or math expression
        step_delay: Delay between steps (seconds)
        
    Returns:
        Result message
    """
    calc = VoiceCalculator(step_delay=step_delay, enable_voice=True)
    return calc.calculate(expression)


# Test examples
if __name__ == "__main__":
    print("=" * 60)
    print("Visual Step-by-Step Calculator Test")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        "2 + 5 + 4 + 3",
        "10 times 5 plus 3",
        "100 divided by 4",
        "calculate 25 minus 7 plus 2",
        "what is 3.5 times 2",
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {test}")
        print('='*60)
        
        result = visual_calculator_compute(test, step_delay=0.4)
        print(f"\nResult: {result}")
        
        if i < len(test_cases):
            input("\nPress Enter for next test...")
            time.sleep(1)
    
    print("\n" + "="*60)
    print("✅ All tests complete!")
    print("="*60)
