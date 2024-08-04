# AI Chatbots

## Overview
This repository contains the source code for "AI Chatbots", a program designed to create and interact with AI-based chatbots. Leveraging OpenAI's API, this tool offers a streamlined approach to deploying conversational agents capable of handling various dialogue scenarios.

## Features
- **GPT-based Conversations:** Utilize the power of OpenAI's GPT models to generate realistic and engaging conversations.
- **Configurable Settings:** Easy customization of API keys and other parameters through a `config.json` file.
- **Testing Mode:** Includes a testing mode to validate chatbot interactions without affecting live data.

## Prerequisites
To use this chatbot framework, you will need:
- Python 3.x
- Access to OpenAI API credentials (API key, Organization ID, and Project ID).

## Installation
Ensure Python and `pip` are installed on your system, then follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ribartra/ai-chatbots.git
   cd custom-chatbots
   ```

2. **Install required libraries:**
   ```bash
   pip install requests
   ```

## Configuration
Create a `config.json` file in the root directory of the project and populate it with your OpenAI credentials and other configuration settings:

```json
{
  "OPENAI_API_KEY": "your-openai-api-key",
  "OPENAI_ORG_ID": "your-openai-org-id",
  "OPENAI_PROJECT_ID": "your-openai-project-id",
  "TESTING": true
}
```

## Usage
To start the chatbot:
1. Ensure the `config.json` is configured correctly.
2. Run the program:
   ```bash
   python app.py
   ```

In testing mode (`"TESTING": true`), the program will show extra information about interaction like usage and threads, ideal for development and debugging.

## Contributing
Contributions to "AI Chatbots" are welcome. Please fork the repository, make your changes, and submit a pull request for review.

## License
This project is licensed under the MIT [LICENSE](LICENSE) - see the LICENSE file for details.
