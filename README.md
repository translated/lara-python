# Lara Python SDK

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

This SDK empowers you to build your own branded translation AI leveraging our translation fine-tuned language model. 

All major translation features are accessible, making it easy to integrate and customize for your needs. 

## 🌍 **Features:**
- **Text Translation**: Single strings, multiple strings, and complex text blocks
- **Document Translation**: Word, PDF, and other document formats with status monitoring
- **Translation Memory**: Store and reuse translations for consistency
- **Glossaries**: Enforce terminology standards across translations
- **Language Detection**: Automatic source language identification
- **Advanced Options**: Translation instructions and more

## 📚 Documentation

Lara's SDK full documentation is available at [https://developers.laratranslate.com/](https://developers.laratranslate.com/)

## 🚀 Quick Start

### Installation

```bash
pip install lara-sdk
```

### Basic Usage

```python
import os
from lara_sdk import Credentials, Translator

# Set your credentials using environment variables (recommended)
credentials = Credentials(
  os.environ.get('LARA_ACCESS_KEY_ID'),
  os.environ.get('LARA_ACCESS_KEY_SECRET')
)

# Create translator instance
lara = Translator(credentials)

# Simple text translation
try:
  result = lara.translate("Hello, world!", target="fr-FR", source="en-US")
  print(f"Translation: {result.translation}")
  # Output: Translation: Bonjour, le monde !
except Exception as error:
  print(f"Translation error: {error}")
```

## 📖 Examples

The `examples/` directory contains comprehensive examples for all SDK features.

**All examples use environment variables for credentials, so set them first:**
```bash
export LARA_ACCESS_KEY_ID="your-access-key-id"
export LARA_ACCESS_KEY_SECRET="your-access-key-secret"
```

### Text Translation
- **[text_translation.py](examples/text_translation.py)** - Complete text translation examples
  - Single string translation
  - Multiple strings translation  
  - Translation with instructions
  - TextBlocks translation (mixed translatable/non-translatable content)
  - Auto-detect source language
  - Advanced translation options
  - Get available languages

```bash
cd examples
python text_translation.py
```

### Document Translation
- **[document_translation.py](examples/document_translation.py)** - Document translation examples
  - Basic document translation
  - Advanced options with memories and glossaries
  - Step-by-step translation with status monitoring

```bash
cd examples
python document_translation.py
```

### Translation Memory Management
- **[memories_management.py](examples/memories_management.py)** - Memory management examples
  - Create, list, update, delete memories
  - Add individual translations
  - Multiple memory operations
  - TMX file import with progress monitoring
  - Translation deletion
  - Translation with TUID and context

```bash
cd examples
python memories_management.py
```

### Glossary Management
- **[glossaries_management.py](examples/glossaries_management.py)** - Glossary management examples
  - Create, list, update, delete glossaries
  - CSV import with status monitoring
  - Glossary export
  - Glossary terms count
  - Import status checking

```bash
cd examples
python glossaries_management.py
```

## 🔧 API Reference

### Core Components

### 🔐 Authentication

The SDK supports authentication via access key and secret:

```python
from lara_sdk import Credentials, Translator

credentials = Credentials("your-access-key-id", "your-access-key-secret")
lara = Translator(credentials)
```

**Environment Variables (Recommended):**
```bash
export LARA_ACCESS_KEY_ID="your-access-key-id"
export LARA_ACCESS_KEY_SECRET="your-access-key-secret"
```

```python
import os
from lara_sdk import Credentials

credentials = Credentials(
    os.environ['LARA_ACCESS_KEY_ID'],
    os.environ['LARA_ACCESS_KEY_SECRET']
)
```

**Alternative Constructor:**
```python
# You can also pass credentials directly to Translator
lara = Translator(
    access_key_id="your-access-key-id",
    access_key_secret="your-access-key-secret"
)
```


### 🌍 Translator

```python
# Create translator with credentials
lara = Translator(credentials)
```

#### Text Translation

```python
# Basic translation
result = lara.translate("Hello", target="fr-FR", source="en-US")

# Multiple strings
result = lara.translate(["Hello", "World"], target="fr-FR", source="en-US")

# TextBlocks (mixed translatable/non-translatable content)
from lara_sdk import TextBlock

text_blocks = [
    TextBlock(text="Translatable text", translatable=True),
    TextBlock(text="<br>", translatable=False),  # Non-translatable HTML
    TextBlock(text="More translatable text", translatable=True)
]
result = lara.translate(text_blocks, target="fr-FR", source="en-US")

# With advanced options

result = lara.translate(
    "Hello",
    target="fr-FR",
    source="en-US",
    instructions=["Formal tone"],
    adapt_to=["memory-id"],  # Replace with actual memory IDs
    glossaries=["glossary-id"],  # Replace with actual glossary IDs
    style="fluid",
    timeout_ms=10000
)
```

### 📖 Document Translation
#### Simple document translation
```python
translated_content = lara.documents.translate(
    file_path="/path/to/your/document.txt",  # Replace with actual file path
    filename="document.txt",
    source="en-US",
    target="fr-FR"
)

# With options
translated_content = lara.documents.translate(
    file_path="/path/to/your/document.txt",  # Replace with actual file path
    filename="document.txt",
    source="en-US",
    target="fr-FR",
    adapt_to=["mem_1A2b3C4d5E6f7G8h9I0jKl"],  # Replace with actual memory IDs
    glossaries=["gls_1A2b3C4d5E6f7G8h9I0jKl"],  # Replace with actual glossary IDs
    style="fluid"
)
```
### Document translation with status monitoring
#### Document upload
```python
#Optional: upload options
document = lara.documents.upload(
    file_path="/path/to/your/document.txt",  # Replace with actual file path
    filename="document.txt",
    source="en-US",
    target="fr-FR",
    adapt_to=["mem_1A2b3C4d5E6f7G8h9I0jKl"],  # Replace with actual memory IDs
    glossaries=["gls_1A2b3C4d5E6f7G8h9I0jKl"]  # Replace with actual glossary IDs
)
```
#### Document translation status monitoring
```python
status = lara.documents.status(document.id)
```
#### Download translated document
```python
translated_content = lara.documents.download(document.id)
```

### 🧠 Memory Management

```python
# Create memory
memory = lara.memories.create("MyMemory")

# Create memory with external ID (MyMemory integration)
memory = lara.memories.create("Memory from MyMemory", external_id="aabb1122")  # Replace with actual external ID

# Important: To update/overwrite a translation unit you must provide a tuid. Calls without a tuid always create a new unit and will not update existing entries.
# Add translation to single memory
memory_import = lara.memories.add_translation("mem_1A2b3C4d5E6f7G8h9I0jKl", "en-US", "fr-FR", "Hello", "Bonjour", tuid="greeting_001")

# Add translation to multiple memories
memory_import = lara.memories.add_translation(["mem_1A2b3C4d5E6f7G8h9I0jKl", "mem_2XyZ9AbC8dEf7GhI6jKlMn"], "en-US", "fr-FR", "Hello", "Bonjour", tuid="greeting_002")

# Add with context
memory_import = lara.memories.add_translation(
    "mem_1A2b3C4d5E6f7G8h9I0jKl", "en-US", "fr-FR", "Hello", "Bonjour", 
    tuid="tuid", sentence_before="sentenceBefore", sentence_after="sentenceAfter"
)

# TMX import from file
memory_import = lara.memories.import_tmx("mem_1A2b3C4d5E6f7G8h9I0jKl", "/path/to/your/memory.tmx")  # Replace with actual TMX file path

# Delete translation
# Important: if you omit tuid, all entries that match the provided fields will be removed
delete_job = lara.memories.delete_translation(
  "mem_1A2b3C4d5E6f7G8h9I0jKl", "en-US", "fr-FR", "Hello", "Bonjour", tuid="greeting_001"
)

# Wait for import completion
completed_import = lara.memories.wait_for_import(memory_import, max_wait_time=300)  # 5 minutes
```

### 📚 Glossary Management

```python
# Create glossary
glossary = lara.glossaries.create("MyGlossary")

# Import CSV from file
glossary_import = lara.glossaries.import_csv("gls_1A2b3C4d5E6f7G8h9I0jKl", "/path/to/your/glossary.csv")  # Replace with actual CSV file path

# Check import status
import_status = lara.glossaries.get_import_status(import_id)

# Wait for import completion
completed_import = lara.glossaries.wait_for_import(glossary_import, max_wait_time=300)  # 5 minutes

# Export glossary
csv_data = lara.glossaries.export("gls_1A2b3C4d5E6f7G8h9I0jKl", "csv/table-uni", "en-US")

# Get glossary terms count
counts = lara.glossaries.counts("gls_1A2b3C4d5E6f7G8h9I0jKl")
```

### Translation Options

```python
result = lara.translate(
    text,
    target="fr-FR",                          # Target language (required)
    source="en-US",                          # Source language (optional, auto-detect if None)
    source_hint="en",                        # Hint for source language detection
    adapt_to=["memory-id"],                  # Memory IDs to adapt to
    glossaries=["glossary-id"],              # Glossary IDs to use
    instructions=["instruction"],            # Translation instructions
    style="fluid",                           # Translation style (fluid, faithful, creative)
    content_type="text/plain",               # Content type (text/plain, text/html, etc.)
    multiline=True,                          # Enable multiline translation
    timeout_ms=10000,                        # Request timeout in milliseconds
    no_trace=False,                          # Disable request tracing
    verbose=False,                           # Enable verbose response
)
```

### Language Codes

The SDK supports full language codes (e.g., `en-US`, `fr-FR`, `es-ES`) as well as simple codes (e.g., `en`, `fr`, `es`):

```python
# Full language codes (recommended)
result = lara.translate("Hello", target="fr-FR", source="en-US")

# Simple language codes
result = lara.translate("Hello", target="fr", source="en")
```

### 🌐 Supported Languages

The SDK supports all languages available in the Lara API. Use the `languages()` method to get the current list:

```python
languages = lara.languages()
print(f"Supported languages: {', '.join(languages)}")
```

## ⚙️ Configuration
### Error Handling

The SDK provides detailed error information:

```python
from lara_sdk import LaraApiError, LaraError

try:
    result = lara.translate("Hello", target="fr-FR", source="en-US")
    print(f"Translation: {result.translation}")
except LaraApiError as error:
    print(f"API Error [{error.status_code}]: {error.message}")
    print(f"Error type: {error.type}")
except LaraError as error:
    print(f"SDK Error: {error}")
except Exception as error:
    print(f"Unexpected error: {error}")
```

## 📋 Requirements

- Python 3.8 or higher
- pip
- Valid Lara API credentials

## 🧪 Testing

Run the examples to test your setup.

```bash
# All examples use environment variables for credentials, so set them first:
export LARA_ACCESS_KEY_ID="your-access-key-id"
export LARA_ACCESS_KEY_SECRET="your-access-key-secret"
```
```bash
# Run basic text translation example
cd examples
python text_translation.py
```

## 🏗️ Building from Source

```bash
# Clone the repository
git clone https://github.com/translated/lara-python.git
cd lara-python

# Install in development mode
pip install -e .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Happy translating! 🌍✨
