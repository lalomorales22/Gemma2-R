# Gemma2B-R: Advanced Software Engineering Chat Interface

Gemma2B-R is a powerful GUI application that leverages the Gemma 2B AI model for advanced software engineering tasks. This interface allows users to engage in high-level technical discussions, receive code implementations, and benefit from AI-driven software engineering insights.

## Features

- Interactive chat interface with Gemma 2B AI model
- Real-time streaming of AI responses
- Syntax-highlighted code display in separate windows
- Ability to save and copy generated code
- Customizable themes and font sizes
- Chat log saving functionality
- Configurable via `config.ini` file

## Requirements

- Python 3.7+
- Tkinter (usually comes pre-installed with Python)
- Requests library
- Ollama with the Gemma 2B model

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/lalomorales22/Gemma2B-R.git
   cd Gemma2B-R
   ```

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Ensure you have Ollama installed and the Gemma 2B model pulled:
   ```
   ollama pull gemma2:2b
   ```

## Configuration

Before running the application, you can customize its behavior by editing the `config.ini` file:

```ini
[API]
ollama_url = http://localhost:11434/api/generate

[GUI]
theme = clam
font_size = 10
```

## Usage

1. Start the Ollama server with the Gemma 2B model.

2. Run the application:
   ```
   python gemmaR.py
   ```

3. Use the GUI to interact with Gemma 2B:
   - Type your software engineering queries in the input field and press Enter or click 'Send'
   - View the AI's thought process, analysis, and implementation in separate sections
   - Access generated code in pop-up windows with options to copy or save the code
   - Use the menu options to save chat logs, change themes, or adjust font sizes

## Contributing

Contributions to Gemma2B-R are welcome! Please feel free to submit pull requests, create issues, or suggest improvements.

## License

[MIT License](LICENSE)

## Acknowledgements

- Gemma 2B model by Google
- Ollama for providing local API access to large language models
