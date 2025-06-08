"""
LLM integration module for ASB.
This module handles communication with language models for content filtering and analysis using the agents library.
"""
import json
import logging
import os
from typing import List, Dict, Optional, Any
import asyncio

# Agents library imports
from openai import AsyncOpenAI
from agents import Agent, Runner, set_tracing_disabled, RunConfig, ModelProvider, OpenAIChatCompletionsModel, Model

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("llm_processor")

# Default API endpoint and keys - override with environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "your_openai_api_key_here")
OPENAI_API_ENDPOINT = os.environ.get("OPENAI_API_ENDPOINT", "https://openrouter.ai/api/v1")
LLM_MODEL = os.environ.get("LLM_MODEL", "google/gemini-2.0-flash-exp:free")

# Set up custom OpenAI client with OpenRouter
custom_client = AsyncOpenAI(base_url=OPENAI_API_ENDPOINT, api_key=OPENAI_API_KEY)
set_tracing_disabled(disabled=True)

# Create a custom model provider to use with the agent
class CustomModelProvider(ModelProvider):
    def get_model(self, model_name: str | None) -> Model:
        # If a specific model is requested, use that
        if model_name is not None:
            logger.info(f"Using specified model: {model_name}")
            return OpenAIChatCompletionsModel(model=model_name, openai_client=custom_client)
        
        # Otherwise fall back to the default model
        logger.info(f"No model specified, using default model: {LLM_MODEL}")
        return OpenAIChatCompletionsModel(model=LLM_MODEL, openai_client=custom_client)

class LLMProcessor:
    """Class for handling LLM-based processing and filtering using agents library."""
    
    def __init__(self, api_key=None, api_base=None, model=None):
        """Initialize the LLM processor with API credentials."""
        self.api_key = api_key or OPENAI_API_KEY
        self.api_base = api_base or OPENAI_API_ENDPOINT
        self.model = model or LLM_MODEL
        
        # Set up custom OpenAI client
        self.custom_client = AsyncOpenAI(
            base_url=self.api_base,
            api_key=self.api_key
        )
        
        # Create custom model provider
        self.model_provider = CustomModelProvider()
        
        # Create the LinkedIn profile parser agent
        self.linkedin_parser_agent = Agent(
            name="LinkedInProfileParserAgent",
            model=self.model,
            instructions="""You are an AI assistant specialized in parsing LinkedIn profile information.
      Your task is to extract structured data from profile content and convert it into a standardized JSON format.

      IMPORTANT RULES:
      - Extract all available information from the provided LinkedIn profile content
      - Make educated guesses for fields when information is implicit but not explicit
      - Use null or empty string for fields where information is not available
      - Return your response AS A JSON object with the exact structure shown below:

      {
        "Name": "Full name of the person",
        "Gender": "Gender if can be determined, else guess and assumed the gender (Male or Female)",
        "Profile Image": "URL of the profile image if available",
        "Location": "Location of the person, e.g. 'San Francisco, CA'",
        "Headline": "Current headline or job title",
        "About": "Summary or about section content",
        "Activity Posts": "Recent activity posts if available, else null",
        "Current Position": "Current job title",
        "Current Company": "Name of current employer", 
        "Current Company Duration": "Duration at current company",
        "Education": ["List of education institutions"],
        "Education URLs": ["List of education institution URLs"],
        "Degrees": ["List of degrees obtained"],
        "Connection Count": "Number of LinkedIn connections",
        "Languages": ["List of languages spoken"],
        "Skills": ["List of professional skills"],
        "Websites": ["List of personal/professional websites"],
        "Contact Phone": "Phone number if available",
        "Contact Email": "Email address",
        "Contact Twitter": "Twitter/X handle",
        "Birthday": "Birthday if available, don't assumed",
        "Position Level": "Whether they are C-level, Junior, Senior, others"
      }

      Be thorough but do not invent information that is not directly stated or strongly implied in the profile content."""
        )
    
    async def parse_linkedin_profile(self, profile_data: str) -> Dict:
        """
        Parse LinkedIn profile information into a structured format.
        
        Args:
            profile_data: HTML or text data from a LinkedIn profile
            
        Returns:
            A dictionary with structured profile information
        """
        if not profile_data:
            logger.warning("Empty profile data provided")
            return {}
            
        try:
            # Create the prompt
            prompt = f"""Please analyze this LinkedIn profile information and extract the requested details into JSON format:

{profile_data}
"""
            
            # Run the agent
            logger.info("Sending profile data to LLM for parsing")
            result = await Runner.run(
                self.linkedin_parser_agent, 
                prompt, 
                run_config=RunConfig(model_provider=self.model_provider)
            )
            
            response_content = result.final_output
            logger.debug(f"Received response from LLM: {response_content[:100]}...")
            
            # Try to parse as JSON
            try:
                # Handle cases where the model outputs text before/after the JSON
                response_content = response_content.strip()
                start_idx = response_content.find('{')
                end_idx = response_content.rfind('}') + 1
                
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response_content[start_idx:end_idx]
                    profile_info = json.loads(json_str)
                    
                    # Ensure we got a properly structured response
                    if isinstance(profile_info, dict):
                        logger.info(f"Successfully parsed LinkedIn profile information")
                        
                        return profile_info
                
                logger.warning(f"Failed to parse LLM LinkedIn profile response: {response_content[:200]}")
                return {"error": "Failed to parse profile data", "raw_text": profile_data[:500]}
                
            except json.JSONDecodeError as json_err:
                logger.warning(f"Failed to parse LLM LinkedIn profile response as JSON: {str(json_err)}")
                return {"error": f"JSON decode error: {str(json_err)}", "raw_text": profile_data[:500]}
                
        except Exception as e:
            logger.error(f"Error in LLM LinkedIn profile parsing: {str(e)}")
            return {"error": f"Processing error: {str(e)}", "raw_text": profile_data[:500]}

# Initialize a shared LLM processor
_llm_processor = None

def get_llm_processor() -> LLMProcessor:
    """Get or create an LLM processor instance."""
    global _llm_processor
    if _llm_processor is None:
        _llm_processor = LLMProcessor()
    return _llm_processor

async def parse_linkedin_profile(profile_data: str) -> Dict:
    """Parse LinkedIn profile information into a structured format."""
    processor = get_llm_processor()
    return await processor.parse_linkedin_profile(profile_data)
