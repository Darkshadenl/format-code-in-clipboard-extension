#!/usr/bin/env python3
import re
import json
from pathlib import Path
from typing import List, Dict
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    regex_patterns: Dict[str, str] = {
        "attribute": r"\[\s*\w+(?:\([^)]*\))?\s*\]",
        "namespace": r"namespace\s+\w+(?:\.\w+)*(?:;|\s*\{)",
        "class_basic": r"(?:public|internal|private|protected)?\s+class\s+\w+\s*\{",
        "class_with_inheritance": r"(?:public|internal|private|protected)?\s+class\s+\w+\s*:\s*\w+(?:\s*,\s*\w+)*\s*\{",
        "abstract_class": r"(?:public|internal|private|protected)?\s+abstract\s+class\s+\w+\s*\{",
        "record": r"(?:public|internal|private|protected)?\s+record\s+\w+\s*\{",
        "struct": r"(?:public|internal|private|protected)?\s+struct\s+\w+\s*\{",
        "interface": r"(?:public|internal|private|protected)?\s+interface\s+\w+\s*\{",
        "enum": r"(?:public|internal|private|protected)?\s+enum\s+\w+\s*\{",
        "constructor": r"(?:public|internal|private|protected)?\s+\w+\s*\([^)]*\)\s*\{",
        "destructor": r"~\w+\s*\(\)\s*\{",
        "method_basic": r"(?:public|internal|private|protected)?\s+(?!async)(?:[\w<>]+\s+)+\w+\s*\([^)]*\)\s*\{?",
        "method_async": r"(?:public|internal|private|protected)?\s+async\s+(?:[\w<>]+\s+)+\w+\s*\([^)]*\)\s*\{",
        "overridden": r"(?:public|internal|private|protected)?\s+override\s+(?:[\w<>]+\s+)+\w+\s*\([^)]*\)\s*\{",
        "generic_class": r"(?:public|internal|private|protected)?\s+class\s+\w+<\w+(?:\s*,\s*\w+)*>\s*\{",
        "generic_method": r"(?:public|internal|private|protected)?\s+(?:[\w<>]+\s+)+\w+<\w+(?:\s*,\s*\w+)*>\s*\([^)]*\)\s*\{",
        "auto_property": r"(?:public|internal|private|protected)?\s+\w+\s+\w+\s*\{\s*(?:get|set|init)(?:\s*;\s*(?:get|set|init))*\s*\}",
        "readonly_property": r"(?:public|internal|private|protected)?\s+\w+\s+\w+\s*\{\s*get;\s*\}",
        "expression_bodied_member": r"=>\s*[^;]+;",
        "field": r"(?:public|internal|private|protected)\s+(?:static\s+)?(?:readonly\s+)?\S+\s+\w+\s*(=\s*[^;]+)?;",
        "local_variable": r"(?:var|\S+)\s+\w+\s*(=\s*[^;]+)?;",
        "constant": r"(?:public|internal|private|protected)?\s+const\s+\S+\s+\w+\s*=\s*[^;]+;",
        "delegate": r"(?:public|internal|private|protected)?\s+delegate\s+\S+\s+\w+\s*\([^)]*\);",
        "lambda": r"=>\s*\{?",
        "for_loop": r"for\s*\([^)]*\)\s*\{",
        "if_statement": r"if\s*\([^)]*\)\s*\{?",
        "switch_statement": r"switch\s*\([^)]*\)\s*\{",
        "pattern_matching": r"\bis\s+\w+\s*=>",
        "comment": r"^\s*//",
        "code_symbols": r"[{}();=]",
    }
    regex_match_threshold: int = 2
    outPath: Path = Path("./output/")
    outPathJson: Path = outPath / Path("json")
    outPathTxt: Path = outPath / Path("text")

    class Config:
        env_file = ".env"


def process_clipboard_text(text: str, config: BaseSettings) -> str:
    # Case 1: Explicit code blocks - keep as is
    if "```csharp" in text and "```" in text[text.index("```csharp") + 8 :]:
        return text

    # Case 2: Standalone code block
    if text.lstrip().startswith(("public class", "namespace")):
        return "```csharp\n" + text.strip() + "\n```"

    # Case 3: Inline code with "codefragment:" or "code"
    if len(text.splitlines()) == 1 and "public" in text and "{" in text and "}" in text:
        pattern = r"(public\s+\w+\s+\w+\s*\([^)]*\)\s*{[^}]*})"
        match = re.search(pattern, text)
        if match:
            code = match.group(1)
            before = text[: match.start()].rstrip()
            after = text[match.end() :].lstrip()
            if "codefragment:" in before.lower():
                return f"{before} ```csharp\n{code}```\n{after}"
            elif "code" in before.lower():
                return f"{before} ```csharp\n{code}\n```\n{after}"
            else:
                return f"{before}: ```csharp {code}``` {after}"

    # Case 4 & 5: Code blocks with text
    lines = text.splitlines()
    result = []
    current_block = []
    in_code = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Check for code block start
        if (
            not in_code
            and (stripped.startswith("public") or stripped.startswith("namespace"))
            and not (
                stripped.startswith("public void Execute()") and "codefragment:" in text
            )
        ):
            # Start new code block
            if current_block:
                result.extend(current_block)
                current_block = []
            result.append("```csharp")
            current_block.append(line)
            in_code = True
            continue

        # Inside code block
        if in_code:
            # Check for end of code block
            if (
                stripped.startswith("Text na de code")
                or stripped.startswith("Hier wat")
                or stripped.startswith("Opnieuw tekst")
            ):
                # Close current block
                result.extend(current_block)
                result.append("```")
                result.append(line)
                current_block = []
                in_code = False
            else:
                current_block.append(line)
            continue

        # Regular text
        if stripped:
            if current_block:
                result.extend(current_block)
                current_block = []
            result.append(line)

    # Handle any remaining code block
    if current_block:
        if in_code:
            result.extend(current_block)
            result.append("```")
        else:
            result.extend(current_block)

    return "\n".join(result)


def compare_outputs(config: Config) -> float:
    """Compare output.json with output_samples.json and return similarity percentage"""
    import difflib

    def normalize_text(text: str) -> str:
        """Normalize text for comparison by removing extra whitespace"""
        return "\n".join(line.strip() for line in text.splitlines() if line.strip())

    def safe_load_json(filepath: str) -> list:
        """Safely load JSON file with error handling"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                if not content.strip():
                    return []
                return json.loads(content).get("outputs", [])
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    # Read outputs
    current_outputs = safe_load_json(config.outPathJson / "output.json")
    sample_outputs = safe_load_json(config.outPathJson / "output_samples.json")

    print("\nDebug info:")
    print(f"Current outputs count: {len(current_outputs)}")
    print(f"Sample outputs count: {len(sample_outputs)}")

    # Create mapping of descriptions to normalized outputs
    current_map = {}
    sample_map = {}

    if isinstance(current_outputs, list):
        current_map = {
            o.get("description", ""): normalize_text(o.get("output", ""))
            for o in current_outputs
            if isinstance(o, dict)
        }
        print(f"Current map entries: {len(current_map)}")
        print("Current descriptions:", list(current_map.keys()))

    if isinstance(sample_outputs, list):
        sample_map = {
            o.get("description", ""): normalize_text(o.get("output", ""))
            for o in sample_outputs
            if isinstance(o, dict)
        }
        print(f"Sample map entries: {len(sample_map)}")
        print("Sample descriptions:", list(sample_map.keys()))

    # Calculate similarity per test case
    total_similarity = 0
    matched_tests = 0

    # Debug output
    print("\nComparing outputs:")
    for desc, sample_output in sample_map.items():
        if desc in current_map:
            current_output = current_map[desc]
            print(f"\nTest case: {desc}")
            print("Sample output:")
            print(sample_output)
            print("\nCurrent output:")
            print(current_output)
            if current_output == sample_output:
                print("Exact match!")
                total_similarity += 1.0
            else:
                matcher = difflib.SequenceMatcher(None, current_output, sample_output)
                ratio = matcher.ratio()
                print(f"Similarity ratio: {ratio}")
                total_similarity += ratio
            matched_tests += 1

    # Return average similarity across matched tests
    if matched_tests > 0:
        return (total_similarity / matched_tests) * 100
    return 0.0


def load_test_inputs(json_filename: str) -> List[dict]:
    with open(json_filename, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data.get("inputs", [])


def handle_file_management(config: Config):
    """Handle output file management including backups and clearing"""
    output_txt = config.outPathTxt / Path("output.txt")
    output_json = config.outPathJson / Path("output.json")
    prev_output_txt = config.outPathTxt / Path("output_prev.txt")
    prev_output_json = config.outPathJson / Path("output_prev.json")

    if Path.exists(output_txt):
        # Backup current outputs
        with open(output_txt, "r", encoding="utf-8") as f:
            current_txt = f.read()
        with open(prev_output_txt, "w", encoding="utf-8") as f:
            f.write(current_txt)

        if Path.exists(output_json):
            with open(output_json, "r", encoding="utf-8") as f:
                current_json = json.load(f)
            with open(prev_output_json, "w", encoding="utf-8") as f:
                json.dump(current_json, f, indent=2)

        # Clear current outputs
        with open(output_txt, "w", encoding="utf-8") as f:
            f.truncate(0)
        with open(output_json, "w", encoding="utf-8") as f:
            f.truncate(0)


def process_test_inputs(config: Config):
    """Process test inputs and return outputs"""
    json_filename = "input_samples.json"
    test_inputs = load_test_inputs(json_filename)
    outputs = []
    tempTextfile = []

    # First process all inputs
    for test in test_inputs:
        description = test.get("description", "Geen beschrijving")
        input_text = test.get("input", "")
        output_text = process_clipboard_text(input_text, config)
        outputs.append({"description": description, "output": output_text})
        tempTextfile.append(f"--- {description} ---\n{output_text}\n" + "=" * 40 + "\n")

    # Write JSON output first
    output_json = config.outPathJson / Path("output.json")
    with open(output_json, "w", encoding="utf-8") as json_f:
        json.dump({"outputs": outputs}, json_f, indent=2)

    # Calculate similarity after writing JSON
    similarity = compare_outputs(config)
    simText = f"Output similarity: {similarity:.2f}%\n"
    if similarity < 90:
        simText = f"{simText}Warning: Output similarity is below 90% threshold\n\n"

    # Write text output
    output_txt = config.outPathTxt / Path("output.txt")
    with open(output_txt, "w", encoding="utf-8") as txt_f:
        txt_f.write(f"regex_match_threshold: {config.regex_match_threshold}\n")
        txt_f.write(simText)
        txt_f.write("".join(tempTextfile))

    print(simText)


def main():
    """Main function that orchestrates the program execution"""
    config = Config()
    handle_file_management(config)
    process_test_inputs(config)


if __name__ == "__main__":
    main()
