
# PriVsense (Pri-V-Sense)

This project pseudonymizes text data using `spaCy` and `Faker`. The project identifies and replaces personal names, organization names, URLs, and emails with pseudonyms, ensuring that sensitive information is anonymized. It is designed to work with text files and can dynamically load custom company names from a specified file. Additionally, it provides a Flask API for easy integration.

## Features

- **Named Entity Recognition**: Uses `spaCy`'s transformer-based model (`en_core_web_trf`) to accurately identify named entities in the text.
- **Custom Entity Patterns**: Allows adding custom company names from a file (`companies.txt`), handling both upper and lower case variations.
- **Pseudonymization**: Replaces identified names, organizations, URLs, and emails with realistic pseudonyms generated by `Faker`.
- **Flask API**: Provides endpoints to pseudonymize text from JSON input or from a file.
- **Flexible Input Handling**: Can work with both plain text input and text files.

## Process Flow

![image](https://github.com/user-attachments/assets/3d58f163-625c-4364-b4c5-4efe1d755607)


## Screenshot
<img width="494" alt="2024-08-06_14-04" src="https://github.com/user-attachments/assets/0639b41d-3169-47d3-9844-117fd0be2362">

## Requirements

- Python 3.11
- `spaCy`
- `spaCy-transformers`
- `Faker`
- `Flask`
- `Flask-CORS`
- GPU with CUDA Toolkit 12 (Can still work with both CPU and GPU)

## Installation

1. Install the required libraries:
    ```sh
    conda create -n venv
    conda activate venv
    conda install -c conda-forge spacy
    conda install -c conda-forge cupy
    python -m spacy download en_core_web_trf
    pip install flask flask-cors
    ```

## Usage

### API Usage

1. Start the Flask server:
    ```sh
    python pseudoanon.py
    ```

2. Use the following API endpoints:

    - **Pseudonymize text from JSON**:
        - **Endpoint**: `/pseudonymize`
        - **Method**: POST
        - **Payload**:
          ```json
          {
              "text": "John Doe is a software engineer at Acme Corp. Jane Doe, his colleague, works in the marketing department."
          }
          ```
        - **Response**:
          ```json
          {
              "pseudonymized_text": "Richard Roe is a software engineer at Dynamic Solutions. Elizabeth Smith, his colleague, works in the marketing department."
          }
          ```

    - **Pseudonymize text from a file**:
        - **Endpoint**: `/pseudonymize-file`
        - **Method**: POST
        - **Payload**: A file upload with the text content.
        - **Response**:
          ```json
          {
              "pseudonymized_text": "Richard Roe is a software engineer at Dynamic Solutions. Elizabeth Smith, his colleague, works in the marketing department."
          }
          ```

## Example

**input.txt**:
```
John Doe is a software engineer at Acme Corp. Jane Doe, his colleague, works in the marketing department.
Acme Corp recently announced a merger with Tech Solutions, another leading company in the industry.
```

**companies.txt**:
```
Acme Corp
Tech Solutions
```

## Customization

- **Adding More Companies**: Simply add more company names to the `companies.txt` file, one per line.
- **Handling Case Sensitivity**: The project automatically handles both upper and lower case variations of the company names.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.
