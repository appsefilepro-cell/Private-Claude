"""
Master System Orchestrator
Coordinates all system components and executes comprehensive tasks
"""
import asyncio
import logging
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add core-systems to path
core_systems_path = Path(__file__).parent
sys.path.insert(0, str(core_systems_path))

# Import all modules with full paths
from core_systems.security.path_traversal_scanner import PathTraversalScanner
from core_systems.pr_management.pr_task_manager import PRManager
from core_systems.gitlab_integration.gitlab_connector import GitLabIntegration
from core_systems.zapier_integration.zapier_advanced_connector import ZapierAdvancedIntegration
from core_systems.copilot_integration.copilot_agents import CopilotMultiAgentSystem
from core_systems.job_debugger.job_failure_resolver import JobDebugger
from core_systems.container_config.agentx5_container import AgentX5Container
from core_systems.sub_issue_tracker.sub_issue_manager import SubIssueTracker
from core_systems.agent_orchestration.agent_sync_orchestrator import AgentOrchestrator
from core_systems.ai_testing.ai_integration_tests import AITestingFramework
from pillar_a_trading.execution.trading_task_executor import TradingTaskExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MasterSystemOrchestrator:
    """Orchestrates all system components"""
    
    def __init__(self):
        self.components = {}
        self.execution_results = {}
        self.start_time = None
        self.end_time = None
        
    def initialize_components(self):
        """Initialize all system components"""
        logger.info("Initializing all system components...")
        
        self.components = {
            'security_scanner': PathTraversalScanner('/home/runner/work/Private-Claude/Private-Claude'),
            'pr_manager': PRManager(),
            'gitlab': GitLabIntegration(),
            'zapier': ZapierAdvancedIntegration(),
            'copilot': CopilotMultiAgentSystem(),
            'job_debugger': JobDebugger(),
            'container': AgentX5Container(),
            'sub_issue_tracker': SubIssueTracker(),
            'agent_orchestrator': AgentOrchestrator(),
            'testing_framework': AITestingFramework(),
            'trading_executor': TradingTaskExecutor()
        }
        
        logger.info(f"Initialized {len(self.components)} components")
    
    async def execute_all_tasks(self):
        """Execute all tasks across all components"""
        self.start_time = datetime.now()
        logger.info("="*60)
        logger.info("MASTER SYSTEM EXECUTION STARTED")
        logger.info("="*60)
        
        # Task 1: Security - Path Traversal Scanner
        logger.info("\n[1/10] Running Path Traversal Security Scanner...")
        try:
            vulnerabilities = self.components['security_scanner'].scan_directory()
            report = self.components['security_scanner'].generate_report('security_scan_report.json')
            self.execution_results['security'] = {
                'status': 'completed',
                'vulnerabilities_found': len(vulnerabilities),
                'report': 'security_scan_report.json'
            }
            logger.info(f"✓ Security scan completed: {len(vulnerabilities)} vulnerabilities found")
        except Exception as e:
            logger.error(f"✗ Security scan failed: {e}")
            self.execution_results['security'] = {'status': 'failed', 'error': str(e)}
        
        # Task 2: Trading - Execute 100 Tasks
        logger.info("\n[2/10] Executing 100 Trading Tasks...")
        try:
            results = await self.components['trading_executor'].execute_100_tasks()
            self.execution_results['trading'] = {
                'status': 'completed',
                'tasks_completed': results['completed'],
                'success_rate': results['success_rate']
            }
            logger.info(f"✓ Trading tasks completed: {results['completed']}/100")
        except Exception as e:
            logger.error(f"✗ Trading tasks failed: {e}")
            self.execution_results['trading'] = {'status': 'failed', 'error': str(e)}
        
        # Task 3: PR Management
        logger.info("\n[3/10] Organizing Pull Requests and Tasks...")
        try:
            self.components['pr_manager'].create_task_from_pr_141()
            report = self.components['pr_manager'].generate_report('pr_management_report.json')
            self.execution_results['pr_management'] = {
                'status': 'completed',
                'total_prs': report['total_prs'],
                'total_tasks': report['total_tasks']
            }
            logger.info(f"✓ PR management completed: {report['total_prs']} PRs, {report['total_tasks']} tasks")
        except Exception as e:
            logger.error(f"✗ PR management failed: {e}")
            self.execution_results['pr_management'] = {'status': 'failed', 'error': str(e)}
        
        # Task 4: GitLab Integration
        logger.info("\n[4/10] Setting up GitLab Integration...")
        try:
            self.components['gitlab'].connect()
            project = self.components['gitlab'].create_project("Private-Claude-GitLab")
            self.components['gitlab'].setup_ci_cd(project['id'], {})
            report = self.components['gitlab'].export_report('gitlab_integration_report.json')
            self.execution_results['gitlab'] = {
                'status': 'completed',
                'projects': report['total_projects'],
                'pipelines': report['total_pipelines']
            }
            logger.info(f"✓ GitLab integration completed")
        except Exception as e:
            logger.error(f"✗ GitLab integration failed: {e}")
            self.execution_results['gitlab'] = {'status': 'failed', 'error': str(e)}
        
        # Task 5: Zapier Integration
        logger.info("\n[5/10] Setting up Zapier Integration...")
        try:
            self.components['zapier'].create_trading_alert_zap()
            self.components['zapier'].create_pr_notification_zap()
            self.components['zapier'].create_error_monitoring_zap()
            report = self.components['zapier'].generate_report('zapier_integration_report.json')
            self.execution_results['zapier'] = {
                'status': 'completed',
                'zaps_created': report['total_zaps']
            }
            logger.info(f"✓ Zapier integration completed: {report['total_zaps']} Zaps")
        except Exception as e:
            logger.error(f"✗ Zapier integration failed: {e}")
            self.execution_results['zapier'] = {'status': 'failed', 'error': str(e)}
        
        # Task 6: Copilot Multi-Agent
        logger.info("\n[6/10] Setting up GitHub Copilot Multi-Agent System...")
        try:
            self.components['copilot'].setup_default_agents()
            self.components['copilot'].integrate_with_github_actions()
            report = self.components['copilot'].generate_report('copilot_integration_report.json')
            self.execution_results['copilot'] = {
                'status': 'completed',
                'agents': report['total_agents']
            }
            logger.info(f"✓ Copilot integration completed: {report['total_agents']} agents")
        except Exception as e:
            logger.error(f"✗ Copilot integration failed: {e}")
            self.execution_results['copilot'] = {'status': 'failed', 'error': str(e)}
        
        # Task 7: Job Debugger
        logger.info("\n[7/10] Debugging Job Failure 59014433637...")
        try:
            analysis = self.components['job_debugger'].analyze_job_59014433637()
            if analysis['auto_fixable']:
                fix_result = self.components['job_debugger'].auto_fix_job(analysis['job_id'])
            report = self.components['job_debugger'].generate_report('job_debugger_report.json')
            self.execution_results['job_debugger'] = {
                'status': 'completed',
                'failure_type': analysis['failure_type'],
                'auto_fixed': analysis['auto_fixable']
            }
            logger.info(f"✓ Job debugging completed: {analysis['failure_type']}")
        except Exception as e:
            logger.error(f"✗ Job debugging failed: {e}")
            self.execution_results['job_debugger'] = {'status': 'failed', 'error': str(e)}
        
        # Task 8: AgentX 5.0 Container
        logger.info("\n[8/10] Configuring AgentX 5.0 Container...")
        try:
            configs = self.components['container'].save_configs()
            report = self.components['container'].generate_report('agentx5_container_report.json')
            self.execution_results['container'] = {
                'status': 'completed',
                'configs_generated': len(configs)
            }
            logger.info(f"✓ Container configuration completed: {len(configs)} files")
        except Exception as e:
            logger.error(f"✗ Container configuration failed: {e}")
            self.execution_results['container'] = {'status': 'failed', 'error': str(e)}
        
        # Task 9: Sub-Issue Tracker
        logger.info("\n[9/10] Setting up Sub-Issue Tracking...")
        try:
            self.components['sub_issue_tracker'].create_pr_141_sub_issues()
            report = self.components['sub_issue_tracker'].generate_report('sub_issue_tracker_report.json')
            self.execution_results['sub_issue_tracker'] = {
                'status': 'completed',
                'sub_issues': report['total_sub_issues']
            }
            logger.info(f"✓ Sub-issue tracking completed: {report['total_sub_issues']} sub-issues")
        except Exception as e:
            logger.error(f"✗ Sub-issue tracking failed: {e}")
            self.execution_results['sub_issue_tracker'] = {'status': 'failed', 'error': str(e)}
        
        # Task 10: Agent Orchestration
        logger.info("\n[10/10] Orchestrating Agent Systems...")
        try:
            self.components['agent_orchestrator'].setup_agent_fleet()
            sync_result = self.components['agent_orchestrator'].sync_agents()
            merge_result = self.components['agent_orchestrator'].merge_agents(
                ["agent_3.0", "agent_4.0", "agentx5"]
            )
            report = self.components['agent_orchestrator'].generate_report('agent_orchestration_report.json')
            self.execution_results['agent_orchestration'] = {
                'status': 'completed',
                'agents_synced': len(sync_result['agents_synced'])
            }
            logger.info(f"✓ Agent orchestration completed: {len(sync_result['agents_synced'])} agents synced")
        except Exception as e:
            logger.error(f"✗ Agent orchestration failed: {e}")
            self.execution_results['agent_orchestration'] = {'status': 'failed', 'error': str(e)}
        
        # Bonus: AI Testing Framework
        logger.info("\n[BONUS] Running AI Integration Tests...")
        try:
            self.components['testing_framework'].setup_comprehensive_tests()
            test_results = self.components['testing_framework'].execute_all_tests()
            report = self.components['testing_framework'].generate_report('ai_testing_report.json')
            self.execution_results['testing'] = {
                'status': 'completed',
                'success_rate': test_results['overall_success_rate']
            }
            logger.info(f"✓ Testing completed: {test_results['overall_success_rate']:.1f}% success rate")
        except Exception as e:
            logger.error(f"✗ Testing failed: {e}")
            self.execution_results['testing'] = {'status': 'failed', 'error': str(e)}
        
        self.end_time = datetime.now()
    
    def generate_master_report(self):
        """Generate comprehensive master report"""
        duration = (self.end_time - self.start_time).total_seconds()
        
        completed = sum(1 for r in self.execution_results.values() if r['status'] == 'completed')
        failed = sum(1 for r in self.execution_results.values() if r['status'] == 'failed')
        
        report = {
            'execution_summary': {
                'start_time': self.start_time.isoformat(),
                'end_time': self.end_time.isoformat(),
                'duration_seconds': duration,
                'total_tasks': len(self.execution_results),
                'completed': completed,
                'failed': failed,
                'success_rate': (completed / len(self.execution_results)) * 100
            },
            'task_results': self.execution_results,
            'recommendations': self._generate_recommendations()
        }
        
        with open('MASTER_EXECUTION_REPORT.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def _generate_recommendations(self):
        """Generate recommendations based on results"""
        recommendations = []
        
        if self.execution_results.get('security', {}).get('vulnerabilities_found', 0) > 0:
            recommendations.append("Review and fix identified security vulnerabilities")
        
        if self.execution_results.get('testing', {}).get('success_rate', 100) < 95:
            recommendations.append("Investigate and fix failing tests")
        
        if any(r['status'] == 'failed' for r in self.execution_results.values()):
            recommendations.append("Review and resolve failed task executions")
        
        recommendations.append("Continue monitoring system performance")
        recommendations.append("Schedule regular security scans")
        recommendations.append("Keep all integrations up to date")
        
        return recommendations
    
    def print_summary(self):
        """Print execution summary"""
        report = self.generate_master_report()
        
        print(f"\n{'='*70}")
        print("MASTER SYSTEM EXECUTION REPORT")
        print(f"{'='*70}")
        print(f"Start Time: {report['execution_summary']['start_time']}")
        print(f"End Time: {report['execution_summary']['end_time']}")
        print(f"Duration: {report['execution_summary']['duration_seconds']:.2f} seconds")
        print(f"\nExecution Summary:")
        print(f"  Total Tasks: {report['execution_summary']['total_tasks']}")
        print(f"  Completed: {report['execution_summary']['completed']}")
        print(f"  Failed: {report['execution_summary']['failed']}")
        print(f"  Success Rate: {report['execution_summary']['success_rate']:.2f}%")
        
        print(f"\nTask Results:")
        for task_name, result in report['task_results'].items():
            status_icon = "✓" if result['status'] == 'completed' else "✗"
            print(f"  {status_icon} {task_name}: {result['status']}")
        
        print(f"\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
        
        print(f"\nDetailed reports saved:")
        print(f"  • MASTER_EXECUTION_REPORT.json")
        print(f"  • security_scan_report.json")
        print(f"  • pr_management_report.json")
        print(f"  • gitlab_integration_report.json")
        print(f"  • zapier_integration_report.json")
        print(f"  • copilot_integration_report.json")
        print(f"  • job_debugger_report.json")
        print(f"  • agentx5_container_report.json")
        print(f"  • sub_issue_tracker_report.json")
        print(f"  • agent_orchestration_report.json")
        print(f"  • ai_testing_report.json")
        print(f"{'='*70}\n")


async def main():
    """Main execution function"""
    orchestrator = MasterSystemOrchestrator()
    orchestrator.initialize_components()
    await orchestrator.execute_all_tasks()
    orchestrator.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
