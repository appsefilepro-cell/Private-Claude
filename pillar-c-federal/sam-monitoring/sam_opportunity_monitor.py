"""
SAM.gov Opportunity Monitor
Monitors federal contracting opportunities for 8(a), small business set-asides
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SAMOpportunityMonitor')


class SAMOpportunityMonitor:
    """
    Monitor SAM.gov for federal contracting opportunities
    """

    def __init__(self):
        self.api_key = os.getenv('SAM_GOV_API_KEY', '')
        self.api_url = "https://api.sam.gov/prod/opportunities/v2/search"
        self.opportunities_file = "pillar-c-federal/sam-monitoring/opportunities.json"
        self.alerts_file = "pillar-c-federal/sam-monitoring/alerts.json"

        # Target criteria from the master prompt
        self.target_naics = ["561110", "541611", "541990"]
        self.max_value = 10000
        self.set_aside_types = ["8(a)", "SDB", "SDVOSB", "WOSB"]

        os.makedirs(os.path.dirname(self.opportunities_file), exist_ok=True)

        logger.info("SAM.gov Opportunity Monitor initialized")

    def search_opportunities(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Search for opportunities matching criteria

        Args:
            days_back: Number of days to look back

        Returns:
            List of matching opportunities
        """
        logger.info(f"Searching SAM.gov for opportunities (last {days_back} days)")

        opportunities = []

        try:
            # In production, this would make actual API calls
            # Example API call structure:
            # params = {
            #     "api_key": self.api_key,
            #     "postedFrom": (datetime.now() - timedelta(days=days_back)).strftime("%m/%d/%Y"),
            #     "postedTo": datetime.now().strftime("%m/%d/%Y"),
            #     "ncode": ",".join(self.target_naics),
            #     "typeOfSetAside": "8A",
            #     "limit": 100
            # }
            # response = requests.get(self.api_url, params=params)
            # opportunities = response.json().get('opportunitiesData', [])

            # Simulated opportunities for template
            opportunities = self._get_sample_opportunities()

            # Filter by criteria
            filtered = []
            for opp in opportunities:
                if self._matches_criteria(opp):
                    filtered.append(opp)

            logger.info(f"Found {len(filtered)} matching opportunities")
            return filtered

        except Exception as e:
            logger.error(f"Error searching opportunities: {e}")
            return []

    def _matches_criteria(self, opportunity: Dict[str, Any]) -> bool:
        """Check if opportunity matches our criteria"""
        # Check NAICS code
        naics = opportunity.get('naicsCode', '')
        if naics not in self.target_naics:
            return False

        # Check set-aside type
        set_aside = opportunity.get('typeOfSetAside', '')
        if not any(sa in set_aside for sa in self.set_aside_types):
            return False

        # Check value (if available)
        value = opportunity.get('estimatedValue', 0)
        if value > 0 and value > self.max_value:
            return False

        return True

    def _get_sample_opportunities(self) -> List[Dict[str, Any]]:
        """Get sample opportunities for template"""
        return [
            {
                "noticeId": "sample_001",
                "title": "Office Administrative Services",
                "solicitationNumber": "123456789",
                "department": "Department of Defense",
                "subTier": "Army",
                "office": "Army Contracting Command",
                "postedDate": datetime.now().isoformat(),
                "responseDeadLine": (datetime.now() + timedelta(days=30)).isoformat(),
                "naicsCode": "561110",
                "typeOfSetAside": "Total Small Business Set-Aside (FAR 19.5)",
                "classificationCode": "R",
                "description": "Office administrative services for military installation",
                "estimatedValue": 8500,
                "uiLink": "https://sam.gov/opp/sample_001"
            }
        ]

    def save_opportunities(self, opportunities: List[Dict[str, Any]]) -> None:
        """Save opportunities to file"""
        try:
            # Load existing opportunities
            existing = []
            if os.path.exists(self.opportunities_file):
                with open(self.opportunities_file, 'r') as f:
                    existing = json.load(f)

            # Merge and deduplicate
            all_opps = existing + opportunities
            seen = set()
            unique_opps = []
            for opp in all_opps:
                notice_id = opp.get('noticeId')
                if notice_id not in seen:
                    seen.add(notice_id)
                    unique_opps.append(opp)

            # Save
            with open(self.opportunities_file, 'w') as f:
                json.dump(unique_opps, f, indent=2)

            logger.info(f"Saved {len(unique_opps)} opportunities to {self.opportunities_file}")

        except Exception as e:
            logger.error(f"Error saving opportunities: {e}")

    def create_alerts(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create alerts for new opportunities"""
        alerts = []

        for opp in opportunities:
            alert = {
                "timestamp": datetime.now().isoformat(),
                "opportunity_id": opp.get('noticeId'),
                "title": opp.get('title'),
                "agency": opp.get('department'),
                "deadline": opp.get('responseDeadLine'),
                "naics": opp.get('naicsCode'),
                "set_aside": opp.get('typeOfSetAside'),
                "value": opp.get('estimatedValue'),
                "link": opp.get('uiLink'),
                "priority": self._calculate_priority(opp),
                "status": "new"
            }
            alerts.append(alert)

        # Save alerts
        try:
            with open(self.alerts_file, 'w') as f:
                json.dump(alerts, f, indent=2)
            logger.info(f"Created {len(alerts)} alerts")
        except Exception as e:
            logger.error(f"Error saving alerts: {e}")

        return alerts

    def _calculate_priority(self, opportunity: Dict[str, Any]) -> str:
        """Calculate priority based on deadline and fit"""
        deadline_str = opportunity.get('responseDeadLine', '')

        try:
            deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
            days_until = (deadline - datetime.now()).days

            if days_until < 7:
                return "URGENT"
            elif days_until < 14:
                return "HIGH"
            elif days_until < 30:
                return "MEDIUM"
            else:
                return "LOW"

        except Exception:
            return "MEDIUM"

    def send_email_alert(self, alerts: List[Dict[str, Any]]) -> None:
        """Send email alert for new opportunities"""
        if not alerts:
            return

        subject = f"SAM.gov Alert: {len(alerts)} New Federal Opportunities"

        body = f"""
You have {len(alerts)} new federal contracting opportunities:

"""

        for alert in alerts[:10]:  # Top 10 only
            body += f"""
Title: {alert['title']}
Agency: {alert['agency']}
NAICS: {alert['naics']}
Set-Aside: {alert['set_aside']}
Deadline: {alert['deadline']}
Priority: {alert['priority']}
Link: {alert['link']}

---
"""

        logger.info(f"Email alert created: {subject}")
        # In production, this would actually send email

    def get_setup_instructions(self) -> List[str]:
        """Get instructions for SAM.gov API setup"""
        return [
            "=== SAM.gov API Setup Instructions ===",
            "",
            "1. Create SAM.gov account:",
            "   - Go to https://sam.gov/",
            "   - Click 'Sign In' > 'Create Account'",
            "   - Complete entity registration for APPS Holdings WY Inc.",
            "",
            "2. Get API Key:",
            "   - Log in to SAM.gov",
            "   - Go to 'Account' > 'System Account'",
            "   - Request API key (Public API)",
            "   - Note: Free tier has rate limits",
            "",
            "3. Configure saved searches:",
            "   - Go to 'Contract Opportunities' > 'Advanced Search'",
            "   - Set criteria:",
            "     * NAICS: 561110, 541611, 541990",
            "     * Set-Aside: 8(a)",
            "     * Posted Within: Last 30 days",
            "   - Save search and enable email alerts",
            "",
            "4. Update .env file:",
            "   - Add your API key: SAM_GOV_API_KEY=your_key",
            "",
            "5. Alternative: Email parsing",
            "   - SAM.gov sends email alerts",
            "   - Use Power Automate to parse emails",
            "   - Extract opportunity details",
            "   - Add to SharePoint list",
            "",
            "API Documentation:",
            "https://open.gsa.gov/api/opportunities-api/",
            "",
            "Rate Limits (Public tier):",
            "- 1,000 requests per day",
            "- 10 requests per 10 seconds"
        ]

    def run_daily_check(self) -> Dict[str, Any]:
        """Run daily opportunity check"""
        logger.info("=== Starting daily SAM.gov check ===")

        # Search for opportunities
        opportunities = self.search_opportunities(days_back=1)

        # Save opportunities
        if opportunities:
            self.save_opportunities(opportunities)

            # Create alerts
            alerts = self.create_alerts(opportunities)

            # Send notifications
            self.send_email_alert(alerts)

            result = {
                "timestamp": datetime.now().isoformat(),
                "opportunities_found": len(opportunities),
                "alerts_created": len(alerts),
                "status": "success"
            }
        else:
            result = {
                "timestamp": datetime.now().isoformat(),
                "opportunities_found": 0,
                "alerts_created": 0,
                "status": "no_opportunities"
            }

        logger.info(f"Daily check complete: {json.dumps(result)}")
        return result


def main():
    """Main entry point"""
    monitor = SAMOpportunityMonitor()

    print("\n".join(monitor.get_setup_instructions()))
    print("\n")

    # Run daily check
    result = monitor.run_daily_check()
    print(f"\nDaily Check Result:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
