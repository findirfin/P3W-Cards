from dotenv import load_dotenv
import os
import requests
import google.generativeai as genai
from typing import Dict, Any, Tuple, Optional
import json
from colorama import init, Fore, Back, Style
import time
import sys

# Initialize colorama
init()

# Add this at the top of the file after imports
def print_typing_effect(text, delay=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def display_loading_animation(message, duration=3):
    animation = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        sys.stdout.write(f'\r{Fore.CYAN}{message} {animation[i % len(animation)]}{Style.RESET_ALL}')
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write('\r' + ' ' * (len(message) + 2) + '\r')
    sys.stdout.flush()

load_dotenv()


class PerplexityClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not found")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.base_url = "https://api.perplexity.ai/chat/completions"
    
    def query(self, 
              prompt: str, 
              model: str = "sonar",
              return_sources: bool = True
    ) -> Tuple[str, list]:
        """Send a query to Perplexity API and get response with optional sources"""
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            
            result = response.json()
            answer = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            sources = result.get('citations', []) if return_sources else []
            
            return answer, sources
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def ask(self, prompt: str) -> str:
        """Simplified method that returns only the answer"""
        answer, _ = self.query(prompt, return_sources=False)
        return answer












class GeminiClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def query(self, 
              prompt: str,
              return_sources: bool = True
    ) -> Tuple[str, list]:
        """Send a query to Gemini API and get response with optional sources"""
        try:
            response = self.model.generate_content(prompt)
            return response.text, []  # Gemini doesn't provide sources like Perplexity
            
        except Exception as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def ask(self, prompt: str) -> str:
        """Simplified method that returns only the answer"""
        answer, _ = self.query(prompt, return_sources=False)
        return answer








class FactsGenerator:
    def __init__(self):
        self.gemini = GeminiClient()
        self.perplexity = PerplexityClient()
    
    def generate_debate_questions(self, topic: str) -> str:
        prompt = f"""Generate 15 questions one might ask about the topic: "{topic}" when learning about it or preparing for a debate. output the questions in this json format: {{ "questions": [ "question1", "question2", ... ] }}"""
        
        response = self.gemini.ask(prompt)
        # Clean up the response by removing markdown code blocks
        cleaned_response = response.strip('`').replace('json\n', '').replace('```', '')
        return cleaned_response

    def get_perplexity_answers(self, questions_json: str) -> list:
        try:
            questions = json.loads(questions_json)['questions']
            answers = []
            
            print("\nGathering answers from Perplexity...")
            for i, question in enumerate(questions, 1):
                print(f"Processing question {i}/{len(questions)}")
                answer, sources = self.perplexity.query(question, return_sources=True)
                
                # Handle sources - they might be URLs directly or objects with URL field
                source_urls = []
                for source in sources:
                    if isinstance(source, dict):
                        url = source.get('url', 'No URL')
                    else:
                        url = str(source)
                    source_urls.append(url)
                
                answers.append({
                    "question": question, 
                    "answer": answer, 
                    "sources": source_urls
                })
            
            return answers
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            print(f"Error processing question: {str(e)}")
            return []
    
    def analyze_answers(self, answers: list) -> list:
        facts = []
        print("\nAnalyzing answers with Gemini...")
        
        for i, item in enumerate(answers, 1):
            print(f"Analyzing answer {i}/{len(answers)}")
            sources_str = "\n".join(item['sources']) if item['sources'] else "No sources available"
            
            prompt = f"""You are a fact extractor. Extract as many facts as possible from this answer and its sources.

Question: {item['question']}
Answer: {item['answer']}
Sources: {sources_str}

Return a JSON array of facts exactly like this example, with no other text:
[
    {{
        "title": "Clear Concise Title",
        "content": "Detailed fact statement",
        "citation": "URL from the provided sources, or 'No specific citation' if none"
    }}
]"""
            
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    result = self.gemini.ask(prompt)
                    # Clean and validate JSON
                    result = result.strip()
                    if not result.startswith('['):
                        result = result[result.find('['):]
                    if not result.endswith(']'):
                        result = result[:result.rfind(']')+1]
                    
                    parsed_facts = json.loads(result)
                    if isinstance(parsed_facts, list) and len(parsed_facts) > 0:
                        facts.extend(parsed_facts)
                        break
                except json.JSONDecodeError as e:
                    if attempt == max_retries - 1:
                        print(f"Warning: Could not parse facts from answer {i} after {max_retries} attempts")
                except Exception as e:
                    if attempt == max_retries - 1:
                        print(f"Error analyzing answer {i}: {str(e)}")
        
        return facts

    def run(self):
        print(f"{Fore.CYAN}[*] Initializing Facts Generator...{Style.RESET_ALL}")
        display_loading_animation("Loading AI modules", 2)
        print(f"\n{Fore.GREEN}[+] System ready!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] Type 'quit' to exit{Style.RESET_ALL}")
        
        while True:
            try:
                topic = input(f"\n{Fore.CYAN}[?] Enter a debate topic:{Style.RESET_ALL} ")
                if topic.lower() in ['quit', 'exit', 'q']:
                    print(f"\n{Fore.GREEN}[+] Shutting down...{Style.RESET_ALL}")
                    break
                
                print(f"\n{Fore.CYAN}[*] Generating questions for '{topic}'...{Style.RESET_ALL}")
                questions = self.generate_debate_questions(topic)
                print(f"\n{Fore.GREEN}[+] Generated questions:{Style.RESET_ALL}\n")
                print(questions)
                
                display_loading_animation("Connecting to AI services", 2)
                answers = self.get_perplexity_answers(questions)
                facts = self.analyze_answers(answers)
                
                if facts:
                    self.save_results(topic, facts)
                    print(f"\n{Fore.GREEN}[+] Results saved to facts_{topic.replace(' ', '_').lower()}.txt{Style.RESET_ALL}")
                else:
                    print(f"\n{Fore.RED}[-] No facts were successfully extracted.{Style.RESET_ALL}")
                    
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}[!] Operation cancelled by user. Exiting...{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"\n{Fore.RED}[-] Error: {str(e)}{Style.RESET_ALL}")

    def save_results(self, topic: str, facts: list):
        filename = f"facts_{topic.replace(' ', '_').lower()}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Facts about: {topic}\n")
            f.write("=" * 50 + "\n\n")
            
            for fact in facts:
                f.write(f"Title: {fact['title']}\n")
                f.write(f"Content: {fact['content']}\n")
                f.write(f"Citation: {fact['citation']}\n")
                f.write("-" * 50 + "\n\n")

    def count_existing_facts(self) -> list:
        """Count facts from all existing output files"""
        fact_files = [f for f in os.listdir() if f.startswith('facts_') and f.endswith('.txt')]
        results = []
        
        for file in fact_files:
            fact_count = 0
            topic = file[6:-4].replace('_', ' ').title()
            
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                fact_count = content.count('Title:')  # Count occurrences of "Title:" as each fact has one
            
            results.append((topic, fact_count, file))
        
        return results

# Replace the existing display_menu function with this one
def display_menu():
    logo = f"""
{Fore.CYAN}    ██████╗ ██████╗ ██╗    ██╗     ██████╗ █████╗ ██████╗ ██████╗ ███████╗
    ██╔══██╗╚════██╗██║    ██║    ██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝
    ██████╔╝ █████╔╝██║ █╗ ██║    ██║     ███████║██████╔╝██║  ██║███████╗
    ██╔═══╝  ╚═══██╗██║███╗██║    ██║     ██╔══██║██╔══██╗██║  ██║╚════██║
    ██║     ██████╔╝╚███╔███╔╝    ╚██████╗██║  ██║██║  ██║██████╔╝███████║
    ╚═╝     ╚═════╝  ╚══╝╚══╝      ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚══════╝{Style.RESET_ALL}
    
{Fore.GREEN}╔════════════════════════════════════════════════════════════════════════╗
║                    AI-Powered Facts Generation System                    ║
╠════════════════════════════════════════════════════════════════════════╣
║  [{Fore.CYAN}1{Fore.GREEN}] Generate Facts About a Topic                                        ║
║  [{Fore.CYAN}2{Fore.GREEN}] View Previous Facts Statistics                                      ║
║  [{Fore.CYAN}3{Fore.GREEN}] Exit                                                               ║
╚════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print_typing_effect(logo, delay=0.001)

# Update the main block to include loading animation
if __name__ == "__main__":
    print(f"{Fore.CYAN}[*] Initializing Pay-to-Win Cards AI...{Style.RESET_ALL}")
    display_loading_animation("Loading system modules", 2)
    generator = FactsGenerator()
    
    while True:
        display_menu()
        choice = input(f"{Fore.CYAN}[?] Enter your choice (1-3):{Style.RESET_ALL} ")
        
        if choice == '1':
            generator.run()
        elif choice == '2':
            display_loading_animation("Analyzing fact files", 1)
            facts_stats = generator.count_existing_facts()
            if not facts_stats:
                print(f"\n{Fore.YELLOW}[!] No fact files found!{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.GREEN}=== Facts Statistics ==={Style.RESET_ALL}")
                print(f"{Fore.CYAN}Topic".ljust(30) + "Facts Count".ljust(15) + f"Filename{Style.RESET_ALL}")
                print("-" * 60)
                for topic, count, filename in facts_stats:
                    print(f"{topic[:28].ljust(30)}{str(count).ljust(15)}{filename}")
                print("-" * 60)
                total_facts = sum(count for _, count, _ in facts_stats)
                print(f"{Fore.GREEN}Total facts generated: {total_facts}{Style.RESET_ALL}")
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        elif choice == '3':
            print(f"\n{Fore.GREEN}[+] Thank you for using Pay-to-Win Cards AI. Goodbye!{Style.RESET_ALL}")
            break2
        else:
            print(f"\n{Fore.RED}[-] Invalid choice! Please try again.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
