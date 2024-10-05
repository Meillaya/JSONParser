# JSON Parser

## Overview

This project implements a custom JSON parser in Python. It provides a robust, efficient, and extensible solution for parsing JSON data, with a focus on readability and maintainability.

## Features

- **Lexical Analysis**: Tokenizes JSON input strings into a sequence of meaningful tokens.
- **Syntactic Analysis**: Parses the token stream to construct an Abstract Syntax Tree (AST).
- **Data Structure Generation**: Converts the AST into Python data structures (dictionaries, lists, etc.).
- **Error Handling**: Provides detailed error messages for invalid JSON inputs.
- **Custom Extensions**: Supports custom JSON extensions (configurable).
- **Performance Optimizations**: Implements efficient parsing algorithms.
- **Comprehensive Testing**: Includes unit tests and integration tests for reliability.

## Installation

To install the JSON parser, follow these steps:

1. Clone the repository:

``` python
   git clone https://github.com/Meillaya/JSONParser.git 
   cd json-parser
```

2. (Optional) Create and activate a virtual environment:

```python
    python -m venv venv
    source venv/bin/activate  # On Windows, use venv\Scripts\activate
```

3. Install the required dependencies:

```python
   pip install -r requirements.txt
```

