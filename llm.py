"""
LLM service for VoiceRAG
Integrates with Together AI API using Llama 3.3 70B model
"""
from typing import List, Dict, Optional
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"


class LLMService:
    """
    LLM service for generating responses using Together AI
    """

    def __init__(self):
        """Initialize LLM service"""
        if not TOGETHER_API_KEY:
            raise ValueError("TOGETHER_API_KEY not found in environment variables")

        self.api_key = TOGETHER_API_KEY
        self.api_url = TOGETHER_API_URL
        self.model = MODEL

    def build_prompt(
        self,
        query: str,
        context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """
        Build prompt messages for LLM

        Args:
            query: User query
            context: Retrieved context from RAG
            conversation_history: Previous messages (optional)

        Returns:
            List of message dictionaries
        """
        system_prompt = """You are a helpful AI assistant for VoiceRAG, a voice-powered document Q&A system. You're conversational, natural, and helpful.

Instructions:
1. **If asked about the file/document overview** (e.g., "what is this file about?", "summarize this", "what's in this document?"):
   - Provide a comprehensive summary of ALL the context provided
   - Give the user a clear overview of the main topics and key points

2. **If asked a specific question that's answered in the context**:
   - Answer directly using the context
   - Be specific and cite relevant details

3. **If asked a general question NOT in the context** (e.g., "how's the weather?", "what's 2+2?"):
   - Answer normally using your general knowledge
   - Optionally mention "This isn't in your document, but..." if relevant
   - Don't refuse to answer - be helpful!

4. **Keep responses natural and concise**:
   - You're in a voice interface, so be conversational
   - 2-5 sentences ideal (unless summarizing, then be thorough)
   - No robotic "I don't have information" responses

5. **Be smart about context**:
   - Use context when relevant
   - Answer generally when context isn't relevant
   - Always try to be helpful"""

        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history if provided (last 4 messages)
        if conversation_history:
            messages.extend(conversation_history[-4:])

        # Add current query with context
        user_message = f"""Context:
{context}

Question: {query}

Please provide a clear, concise answer based on the context above."""

        messages.append({"role": "user", "content": user_message})

        return messages

    async def generate_response(
        self,
        query: str,
        context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """
        Generate response using Together AI API

        Args:
            query: User query
            context: Retrieved context from RAG
            conversation_history: Previous messages (optional)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response

        Returns:
            Generated response text
        """
        # Build messages
        messages = self.build_prompt(query, context, conversation_history)

        # Prepare API request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1.0,
            "stop": ["<|eot_id|>", "<|eom_id|>"]
        }

        try:
            # Make API request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )

                response.raise_for_status()

                # Parse response
                result = response.json()
                generated_text = result["choices"][0]["message"]["content"]

                return generated_text.strip()

        except httpx.HTTPStatusError as e:
            error_detail = e.response.text if hasattr(e.response, 'text') else str(e)
            raise Exception(f"Together AI API error ({e.response.status_code}): {error_detail}")

        except httpx.TimeoutException:
            raise Exception("Together AI API request timed out")

        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")

    async def generate_streaming_response(
        self,
        query: str,
        context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ):
        """
        Generate streaming response using Together AI API

        Args:
            query: User query
            context: Retrieved context from RAG
            conversation_history: Previous messages (optional)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Yields:
            Response chunks as they arrive
        """
        # Build messages
        messages = self.build_prompt(query, context, conversation_history)

        # Prepare API request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1.0,
            "stop": ["<|eot_id|>", "<|eom_id|>"],
            "stream": True
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream(
                    "POST",
                    self.api_url,
                    headers=headers,
                    json=payload
                ) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]  # Remove "data: " prefix

                            if data == "[DONE]":
                                break

                            try:
                                import json
                                chunk = json.loads(data)
                                if "choices" in chunk and len(chunk["choices"]) > 0:
                                    delta = chunk["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue

        except Exception as e:
            raise Exception(f"Error in streaming response: {str(e)}")


# Global instance
llm_service = LLMService()
