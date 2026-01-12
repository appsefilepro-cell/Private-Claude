"""
Grant Pipeline Manager
Manages grant opportunities and application pipeline for non-profit clients
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('GrantPipeline')


class GrantPipelineManager:
    """
    Manages grant discovery, tracking, and pipeline management
    for non-profit clients seeking funding opportunities
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize Grant Pipeline Manager"""
        self.config = self.load_config(config_path)
        self.pipeline_file = "data/grant_pipeline.json"
        self.tools_database = "data/free_tools_database.json"
        self.resource_library = "data/grant_resources.json"
        self.pipeline = self.load_pipeline()
        logger.info("Grant Pipeline Manager initialized")

    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration"""
        default_config = {
            "grant_sources": ["Grants.gov", "SAM.gov", "Candid.org", "State Portals"],
            "focus_areas": ["technology", "AI/automation", "small business support"],
            "alert_days": [30, 7, 3, 1],
            "weekly_digest_day": "Monday"
        }
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        return default_config

    def load_pipeline(self) -> List[Dict[str, Any]]:
        """Load grant pipeline from storage"""
        if os.path.exists(self.pipeline_file):
            with open(self.pipeline_file, 'r') as f:
                return json.load(f)
        return []

    def save_pipeline(self):
        """Save grant pipeline to storage"""
        os.makedirs(os.path.dirname(self.pipeline_file), exist_ok=True)
        with open(self.pipeline_file, 'w') as f:
            json.dump(self.pipeline, f, indent=2)
        logger.info(f"Pipeline saved: {len(self.pipeline)} grants")

    def add_grant(self, grant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add new grant opportunity to pipeline"""
        grant = {
            "id": len(self.pipeline) + 1,
            "grant_name": grant_data.get("grant_name"),
            "funding_agency": grant_data.get("funding_agency"),
            "amount_available": grant_data.get("amount_available", 0),
            "due_date": grant_data.get("due_date"),
            "status": grant_data.get("status", "Research"),
            "assigned_writer": grant_data.get("assigned_writer", "Unassigned"),
            "win_probability": grant_data.get("win_probability", 0.5),
            "notes": grant_data.get("notes", ""),
            "focus_area": grant_data.get("focus_area", ""),
            "source": grant_data.get("source", "Manual Entry"),
            "date_added": datetime.now().strftime("%Y-%m-%d"),
            "last_updated": datetime.now().strftime("%Y-%m-%d")
        }
        self.pipeline.append(grant)
        self.save_pipeline()
        return grant

    def get_upcoming_deadlines(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get grants with deadlines in the next N days"""
        today = datetime.now()
        upcoming = []
        for grant in self.pipeline:
            if grant["status"] in ["Research", "Drafting"]:
                due_date = datetime.strptime(grant["due_date"], "%Y-%m-%d")
                days_remaining = (due_date - today).days
                if 0 <= days_remaining <= days:
                    grant_copy = grant.copy()
                    grant_copy["days_remaining"] = days_remaining
                    upcoming.append(grant_copy)
        upcoming.sort(key=lambda x: x["days_remaining"])
        return upcoming

    def generate_weekly_digest(self) -> Dict[str, Any]:
        """Generate weekly grant digest"""
        upcoming = self.get_upcoming_deadlines(30)
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        recently_added = [g for g in self.pipeline if g["date_added"] >= week_ago]

        status_counts = {"Research": 0, "Drafting": 0, "Submitted": 0, "Awarded": 0, "Declined": 0}
        for grant in self.pipeline:
            if grant["status"] in status_counts:
                status_counts[grant["status"]] += 1

        awarded = [g for g in self.pipeline if g["status"] == "Awarded"]
        declined = [g for g in self.pipeline if g["status"] == "Declined"]
        total_decided = len(awarded) + len(declined)
        win_rate = len(awarded) / total_decided if total_decided > 0 else 0

        return {
            "week_ending": datetime.now().strftime("%Y-%m-%d"),
            "upcoming_deadlines": upcoming,
            "recently_added": recently_added,
            "status_summary": status_counts,
            "win_rate": round(win_rate * 100, 1),
            "total_awarded": sum(g["amount_available"] for g in awarded),
            "total_pipeline_value": sum(g["amount_available"] for g in self.pipeline)
        }
