import requests
import time
import random

class GeminiClient:
    def __init__(self, api_keys=None):
        self.api_keys = api_keys or []
        self.current_key_index = 0
    
    def switch_key(self):
        """
        Switch to the next available API key
        """
        if not self.api_keys:
            raise Exception("No API keys available")
        
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return self.api_keys[self.current_key_index]
    
    def get_current_key(self):
        """
        Get the current API key
        """
        if not self.api_keys:
            raise Exception("No API keys available")
        
        return self.api_keys[self.current_key_index]
    
    def send_request(self, prompt, model="gemini-1.5-flash", max_retries=5):
        """
        Send a request to the Gemini API
        """
        if not self.api_keys:
            raise Exception("No API keys available. Please add your API key.")
        
        retry_count = 0
        
        while retry_count < max_retries:
            # Set up API request
            api_key = self.get_current_key()
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 8192,
                    "stopSequences": []
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            }
            
            try:
                response = requests.post(url, headers=headers, json=data, timeout=120)
                response.raise_for_status()
                response_json = response.json()
                
                if "candidates" in response_json and len(response_json["candidates"]) > 0:
                    text = response_json["candidates"][0]["content"]["parts"][0]["text"]
                    
                    # Always rotate API key after a successful request and wait 2 seconds
                    self.switch_key()
                    time.sleep(2)
                    
                    return text
                else:
                    # No valid response, switch key and retry
                    self.switch_key()
                    time.sleep(2)
                    retry_count += 1
            
            except requests.exceptions.HTTPError as e:
                error_str = str(e)
                
                # Handle rate limiting specifically
                if "429" in error_str and "Too Many Requests" in error_str:
                    # Switch to next API key
                    self.switch_key()
                    
                    # Add exponential backoff wait time based on retry count
                    wait_time = (2 ** retry_count) * 2  # 2, 4, 8, 16, 32 seconds
                    time.sleep(wait_time)
                else:
                    # Other HTTP error, switch key and retry
                    self.switch_key()
                    time.sleep(2)
                
                retry_count += 1
            
            except Exception as e:
                # General exception, switch key and retry
                self.switch_key()
                time.sleep(2)
                retry_count += 1
        
        # If all retries failed with the current model, try with fallback model
        if model == "gemini-1.5-pro":
            return self.send_request(prompt, "gemini-1.5-flash", max_retries)
        
        # If we've exhausted all retries and even the fallback model failed
        raise Exception(f"Failed to get response after {max_retries} attempts with different API keys")