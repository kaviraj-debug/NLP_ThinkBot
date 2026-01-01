import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class ChatbotEngine:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API Key not found. Please provide one.")
            
        genai.configure(api_key=self.api_key)
        
        # Generation configuration
        generation_config = {
            "temperature": 0.7,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }
        
        # Initialize the model (using gemini-flash-lite-latest for maximum quota stability)
        self.model = genai.GenerativeModel(
            model_name="gemini-flash-lite-latest",
            generation_config=generation_config
        )
        
    def get_response(self, user_input, chat_history=[]):
        """
        Generates a response using Gemini, considering the chat history.
        """
        try:
            # Start a chat session with the provided history
            chat = self.model.start_chat(history=chat_history)
            response = chat.send_message(user_input)
            return response.text
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "quota" in err_msg.lower():
                return ("🚨 [QUOTA EXCEEDED] Your Google API key has hit its daily limit (Limit: 0). "
                        "This usually means this specific key is restricted for today. "
                        "Please try creating a NEW key at https://aistudio.google.com/app/apikey "
                        "using a DIFFERENT Google Account for a fresh quota.")
            return f"An error occurred with the AI engine: {err_msg}"

# For testing
if __name__ == "__main__":
    bot = ChatbotEngine()
    print(bot.get_response("Hello, how are you?"))
