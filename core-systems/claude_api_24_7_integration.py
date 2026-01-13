#!/usr/bin/env python3
"""
CLAUDE API 24/7 INTEGRATION - REAL IMPLEMENTATION
==================================================
Connects Agent X5 to Claude API for continuous operation
Uses REAL Anthropic API key from environment
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import json

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from anthropic import Anthropic, AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("⚠️  anthropic package not installed. Run: pip install anthropic")

from dotenv import load_dotenv

# Load environment
load_dotenv(Path(__file__).parent.parent / 'config' / '.env')
load_dotenv()  # Also try from current directory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('ClaudeAPI24x7')


class ClaudeAPI247:
    """
    24/7 Claude API Integration for Agent X5
    REAL implementation using Anthropic API
    """

    def __init__(self):
        """
        Initialize the Claude API integration by loading configuration, validating the environment, and creating client instances if possible.
        
        Reads the ANTHROPIC_API_KEY environment variable and validates it; if the key is missing, invalid, or the Anthropic package is unavailable, the synchronous and asynchronous client attributes are set to None and appropriate log messages are emitted. When initialization succeeds, both synchronous and asynchronous Anthropic clients are created. Also sets the default model, max token limit, and initializes an empty conversation history.
        """
        self.api_key = os.getenv('ANTHROPIC_API_KEY', '')

        if not self.api_key or self.api_key.startswith('your_'):
            logger.error("❌ ANTHROPIC_API_KEY not configured in .env file")
            logger.info("Please add your API key to config/.env:")
            logger.info("ANTHROPIC_API_KEY=sk-ant-api03-...")
            self.client = None
            self.async_client = None
        elif not ANTHROPIC_AVAILABLE:
            logger.error("❌ anthropic package not installed")
            self.client = None
            self.async_client = None
        else:
            try:
                self.client = Anthropic(api_key=self.api_key)
                self.async_client = AsyncAnthropic(api_key=self.api_key)
                logger.info("✅ Claude API initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Claude API: {e}")
                self.client = None
                self.async_client = None

        self.model = "claude-3-5-sonnet-20241022"  # Latest production model
        self.max_tokens = 4096
        self.conversation_history: List[Dict] = []

    def is_available(self) -> bool:
        """
        Return whether both the synchronous and asynchronous Anthropic clients are initialized.
        
        Returns:
            True if both sync and async clients are initialized, False otherwise.
        """
        return self.client is not None and self.async_client is not None

    async def analyze_task(self, task_description: str, context: Dict = None) -> Dict[str, Any]:
        """
        Produce a structured JSON analysis of a task tailored for Agent X5.0.
        
        Parameters:
            task_description (str): Natural-language description of the task to analyze.
            context (Dict, optional): Additional contextual data to include in the prompt; will be JSON-serialized and sent to the model.
        
        Returns:
            Dict[str, Any]: On success, a dictionary containing the parsed analysis (the model's JSON fields), plus metadata keys:
                - `timestamp`: ISO 8601 timestamp when the analysis was produced.
                - `model_used`: model identifier used for the request.
                - `tokens_used`: total tokens consumed (input + output).
                If the model response could not be parsed as JSON, the analysis text is provided under the `analysis` key.
                On failure or if the API is unavailable, returns a dictionary containing an `error` key (and may include a `suggestion` key when the API key is missing).
        """
        if not self.is_available():
            return {
                "error": "Claude API not available",
                "suggestion": "Please configure ANTHROPIC_API_KEY in .env"
            }

        try:
            # Build prompt
            prompt = f"""Analyze this task for Agent X5.0 (219-agent orchestration system):

TASK: {task_description}

CONTEXT: {json.dumps(context, indent=2) if context else 'None provided'}

Provide:
1. Task breakdown (specific steps)
2. Which agents/divisions should handle it
3. Estimated complexity (low/medium/high)
4. Potential risks or issues
5. Success criteria

Format as JSON."""

            logger.info(f"📤 Sending task to Claude API...")

            response = await self.async_client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            content = response.content[0].text
            logger.info(f"📥 Received response from Claude API ({len(content)} chars)")

            # Try to parse as JSON, fallback to text
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                result = {"analysis": content}

            result["timestamp"] = datetime.now().isoformat()
            result["model_used"] = self.model
            result["tokens_used"] = response.usage.input_tokens + response.usage.output_tokens

            return result

        except Exception as e:
            logger.error(f"❌ Error calling Claude API: {e}")
            return {"error": str(e)}

    async def agent_conversation(
        self,
        message: str,
        agent_id: int = None,
        maintain_context: bool = True
    ) -> str:
        """
        Start a context-aware conversation with Claude acting as an agent within Agent X5.0.
        
        Parameters:
            message (str): The message to send to Claude.
            agent_id (int, optional): Agent identifier to include in the system context; if omitted, 'Master CFO' is used.
            maintain_context (bool, optional): If True, append this exchange to in-memory conversation history (history is trimmed to the most recent 20 messages).
        
        Returns:
            str: Claude's reply text, or an error string beginning with "ERROR:" if the API is unavailable or an exception occurs.
        """
        if not self.is_available():
            return "ERROR: Claude API not available. Please configure ANTHROPIC_API_KEY."

        try:
            # Build messages with context
            messages = []

            if maintain_context and self.conversation_history:
                messages.extend(self.conversation_history)

            # Add system context
            system_prompt = f"""You are Claude, integrated with Agent X5.0 - a 219-agent orchestration system.
Current agent: Agent #{agent_id or 'Master CFO'}
Your role: Provide expert analysis, task breakdown, and intelligent decision-making.
Keep responses concise and actionable."""

            messages.append({
                "role": "user",
                "content": message
            })

            logger.info(f"💬 Agent conversation (Agent #{agent_id or 'Master'})...")

            response = await self.async_client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=messages
            )

            reply = response.content[0].text

            # Update conversation history
            if maintain_context:
                self.conversation_history.append({
                    "role": "user",
                    "content": message
                })
                self.conversation_history.append({
                    "role": "assistant",
                    "content": reply
                })

                # Keep only last 10 exchanges
                if len(self.conversation_history) > 20:
                    self.conversation_history = self.conversation_history[-20:]

            logger.info(f"✅ Response received ({len(reply)} chars)")
            return reply

        except Exception as e:
            logger.error(f"❌ Conversation error: {e}")
            return f"ERROR: {str(e)}"

    def clear_conversation_history(self):
        """
        Clear the in-memory conversation history used for agent conversations.
        
        Also logs that the conversation history was cleared.
        """
        self.conversation_history = []
        logger.info("🗑️  Conversation history cleared")

    async def batch_analyze(self, tasks: List[str]) -> List[Dict]:
        """
        Analyze a list of task descriptions concurrently and return their analyses.
        
        Parameters:
            tasks (List[str]): Task description strings to analyze.
        
        Returns:
            List[Dict]: A list where each element is the analysis result dictionary corresponding to the input task at the same index. If the Claude API is unavailable, returns an error dictionary for each task (e.g., `{"error": "Claude API not available"}`).
        """
        if not self.is_available():
            return [{"error": "Claude API not available"} for _ in tasks]

        logger.info(f"📊 Batch analyzing {len(tasks)} tasks...")

        # Run all analyses in parallel
        results = await asyncio.gather(*[
            self.analyze_task(task) for task in tasks
        ])

        logger.info(f"✅ Batch analysis complete")
        return results

    async def continuous_monitoring(self, check_interval: int = 300):
        """
        Run a perpetual monitoring loop that periodically checks system health using the configured Claude API client.
        
        Parameters:
            check_interval (int): Seconds to wait between health checks (default: 300).
        
        Behavior:
            - Logs each monitoring iteration and a short excerpt of the status response.
            - Stops cleanly on KeyboardInterrupt.
            - On unexpected errors, logs the exception, waits 60 seconds, and then continues.
        """
        if not self.is_available():
            logger.error("❌ Cannot start monitoring - Claude API not available")
            return

        logger.info("🔄 Starting 24/7 continuous monitoring...")
        logger.info(f"Check interval: {check_interval} seconds ({check_interval/60:.1f} minutes)")

        iteration = 0
        while True:
            try:
                iteration += 1
                logger.info(f"\n{'='*70}")
                logger.info(f"🔍 Monitoring iteration #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"{'='*70}\n")

                # Check system status
                status_check = await self.agent_conversation(
                    "Quick system health check: Any issues with Agent X5.0?",
                    agent_id=1,  # Master CFO
                    maintain_context=False
                )

                logger.info(f"Status: {status_check[:200]}...")

                # Sleep until next check
                logger.info(f"💤 Sleeping for {check_interval} seconds...")
                await asyncio.sleep(check_interval)

            except KeyboardInterrupt:
                logger.info("\n⚠️  Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                logger.info("⏸️  Waiting 60 seconds before retry...")
                await asyncio.sleep(60)


class ClaudeTaskRouter:
    """Routes tasks to appropriate Claude API instances"""

    def __init__(self):
        """
        Initialize a task router with a Claude API client, an empty task queue, and an empty results store.
        
        Attributes:
            claude: Instance of ClaudeAPI247 used to analyze and converse with Claude.
            task_queue (List[Dict]): Pending tasks to be processed.
            results (Dict[str, Any]): Mapping of task IDs to analysis results.
        """
        self.claude = ClaudeAPI247()
        self.task_queue: List[Dict] = []
        self.results: Dict[str, Any] = {}

    async def route_task(self, task: Dict) -> Dict:
        """
        Route a single task to Claude for analysis, store the analysis in the router results, and return the aggregated result.
        
        Parameters:
            task (dict): Task data. Expected keys:
                - 'id' (str, optional): Unique task identifier; generated if missing.
                - 'description' (str): Text describing the task to analyze.
                - 'context' (dict, optional): Additional context passed to the analyzer.
        
        Returns:
            dict: Aggregated routing result with the following keys:
                - 'task_id' (str): Resolved task identifier.
                - 'original_task' (dict): The input task dictionary.
                - 'claude_analysis' (dict): Analysis result returned by Claude.
                - 'timestamp' (str): ISO-formatted timestamp when the result was produced.
        """
        task_id = task.get('id', f"task_{len(self.task_queue)}")
        description = task.get('description', '')
        context = task.get('context', {})

        logger.info(f"🎯 Routing task: {task_id}")

        # Analyze with Claude
        analysis = await self.claude.analyze_task(description, context)

        result = {
            "task_id": task_id,
            "original_task": task,
            "claude_analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }

        # Store result
        self.results[task_id] = result

        return result

    async def process_queue(self):
        """
        Process and route all tasks currently in the queue.
        
        Routes each queued task via the router, collects their results, stores results in self.results, and clears the queue.
        
        Returns:
            results (List[Dict]): A list of result dictionaries corresponding to each processed task.
        """
        if not self.task_queue:
            logger.info("📭 Task queue is empty")
            return []

        logger.info(f"📬 Processing {len(self.task_queue)} tasks...")

        results = await asyncio.gather(*[
            self.route_task(task) for task in self.task_queue
        ])

        # Clear queue after processing
        self.task_queue = []

        return results


# ========================================
# CLI INTERFACE
# ========================================

async def main():
    """
    Run a demo CLI that verifies Claude API availability, performs sample interactions, and returns an exit code.
    
    Performs a readiness check for the Claude (Anthropic) API, prints setup guidance if unavailable, executes a test conversational exchange, runs an example task analysis, and demonstrates one iteration of the 24/7 monitoring workflow for demonstration purposes.
    
    Returns:
        exit_code (int): `0` on successful demo completion, `1` if the Claude API is not available or not configured.
    """
    print("\n" + "="*70)
    print("🤖 CLAUDE API 24/7 INTEGRATION - Agent X5.0")
    print("="*70 + "\n")

    claude = ClaudeAPI247()

    if not claude.is_available():
        print("❌ Claude API is not available")
        print("\nSetup instructions:")
        print("1. Get API key from: https://console.anthropic.com/")
        print("2. Add to config/.env: ANTHROPIC_API_KEY=sk-ant-api03-...")
        print("3. Install package: pip install anthropic")
        return 1

    print("✅ Claude API is ready!\n")

    # Test conversation
    print("🧪 Testing API connection...\n")
    response = await claude.agent_conversation(
        "Hello! Confirm you're connected to Agent X5.0 and ready for 24/7 operation.",
        agent_id=1
    )
    print(f"Claude: {response}\n")

    # Example task analysis
    print("\n" + "="*70)
    print("📋 Example: Task Analysis")
    print("="*70 + "\n")

    task = "Set up automated trading for BTC/USDT with paper trading mode"
    analysis = await claude.analyze_task(task, {
        "system": "Agent X5.0",
        "available_agents": "30 trading agents (IDs 82-111)",
        "current_mode": "PAPER"
    })

    print(f"Analysis:\n{json.dumps(analysis, indent=2)}\n")

    # Demonstrate 24/7 monitoring (just one iteration for demo)
    print("\n" + "="*70)
    print("🔄 24/7 Monitoring Demo (1 iteration)")
    print("="*70 + "\n")
    print("(In production, this runs continuously)")
    print("Checking system health...\n")

    status = await claude.agent_conversation(
        "System status check for Agent X5.0",
        agent_id=1,
        maintain_context=False
    )
    print(f"Status: {status}\n")

    print("="*70)
    print("✅ Claude API 24/7 Integration Test Complete")
    print("="*70 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))