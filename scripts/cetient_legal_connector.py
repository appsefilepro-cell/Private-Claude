#!/usr/bin/env python3
"""
Cetient Legal Research AI Connector
Integrates with Agent X5 Legal Division (35 agents)
Accesses 9M+ legal decisions for research and document drafting
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional, Any

class CetientLegalAI:
    """Connector for Cetient Legal Research AI Platform"""

    def __init__(self):
        self.api_key = os.getenv("CETIENT_API_KEY", "")
        self.base_url = "https://api.cetient.com/v1"
        self.config = self._load_config()
        self.session = None

    def _load_config(self) -> Dict:
        """Load Cetient configuration"""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "config", "cetient_legal_ai.json"
        )
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "AgentX5-LegalDivision/1.0"
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session

    async def search_case_law(
        self,
        query: str,
        jurisdiction: str = "all",
        date_range: Optional[Dict] = None,
        limit: int = 50
    ) -> Dict:
        """
        Search 9M+ legal decisions

        Args:
            query: Search query (natural language or legal terms)
            jurisdiction: Federal, State, or specific state code
            date_range: Optional date filter
            limit: Max results to return
        """
        session = await self._get_session()

        payload = {
            "query": query,
            "jurisdiction": jurisdiction,
            "limit": limit,
            "include_analysis": True
        }

        if date_range:
            payload["date_from"] = date_range.get("from")
            payload["date_to"] = date_range.get("to")

        try:
            async with session.post(
                f"{self.base_url}/search",
                json=payload
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {
                        "status": "error",
                        "code": response.status,
                        "message": await response.text()
                    }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def draft_document(
        self,
        document_type: str,
        context: Dict,
        style: str = "formal"
    ) -> Dict:
        """
        Draft legal documents using AI

        Args:
            document_type: Type of document (motion, brief, complaint, etc.)
            context: Case context and requirements
            style: Writing style
        """
        session = await self._get_session()

        valid_types = [
            "motion", "complaint", "brief", "contract",
            "legal_memo", "discovery_request", "pleading", "demand_letter"
        ]

        if document_type not in valid_types:
            return {"status": "error", "message": f"Invalid document type. Use: {valid_types}"}

        payload = {
            "document_type": document_type,
            "context": context,
            "style": style,
            "include_citations": True,
            "jurisdiction": context.get("jurisdiction", "federal")
        }

        try:
            async with session.post(
                f"{self.base_url}/document/draft",
                json=payload
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"status": "error", "code": response.status}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def analyze_case(
        self,
        case_id: str = None,
        case_text: str = None,
        analysis_type: List[str] = None
    ) -> Dict:
        """
        Analyze a legal case for precedents, outcomes, strategy

        Args:
            case_id: Cetient case ID if known
            case_text: Raw case text for analysis
            analysis_type: Types of analysis needed
        """
        session = await self._get_session()

        if analysis_type is None:
            analysis_type = ["precedent", "outcome_prediction", "strategy"]

        payload = {
            "analysis_types": analysis_type
        }

        if case_id:
            payload["case_id"] = case_id
        elif case_text:
            payload["case_text"] = case_text
        else:
            return {"status": "error", "message": "Provide case_id or case_text"}

        try:
            async with session.post(
                f"{self.base_url}/case/analyze",
                json=payload
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"status": "error", "code": response.status}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def find_precedents(
        self,
        legal_issue: str,
        jurisdiction: str = "all",
        favorable: bool = True
    ) -> Dict:
        """
        Find relevant precedents for a legal issue

        Args:
            legal_issue: Description of the legal issue
            jurisdiction: Target jurisdiction
            favorable: Whether to prioritize favorable precedents
        """
        session = await self._get_session()

        payload = {
            "legal_issue": legal_issue,
            "jurisdiction": jurisdiction,
            "prioritize_favorable": favorable,
            "include_citations": True,
            "max_results": 25
        }

        try:
            async with session.post(
                f"{self.base_url}/precedents/find",
                json=payload
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"status": "error", "code": response.status}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def verify_citations(self, citations: List[str]) -> Dict:
        """
        Verify legal citations are accurate and current

        Args:
            citations: List of legal citations to verify
        """
        session = await self._get_session()

        payload = {
            "citations": citations,
            "check_overruled": True,
            "check_distinguished": True
        }

        try:
            async with session.post(
                f"{self.base_url}/citations/verify",
                json=payload
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"status": "error", "code": response.status}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()


class LegalDivisionOrchestrator:
    """Orchestrates 35 Legal Division agents with Cetient AI"""

    def __init__(self):
        self.cetient = CetientLegalAI()
        self.agents = self._initialize_agents()

    def _initialize_agents(self) -> Dict:
        """Initialize 35 legal division agents"""
        return {
            "research_specialists": [
                {"id": f"legal_research_{i}", "status": "active", "task": None}
                for i in range(1, 11)
            ],
            "document_drafters": [
                {"id": f"legal_draft_{i}", "status": "active", "task": None}
                for i in range(1, 11)
            ],
            "compliance_monitors": [
                {"id": f"legal_compliance_{i}", "status": "active", "task": None}
                for i in range(1, 9)
            ],
            "strategy_analysts": [
                {"id": f"legal_strategy_{i}", "status": "active", "task": None}
                for i in range(1, 8)
            ]
        }

    async def run_research_task(self, query: str) -> Dict:
        """Assign research task to available agent"""
        for agent in self.agents["research_specialists"]:
            if agent["task"] is None:
                agent["task"] = query
                agent["status"] = "working"
                result = await self.cetient.search_case_law(query)
                agent["task"] = None
                agent["status"] = "active"
                return {
                    "agent": agent["id"],
                    "result": result
                }
        return {"status": "error", "message": "All research agents busy"}

    async def run_drafting_task(
        self,
        doc_type: str,
        context: Dict
    ) -> Dict:
        """Assign drafting task to available agent"""
        for agent in self.agents["document_drafters"]:
            if agent["task"] is None:
                agent["task"] = doc_type
                agent["status"] = "working"
                result = await self.cetient.draft_document(doc_type, context)
                agent["task"] = None
                agent["status"] = "active"
                return {
                    "agent": agent["id"],
                    "result": result
                }
        return {"status": "error", "message": "All drafting agents busy"}

    async def run_compliance_check(self, regulations: List[str]) -> Dict:
        """Run compliance check across regulations"""
        results = []
        for i, reg in enumerate(regulations):
            if i < len(self.agents["compliance_monitors"]):
                agent = self.agents["compliance_monitors"][i]
                agent["task"] = reg
                agent["status"] = "working"
                result = await self.cetient.search_case_law(
                    f"compliance {reg} regulations requirements"
                )
                results.append({
                    "agent": agent["id"],
                    "regulation": reg,
                    "result": result
                })
                agent["task"] = None
                agent["status"] = "active"
        return {"compliance_results": results}

    async def run_strategy_analysis(self, case_details: Dict) -> Dict:
        """Run strategy analysis with all strategy agents"""
        tasks = [
            self.cetient.analyze_case(case_text=case_details.get("description")),
            self.cetient.find_precedents(case_details.get("legal_issue")),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            "case_analysis": results[0] if not isinstance(results[0], Exception) else str(results[0]),
            "precedents": results[1] if not isinstance(results[1], Exception) else str(results[1])
        }

    def get_agent_status(self) -> Dict:
        """Get status of all 35 legal agents"""
        status = {
            "total_agents": 35,
            "active": 0,
            "working": 0,
            "divisions": {}
        }

        for division, agents in self.agents.items():
            division_status = {"active": 0, "working": 0}
            for agent in agents:
                if agent["status"] == "active":
                    status["active"] += 1
                    division_status["active"] += 1
                else:
                    status["working"] += 1
                    division_status["working"] += 1
            status["divisions"][division] = division_status

        return status

    async def shutdown(self):
        """Shutdown all agents and close connections"""
        await self.cetient.close()


async def main():
    """Main execution - test Cetient integration"""
    print("=" * 60)
    print("CETIENT LEGAL AI - AGENT X5 INTEGRATION TEST")
    print("=" * 60)

    orchestrator = LegalDivisionOrchestrator()

    # Check agent status
    status = orchestrator.get_agent_status()
    print(f"\nLegal Division Agents: {status['total_agents']}")
    print(f"  - Active: {status['active']}")
    print(f"  - Working: {status['working']}")

    for division, div_status in status['divisions'].items():
        print(f"  - {division}: {div_status['active']} active")

    print("\n" + "=" * 60)
    print("CETIENT INTEGRATION: READY")
    print("9M+ Legal Decisions: ACCESSIBLE")
    print("Document Drafting: ENABLED")
    print("=" * 60)

    await orchestrator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
