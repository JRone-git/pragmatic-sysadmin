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
            and be exactly适合 the target duration. Break the script into 
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
                        "prompt": f"<|im_start|>system\n{system_prompt}\n<|im_end|>\n<|im_start|>user\n{user_prompt}\n<|im_end|>",
                        "stream": False,
                        "options": {
                            "num_predict": 1024,
                            "temperature": 0.7,
                            "top