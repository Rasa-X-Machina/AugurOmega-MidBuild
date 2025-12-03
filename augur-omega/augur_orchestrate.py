#!/usr/bin/env python3
"""
Augur Omega: AI-Native Parallel Orchestrator
Optimized for Hybrid Architecture:
- Local CPU (32GB RAM): Handles SENSITIVE Prime Koshas (Sequential)
- Groq Cloud (Free Tier): Handles BULK Microagents (Parallel)
Path: C:/Users/Dell/Rasa-X-Machina/augur-omega/
"""
import os
from dotenv import load_dotenv
load_dotenv()
import sys
import os
import sys
import logging
import re
import ast
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import aiohttp
from dataclasses import dataclass

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = Path.home() / "Rasa-X-Machina" / "augur-omega"

# 1. Local Config (The Sovereign Vault)
LOCAL_LLM_ENDPOINT = os.getenv("LOCAL_LLM_ENDPOINT", "http://localhost:1234/v1") 
MAX_LOCAL_CONCURRENCY = 1  # CPU Limit: One at a time

# 2. Cloud Config (The Factory Floor)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
GROQ_MODEL = "llama-3.1-70b-versatile"
MAX_GROQ_CONCURRENCY = 10 # Rate Limit: Run 10 at a time
KILOCODE_API_TOKEN = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbnYiOiJwcm9kdWN0aW9uIiwia2lsb1VzZXJJZCI6Im9hdXRoL2dvb2dsZToxMTUyMDU4MDc5ODg0MzA3NDMwMzMiLCJhcGlUb2tlblBlcHBlciI6bnVsbCwidmVyc2lvbiI6MywiaWF0IjoxNzYxMTU1MzUwLCJleHAiOjE5MTg5NDMzNTB9.xifNTLMSzlT3U5zkVmDW8nMiND6aY_vfyIAM-Jyfa_I")


# ============================================================================
# LOGGING
# ============================================================================

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f"orchestrator_{datetime.now():%Y%m%d_%H%M%S}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("AugurOrchestrator")

# ============================================================================
# AI PROVIDER CLASSES
# ============================================================================

@dataclass
class AIResponse:
    success: bool
    code: str
    provider: str
    tokens_used: int = 0
    error: Optional[str] = None

class LocalServerProvider:
    """Handles Sensitive Tasks on Local CPU"""
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.semaphore = asyncio.Semaphore(MAX_LOCAL_CONCURRENCY)
    
    async def generate(self, prompt: str) -> AIResponse:
        async with self.semaphore:
            try:
                logger.info(f"🔒 [Local-CPU] Processing Sensitive Task...")
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.endpoint}/chat/completions",
                        json={
                            "model": "local-model", # Uses loaded CodeGeeX4
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": 0.1,
                            "max_tokens": 4096,
                            "stream": False
                        },
                        timeout=aiohttp.ClientTimeout(total=900)
                    ) as response:
                        response.raise_for_status()
                        data = await response.json()
                        code = data["choices"][0]["message"]["content"]
                        tokens = data.get("usage", {}).get("total_tokens", 0)
                        logger.info(f"✅ [Local-CPU] Complete ({tokens} tokens)")
                        return AIResponse(True, code, "local-cpu", tokens)
            except Exception as e:
                logger.error(f"Local Server error: {e}")
                return AIResponse(False, "", "local-cpu", error=str(e))

class GroqProvider:
    """Handles Bulk Tasks on Cloud"""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.semaphore = asyncio.Semaphore(MAX_GROQ_CONCURRENCY)
    
    async def generate(self, prompt: str) -> AIResponse:
        if not self.api_key:
            return AIResponse(False, "", "groq", error="No API Key")
            
        async with self.semaphore:
            try:
                logger.info(f"🚀 [Groq-Cloud] Processing Bulk Task...")
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.base_url,
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        json={
                            "model": GROQ_MODEL,
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": 0.3,
                            "max_tokens": 4096
                        },
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status == 429: # Rate limit
                            logger.warning("Groq Rate Limit. Retrying...")
                            await asyncio.sleep(5)
                            return AIResponse(False, "", "groq", error="Rate Limit")
                            
                        response.raise_for_status()
                        data = await response.json()
                        code = data["choices"][0]["message"]["content"]
                        tokens = data.get("usage", {}).get("total_tokens", 0)
                        logger.info(f"⚡ [Groq-Cloud] Complete ({tokens} tokens)")
                        return AIResponse(True, code, "groq-cloud", tokens)
            except Exception as e:
                logger.error(f"Groq error: {e}")
                return AIResponse(False, "", "groq", error=str(e))

# ============================================================================
# ORCHESTRATION & ROUTING
# ============================================================================

class AIOrchestrator:
    def __init__(self):
        self.local = LocalServerProvider(LOCAL_LLM_ENDPOINT)
        self.groq = GroqProvider(GROQ_API_KEY)
    
    async def generate_code(self, prompt: str, is_sensitive: bool = False) -> AIResponse:
        # STRATEGY: Hybrid Routing
        
        # 1. If Sensitive (Prime Kosha) -> MUST use Local
        if is_sensitive:
            return await self.local.generate(prompt)
            
        # 2. If Bulk (Micro/Domain) -> Try Groq first for speed
        if GROQ_API_KEY:
            response = await self.groq.generate(prompt)
            if response.success:
                return response
            else:
                logger.warning("Groq failed, falling back to Local CPU...")
        
        # 3. Fallback -> Local CPU
        return await self.local.generate(prompt)

def clean_and_validate_code(raw_response: str) -> Tuple[Optional[str], Optional[str]]:
    pattern = r"```(?:python)?(.*?)```"
    match = re.search(pattern, raw_response, re.DOTALL)
    if match:
        clean_code = match.group(1).strip()
    else:
        clean_code = raw_response.strip()
        clean_code = re.sub(r"^(Here is|Sure|Below is).+?:\n", "", clean_code, flags=re.IGNORECASE)

    try:
        ast.parse(clean_code)
        return clean_code, None
    except SyntaxError as e:
        return None, f"SyntaxError at line {e.lineno}: {e.msg}"
    except Exception as e:
        return None, str(e)

async def generate_kosha_code(kosha_path: Path, orchestrator: AIOrchestrator, attempt: int = 1) -> bool:
    if attempt > 3: return False

    try:
        with open(kosha_path, "r") as f: scaffold = f.read()
        
        # INTELLIGENT ROUTING TRIGGER
        # Prime Koshas = Strategy/Consciousness = Sensitive = Local
        is_sensitive = "PRIME" in kosha_path.name
        
        base_prompt = f"""Task: Implement Python code for {kosha_path.name}.
SCAFFOLD:
{scaffold}
REQUIREMENTS:
1. Use 'litestar' and 'pydantic'.
2. Use async/await.
3. Output ONLY raw Python code in markdown.
"""
        if attempt > 1: base_prompt += f"\n\nFIX SYNTAX ERROR FROM PREVIOUS ATTEMPT:\n"

        response = await orchestrator.generate_code(base_prompt, is_sensitive=is_sensitive)

        if response.success:
            valid_code, error = clean_and_validate_code(response.code)
            if valid_code:
                with open(kosha_path, "w") as f: f.write(valid_code)
                return True
            else:
                logger.warning(f"⚠️ Syntax Error in {kosha_path.name}. Retrying...")
                return await generate_kosha_code(kosha_path, orchestrator, attempt + 1)
        return False

    except Exception as e:
        logger.error(f"System Error: {str(e)}")
        return False

def create_scaffold(path: Path, kosha_type: str, index: int) -> bool:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        template = f"""# {kosha_type} {index}
import logging
from litestar import Controller, get

logger = logging.getLogger(__name__)

class {kosha_type}{index}Controller(Controller):
    path = "/{kosha_type.lower()}-{index}"
    @get("/")
    async def status(self) -> dict:
        return {{"status": "active", "id": "{kosha_type}-{index}"}}
"""
        with open(path, "w") as f: f.write(template)
        return True
    except Exception: return False

# ============================================================================
# MAIN ASYNC LOOP
# ============================================================================

async def main():
    logger.info("=== Augur Omega Orchestrator v3.0 (Hybrid: Sovereign + Cloud) ===")
    if GROQ_API_KEY:
        logger.info("✅ Groq Key Detected: Bulk tasks will run on Cloud.")
    else:
        logger.warning("⚠️ No Groq Key: All tasks will run on Local CPU (Slow).")

    orchestrator = AIOrchestrator()
    (BASE_DIR / "prime_koshas").mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "domain_koshas").mkdir(parents=True, exist_ok=True)
    
    tasks = []
    
    # 1. Queue Sensitive Tasks (Local CPU - Serial)
    # These will trickle through the semaphore 1 by 1
    for i in range(1, 37):
        path = BASE_DIR / "prime_koshas" / f"PRIME_{i:03d}.py"
        if create_scaffold(path, "PrimeKosha", i):
            tasks.append(generate_kosha_code(path, orchestrator))
            
    # 2. Queue Bulk Tasks (Groq Cloud - Parallel)
    # These will blast through the semaphore 10 by 10
    for i in range(1, 145):
        path = BASE_DIR / "domain_koshas" / f"DOMAIN_{i:03d}.py"
        if create_scaffold(path, "DomainKosha", i):
            tasks.append(generate_kosha_code(path, orchestrator))
    
    logger.info(f"🚀 Launching {len(tasks)} Construction Drones...")
    await asyncio.gather(*tasks)
    logger.info("=== System Construction Complete ===")

if __name__ == "__main__":
    asyncio.run(main())