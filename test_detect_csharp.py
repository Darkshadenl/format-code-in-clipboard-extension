import json
import pytest
from klembord_detect_csharp import process_clipboard_text, Config


def load_test_cases():
    """Load test cases from input_samples.json"""
    with open("input_samples.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("inputs", [])


@pytest.fixture
def config():
    """Fixture to provide Config instance"""
    return Config()


@pytest.mark.parametrize("test_case", load_test_cases())
def test_process_clipboard_text(test_case, config):
    """Test each case from input_samples.json"""
    description = test_case.get("description", "No description")
    input_text = test_case.get("input", "")
    expected_output = test_case.get("expected_output", "")

    result = process_clipboard_text(input_text, config)

    # Compare ignoring whitespace differences
    def normalize(text):
        return "\n".join(line.strip() for line in text.splitlines() if line.strip())

    assert normalize(result) == normalize(expected_output), (
        f"Failed test case: {description}\nExpected:\n{expected_output}\nGot:\n{result}"
    )


def test_explicit_code_block():
    """Test case 1: Explicit code blocks should be preserved"""
    config = Config()
    input_text = """Dit is een tekstuele introductie.
```csharp
public class HelloWorld {
    static void Main() {
        Console.WriteLine("Hello World");
    }
}
```
Hieronder volgt de uitleg na het codeblok."""

    result = process_clipboard_text(input_text, config)
    assert result == input_text


def test_standalone_code():
    """Test case 2: Standalone code should be wrapped"""
    config = Config()
    input_text = """public class MyClass {
    public void MyMethod() {
        // code snippet
        Console.WriteLine("Test");
    }
}"""

    expected = """```csharp
public class MyClass {
    public void MyMethod() {
        // code snippet
        Console.WriteLine("Test");
    }
}
```"""

    result = process_clipboard_text(input_text, config)
    assert result.strip() == expected.strip()


def test_inline_code():
    """Test case 3: Inline code should be properly formatted"""
    config = Config()
    input_text = """Hier is een voorbeeld waar een codefragment: public void Execute() { doSomething(); } direct in de zin zit, waarna de tekst verdergaat."""

    expected = """Hier is een voorbeeld waar een codefragment: ```csharp public void Execute() { doSomething(); }``` direct in de zin zit, waarna de tekst verdergaat."""

    result = process_clipboard_text(input_text, config)
    assert result == expected


def test_code_with_text():
    """Test case 4: Code with surrounding text"""
    config = Config()
    input_text = """Text voorafgaand aan code.
public void ExampleFunction() {
    // Enkele instructies
    if (true) {
        Console.WriteLine("Dit is echte code.");
    }
    // er ontbreekt een afsluitende structuur
Text na de code fragment."""

    expected = """Text voorafgaand aan code.
```csharp
public void ExampleFunction() {
    // Enkele instructies
    if (true) {
        Console.WriteLine("Dit is echte code.");
    }
    // er ontbreekt een afsluitende structuur
```
Text na de code fragment."""

    result = process_clipboard_text(input_text, config)
    assert result.strip() == expected.strip()


def test_multiple_code_blocks():
    """Test case 5: Multiple code blocks with text"""
    config = Config()
    input_text = """Start van tekst.
public class Start {
    public void Run() {
        // eerste codeblok
        Execute();
    }
}
Hier wat tussentijdse tekst.
namespace Eind {
    public class EndClass {
        public static void End() {
            // tweede codeblok
        }
    }
}
Opnieuw tekst na de code segmenten."""

    expected = """Start van tekst.
```csharp
public class Start {
    public void Run() {
        // eerste codeblok
        Execute();
    }
}
```
Hier wat tussentijdse tekst.
```csharp
namespace Eind {
    public class EndClass {
        public static void End() {
            // tweede codeblok
        }
    }
}
```
Opnieuw tekst na de code segmenten."""

    result = process_clipboard_text(input_text, config)
    assert result.strip() == expected.strip()
