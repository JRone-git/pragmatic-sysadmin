#!/usr/bin/env python3
"""
Ollama Client for Local LLM Processing
Interacts with local Ollama instance for script generation
"""

import os
import json
import asyncio
import logging
from typing import Optional, List, Dict, Any
import aiohttp

logger = logging.getLogger("ollama-client")

class OllamaClient:
    def __init__(
        self, 
        base_url: str = "http://localhost:11434",
        model_name: str = "llama3.1:8b-q4_K_M",
        context_size: int = 4096
    ):
        self.base_url = base_url
        self.model_name = model_name
        self.context_size = context_size
        self.session = None
        self.is_model_loaded = False
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models from Ollama"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("models", [])
        except Exception as e:
            logger.error(f"Failed to list models: {str(e)}")
            return []
        return []
    
    async def load_model(self, model_name: str = None) -> bool:
        """Load model into VRAM"""
        try:
            if model_name:
                self.model_name = model_name
            
            # Create a simple request to load the model
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": "A",
                        "stream": False,
                        "options": {"num_predict": 1}
                    }
                ) as response:
                    if response.status == 200:
                        self.is_model_loaded = True
                        logger.info(f"Model loaded: {self.model_name}")
                        return True
                    else:
                        self.is_model_loaded = False
                        return False
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            self.is_model_loaded = False
            return False
    
    def unload_model(self) -> bool:
        """Unload model from VRAM"""
        try:
            # For Ollama, model unloading happens automatically
            # but we can clear our state
            self.is_model_loaded = False
            logger.info(f"Model unloaded: {self.model_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to unload model: {str(e)}")
            return False
    
    async def generate_script(self, request) -> Dict[str, Any]:
        """Generate script from topic"""
        try:
            if not self.is_model_loaded:
                await self.load_model()
            
            # Create system prompt for script generation
            system_prompt = """
            You are a scriptwriter for engaging YouTube Shorts and TikTok videos.
            Your scripts should be conversational, highlight the main point quickly, 
            and be exactly suited for the target duration. Break the script into 
            clear scenes with visual suggestions.
            """
            
            # Create user prompt
            user_prompt = f"""
            Write a script for a {request.target_duration_seconds}-second vertical short about "{request.topic}".
            
            Requirements:
            - Tone: {request.tone}
            - Style: {request.style}
            - Target duration: {request.target_duration_seconds} seconds
            - Include 3-5 scenes with visual suggestions
            - Total word count: ~{request.target_duration_seconds * 3} words
            
            Format the output as JSON with:
            - title: Brief title for the video
            - scenes: Array of scenes, each with:
              - duration: seconds
              - visual: description of what to show
              - voiceover: what to say
            - hashtags: 3-5 relevant hashtags
            """
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": f"system\n{system_prompt}\nuser\n{user_prompt}\nassistant\n",
                        "stream": False,
                        "options": {
                            "num_predict": 1024,
                            "temperature": 0.7,
                            "top_k": 40,
                            "top_p": 0.9
                        }
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response", "")
                        
                        # Try to extract JSON from response
                        try:
                            # Attempt to parse the response as JSON
                            script_data = json.loads(response_text)
                        except json.JSONDecodeError:
                            # If that fails, try to find JSON in the response
                            json_start = response_text.find('{')
                            json_end = response_text.rfind('}') + 1
                            if json_start >= 0 and json_end > json_start:
                                script_data = json.loads(response_text[json_start:json_end])
                            else:
                                # Fallback: create a basic structure
                                script_data = {
                                    "title": request.topic,
                                    "scenes": [
                                        {
                                            "duration": request.target_duration_seconds,
                                            "visual": "Text overlay with main topic",
                                            "voiceover": response_text
                                        }
                                    ],
                                    "hashtags": ["#viral", "#trending", "#shorts"]
                                }
                        
                        return script_data
                    else:
                        raise Exception(f"Ollama API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Script generation failed: {str(e)}")
            raise

    async def refine_script(self, request) -> Dict[str, Any]:
        """Refine an existing script based on adjustments"""
        try:
            if not self.is_model_loaded:
                await self.load_model()
            
            # Create system prompt
            system_prompt = """
            You are a script editor. Refine existing scripts based on specific adjustments
            while maintaining the core message and engagement quality.
            """
            
            # Create user prompt
            adjustment_list = "\n".join(f"- {adj}" for adj in request.adjustments)
            user_prompt = f"""
            Refine the following script based on these adjustments:
            
            {adjustment_list}
            
            Original script:
            {request.script}
            
            Requirements:
            - Maintain the total duration target
            - Keep the core message intact
            - Apply the requested adjustments
            - Output as the same JSON format as before
            """
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": f"system\n{system_prompt}\nuser\n{user_prompt}\nassistant\n",
                        "stream": False,
                        "options": {
                            "num_predict": 1024,
                            "temperature": 0.5,
                            "top_k": 30,
                            "top_p": 0.85
                        }
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response", "")
                        
                        # Try to parse JSON response
                        try:
                            refined_data = json.loads(response_text)
                        except json.JSONDecodeError:
                            # Fallback parsing
                            json_start = response_text.find('{')
                            json_end = response_text.rfind('}') + 1
                            if json_start >= 0 and json_end > json_start:
                                refined_data = json.loads(response_text[json_start:json_end])
                            else:
                                refined_data = json.loads(request.script)
                                refined_data["refined"] = True
                        
                        return refined_data
                    else:
                        raise Exception(f"Ollama API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Script refinement failed: {str(e)}")
            raise

    async def generate_scene_breakdown(self, script: str) -> List[Dict[str, Any]]:
        """Generate scene breakdown from script"""
        try:
            if not self.is_model_loaded:
                await self.load_model()
            
            user_prompt = f"""
            Break down the following script into detailed scenes for video production:
            
            {script}
            
            Output as JSON array with:
            - scene_number: integer
            - start_time: seconds
            - end_time: seconds
            - visual_description: detailed description for video clips
            - audio_description: voiceover and sound effects
            - suggested_music: music mood (optional)
            """
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": f"user\n{user_prompt}\nassistant\n",
                        "stream": False,
                        "options": {
                            "num_predict": 2048,
                            "temperature": 0.6
                        }
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get("response", "")
                        
                        try:
                            scenes = json.loads(response_text)
                            return scenes
                        except json.JSONDecodeError:
                            return []
                    else:
                        return []
        
        except Exception as e:
            logger.error(f"Scene breakdown failed: {str(e)}")
            return []#!/usr/bin/env python3
"""
Ollama Client for Local LLM Processing
Interacts with local Ollama instance for script generation
"""

import os
import json
import asyncio
import logging
from typing import Optional, List, Dict, Any
import requests
import aiohttp

logger = logging.getLogger("ollama-client")

class OllamaClient:
    def __init__(
        self, 
        base_url: str = "http://localhost:11434",
        model_name: str = "llama3.1:8b-q4_K_M",
        context_size: int = 4096
    ):
        self.base_url = base_url
        self.model_name = model_name
        self.context_size = context_size
        self.session = None
        self.is_model_loaded = False
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models from Ollama"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("models", [])
        except Exception as e:
            logger.error(f"Failed to list models: {str(e)}")
            return []
        return []
    
    async def load_model(self, model_name: str = None) -> bool:
        """Load model into VRAM"""
        try:
            if model_name:
                self.model_name = model_name
            
            # Create a simple request to load the model
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": "A",
                        "stream": False,
                        "options": {"num_predict": 1}
                    }
                ) as response:
                    if response.status == 200:
                        self.is_model_loaded = True
                        logger.info(f"Model loaded: {self.model_name}")
                        return True
                    else:
                        self.is_model_loaded = False
                        return False
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            self.is_model_loaded = False
            return False
    
    def unload_model(self) -> bool:
        """Unload model from VRAM"""
        try:
            # For Ollama, model unloading happens automatically
            # but we can clear our state
            self.is_model_loaded = False
            logger.info(f"Model unloaded: {self.model_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to unload model: {str(e)}")
            return False
    
    async def generate_script(self, request) -> str:
        """Generate script from topic"""
        try:
            if not self.is_model_loaded:
                await self.load_model()
            
            # Create system prompt for script generation
            system_prompt = """
            You are a scriptwriter for engaging YouTube Shorts and TikTok videos.
            Your scripts should be conversational, highlight the main point quickly, 
            and be exactly suitable for the target duration. Break the script into 
            clear scenes with visual suggestions.
            """
            
            # Create user prompt
            user_prompt = f"""
            Write a script for a {request.target_duration_seconds}-second vertical short about "{request.topic}".
            
            Requirements:
            - Tone: {request.tone}
            - Style: {request.style}
            - Target duration: {request.target_duration_seconds} seconds
            - Include 3-5 scenes with visual suggestions
            - Total word count: ~{request.target_duration_seconds * 3} words
            
            Format the output as JSON with:
            - title: Brief title for the video
            - scenes: Array of scenes, each with:
              - duration: seconds
              - visual: description of what to show
              - voiceover: what to say
            - hashtags: 3-5 relevant hashtags
            """
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": f"User: {user_prompt}",
                        "stream": False,
                        "options": {
                            "num_predict": 1024,
                            "temperature": 0.7,
                            "top_k": 40,
                            "top_p": 0.9
                        }
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "")
                    else:
                        raise Exception(f"Ollama API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Script generation failed: {str(e)}")
            raise
    
    async def refine_script(self, request) -> str:
        """Refine existing script based on adjustments"""
        try:
            if not self.is_model_loaded:
                await self.load_model()
            
            # Create system prompt
            system_prompt = """
            You are an expert script editor for short-form video content.
            Refine scripts to meet specific duration and style requirements.
            """
            
            # Create user prompt
            adjustment_list = "\n".join([f"- {adj}" for adj in request.adjustments])
            user_prompt = f"""
            Refine this script based on the following adjustments:
            
            {adjustment_list}
            
            Current script:
            {request.script}
            
            Keep the total duration approximately {request.target_duration_seconds} seconds.
            Maintain the engaging tone and clear scene structure.
            """
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": f"User: {user_prompt}",
                        "stream": False,
                        "options": {
                            "num_predict": 1024,
                            "temperature": 0.5,
                            "top_k": 40,
                            "top_p": 0.9
                        }
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "")
                    else:
                        raise Exception(f"Ollama API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Script refinement failed: {str(e)}")
            raise
    
    async def generate_scene_breakdown(self, script: str) -> Dict[str, Any]:
        """Generate detailed scene breakdown from script"""
        try:
            if not self.is_model_loaded:
                await self.load_model()
            
            user_prompt = f"""
            Break down this script into detailed scenes for video production:
            
            {script}
            
            For each scene, provide:
            - Duration in seconds
            - Visual description (what to show on screen)
            - Voiceover text
            - Recommended transition type
            """
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": f"User: {user_prompt}",
                        "stream": False,
                        "options": {
                            "num_predict": 1024,
                            "temperature": 0.6
                        }
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {"scenes": json.loads(result.get("response", "{}"))}
                    else:
                        raise Exception(f"Ollama API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Scene breakdown failed: {str(e)}")
            raise
