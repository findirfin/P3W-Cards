# P3W Cards - AI-Powered Facts Generation System

A powerful tool that generates comprehensive facts and information about any topic using multiple AI models (Perplexity and Google's Gemini).

## Features

- Generate detailed questions about any topic
- Gather answers using Perplexity AI
- Extract and analyze facts using Google's Gemini AI
- Save facts to organized text files
- View statistics about previously generated facts
- Interactive CLI with visual feedback

## Prerequisites

- Python 3.8 or higher
- API keys for Perplexity AI and Google's Gemini
- pip (Python package manager)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd "P3W Cards"
```

2. Install required dependencies:
```bash
pip install python-dotenv requests google-generativeai colorama
```

3. Create a `.env` file in the project root:
```bash
PERPLEXITY_API_KEY=your_perplexity_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

## Getting API Keys

### Perplexity AI
1. Visit [Perplexity AI](https://www.perplexity.ai/)
2. Create an account or sign in
3. Navigate to API settings
4. Generate and copy your API key

### Google Gemini
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create or sign in to your Google account
3. Create a new API key
4. Copy the generated key

## Usage

1. Run the program:
```bash
python main.py
```

2. Choose from the menu options:
   - Option 1: Generate facts about a new topic
   - Option 2: View statistics of previously generated facts
   - Option 3: Exit the program

3. When generating facts:
   - Enter your topic of interest
   - The system will generate relevant questions
   - Gather answers from Perplexity AI
   - Extract and analyze facts using Gemini
   - Save results to a text file

## Output Format

Facts are saved in text files with the following format:
```
Facts about: [Topic]
==================================================

Title: [Fact Title]
Content: [Detailed fact information]
Citation: [Source URL or reference]
--------------------------------------------------
```

## Tips for Best Results

1. Be specific with your topics
2. Use clear, concise topic names
3. Wait for all animations to complete
4. Check the generated facts file in the project directory

## Troubleshooting

- **API Key Errors**: Ensure your `.env` file is properly configured
- **Connection Issues**: Check your internet connection
- **JSON Errors**: The topic might be too complex, try a simpler one
- **Rate Limiting**: Wait a few minutes if you receive API rate limit errors

## Error Messages

- `PERPLEXITY_API_KEY not found`: Check your `.env` file
- `GEMINI_API_KEY not found`: Verify your Google API key
- `API request failed`: Check your internet connection or API key validity
- `Invalid JSON format`: The AI response couldn't be parsed correctly

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License with additional attribution requirements - see the LICENSE file for details.

Important: When submitting facts or points generated using this software, you must include the attribution: "Generated using P3W Cards by findirfin"
