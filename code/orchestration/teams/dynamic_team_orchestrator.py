"""
Augur Omega: Dynamic Team Orchestrator
Advanced team formation with adaptive specialization and intelligent workload distribution
"""
import json
import logging
import threading
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import numpy as np
from collections import defaultdict, deque
import heapq

from ..core.enhanced_agent_manager import (
    AgentInfo, AgentCapability, AgentStatus, TeamType, 
    EnhancedAgentManager, AgentMetrics
)

logger = logging.getLogger(__name__)

class WorkloadType(Enum):
    """Types of workloads that require different team compositions"""
    RESEARCH_PROJECT = "research_project"
    DEVELOPMENT_SPRINT = "development_sprint"
    INTEGRATION_RELEASE = "integration_release"
    EMERGENCY_RESPONSE = "emergency_response"
    MAINTENANCE_WINDOW = "maintenance_window"
    CROSS_TEAM_COLLABORATION = "cross_team_collaboration"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"

class SpecializationDomain(Enum):
    """Domain specializations for agents"""
    AI_MACHINE_LEARNING = "ai_ml"
    WEB_DEVELOPMENT = "web_dev"
    DATA_SCIENCE = "data_science"
    CLOUD_INFRASTRUCTURE = "cloud_infra"
    SECURITY_AUDITING = "security_audit"
    INTEGRATION_TESTING = "integration_testing"
    PERFORMANCE_MONITORING = "performance_monitoring"
    DATABASE_OPTIMIZATION = "database_opt"
    MOBILE_DEVELOPMENT = "mobile_dev"
    DEVOPS_AUTOMATION = "devops_auto"

@dataclass
class TeamCapabilityProfile:
    """Team capability profile for different workload types"""
    required_capabilities: List[str] = field(default_factory=list)
    min_agent_count: int = 2
    max_agent_count: int = 10
    skill_distribution: Dict[str, float] = field(default_factory=dict)  # weight distribution
    coordination_complexity: float = 1.0  # 1.0 = simple, 5.0 = very complex
    estimated_duration_hours: float = 4.0

@dataclass
class WorkloadRequest:
    """Workload request for team assignment"""
    request_id: str
    workload_type: WorkloadType
    domain: SpecializationDomain
    priority: int  # 1 = highest, 10 = lowest
    description: str
    required_skills: List[str] = field(default_factory=list)
    deadline: Optional[datetime] = None
    estimated_effort_hours: float = 4.0
    dependencies: List[str] = field(default_factory=list)  # other request IDs
    constraints: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TeamPerformance:
    """Team performance tracking"""
    team_id: str
    workload_history: List[Dict[str, Any]] = field(default_factory=list)
    avg_completion_time: float = 0.0
    success_rate: float = 1.0
    avg_quality_score: float = 1.0
    efficiency_score: float = 1.0
    specialization_effectiveness: Dict[SpecializationDomain, float] = field(default_factory=dict)

class AdaptiveSpecializationEngine:
    """Engine for adaptive specialization based on performance patterns"""
    
    def __init__(self):
        self.performance_history = {}
        self.specialization_learning = {}
        self.cross_training_effectiveness = {}
        self.domain_expertise = defaultdict(float)
        
    def analyze_performance_pattern(self, agent_id: str, workload_result: Dict[str, Any]):
        """Analyze agent performance for specialization optimization"""
        domain = SpecializationDomain(workload_result.get("domain", "general"))
        success = workload_result.get("success", False)
        completion_time = workload_result.get("completion_time", 1.0)
        quality_score = workload_result.get("quality_score", 1.0)
        complexity = workload_result.get("complexity_score", 1.0)
        
        # Update domain expertise
        effectiveness = (1.0 if success else 0.5) * (quality_score) * (2.0 - min(complexity/10.0, 1.0))
        self.domain_expertise[domain] = max(self.domain_expertise[domain], effectiveness)
        
        # Track agent-specific patterns
        if agent_id not in self.performance_history:
            self.performance_history[agent_id] = {}
        
        if domain.value not in self.performance_history[agent_id]:
            self.performance_history[agent_id][domain.value] = {
                "tasks": 0,
                "total_success_rate": 0.0,
                "avg_quality": 1.0,
                "avg_completion_time": 1.0
            }
        
        history = self.performance_history[agent_id][domain.value]
        history["tasks"] += 1
        
        # Update running averages
        alpha = 0.1  # Learning rate
        if success:
            history["total_success_rate"] = (1 - alpha) * history["total_success_rate"] + alpha * 1.0
        else:
            history["total_success_rate"] = (1 - alpha) * history["total_success_rate"] + alpha * 0.0
        
        history["avg_quality"] = (1 - alpha) * history["avg_quality"] + alpha * quality_score
        history["avg_completion_time"] = (1 - alpha) * history["avg_completion_time"] + alpha * completion_time
    
    def get_specialization_recommendation(self, agent_id: str, domain: SpecializationDomain) -> Dict[str, float]:
        """Get specialization recommendations for an agent"""
        if agent_id in self.performance_history and domain.value in self.performance_history[agent_id]:
            history = self.performance_history[agent_id][domain.value]
            
            return {
                "expertise_level": history["total_success_rate"] * 10,  # Convert to 1-10 scale
                "quality_consistency": 1.0 - (abs(history["avg_quality"] - 1.0) / 2.0),
                "efficiency": 1.0 / max(history["avg_completion_time"], 0.1),
                "recommendation": "high" if history["total_success_rate"] > 0.8 else "medium" if history["total_success_rate"] > 0.6 else "low"
            }
        
        return {"expertise_level": 1.0, "quality_consistency": 0.5, "efficiency": 1.0, "recommendation": "low"}

class TeamCompositionOptimizer:
    """Optimizes team composition based on workload requirements and agent capabilities"""
    
    def __init__(self):
        self.optimization_history = []
        self.success_patterns = {}
        
    def optimize_team_composition(self, 
                                workload: WorkloadRequest, 
                                available_agents: Dict[str, AgentInfo]) -> Tuple[List[str], Dict[str, float]]:
        """Optimize team composition for a workload"""
        
        # Score agents based on capability match
        agent_scores = {}
        
        for agent_id, agent in available_agents.items():
            if agent.status != AgentStatus.RUNNING:
                continue
            
            score = self._calculate_agent_score(agent, workload)
            agent_scores[agent_id] = score
        
        # Select best agents for the team
        team_size = self._calculate_optimal_team_size(workload)
        selected_agents = self._select_team_members(agent_scores, team_size, workload)
        
        # Calculate expected team performance
        team_performance = self._estimate_team_performance(selected_agents, workload)
        
        logger.info(f"Optimized team for {workload.workload_type.value}: {len(selected_agents)} agents, expected performance: {team_performance['expected_success_rate']:.2f}")
        
        return selected_agents, team_performance
    
    def _calculate_agent_score(self, agent: AgentInfo, workload: WorkloadRequest) -> float:
        """Calculate agent suitability score for a workload"""
        base_score = 0.0
        
        # Check capability matching
        capability_score = 0.0
        required_skills = set(workload.required_skills)
        
        for capability in agent.capabilities:
            if capability.name.lower() in [skill.lower() for skill in required_skills]:
                capability_score += (capability.level / 10.0) * (capability.workload_capacity / 5.0)
        
        base_score += capability_score * 0.4
        
        # Check health and availability
        health_score = agent.metrics.health_score / 100.0
        base_score += health_score * 0.3
        
        # Check specialization domain match
        domain_score = self._check_domain_specialization(agent, workload.domain)
        base_score += domain_score * 0.2
        
        # Check current workload capacity
        workload_score = 1.0 - (len(agent.workload.get("current_task", {})) / 10.0)
        base_score += workload_score * 0.1
        
        return min(1.0, base_score)
    
    def _check_domain_specialization(self, agent: AgentInfo, domain: SpecializationDomain) -> float:
        """Check if agent has domain specialization"""
        domain_str = domain.value
        
        for capability in agent.capabilities:
            if domain_str in capability.specialization_tags:
                return capability.level / 10.0
        
        return 0.3  # Base score for non-specialized agents
    
    def _calculate_optimal_team_size(self, workload: WorkloadRequest) -> int:
        """Calculate optimal team size based on workload complexity"""
        base_size = 3
        complexity_bonus = int(workload.estimated_effort_hours / 8.0)  # Additional members per 8 hours
        
        # Adjust for different workload types
        type_adjustments = {
            WorkloadType.RESEARCH_PROJECT: 1,
            WorkloadType.DEVELOPMENT_SPRINT: 2,
            WorkloadType.INTEGRATION_RELEASE: 3,
            WorkloadType.EMERGENCY_RESPONSE: 4,
            WorkloadType.MAINTENANCE_WINDOW: 1,
            WorkloadType.CROSS_TEAM_COLLABORATION: 3,
            WorkloadType.PERFORMANCE_OPTIMIZATION: 2
        }
        
        optimal_size = base_size + complexity_bonus + type_adjustments.get(workload.workload_type, 0)
        return min(8, max(2, optimal_size))
    
    def _select_team_members(self, agent_scores: Dict[str, float], team_size: int, workload: WorkloadRequest) -> List[str]:
        """Select team members based on scores"""
        # Sort agents by score
        sorted_agents = sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)
        
        selected = []
        
        # First pass: select highest scoring agents
        for agent_id, score in sorted_agents[:team_size]:
            selected.append(agent_id)
        
        # Second pass: ensure diversity if needed
        if workload.workload_type in [WorkloadType.RESEARCH_PROJECT, WorkloadType.DEVELOPMENT_SPRINT]:
            # Prioritize diversity in development contexts
            selected = self._ensure_capability_diversity(selected, workload.required_skills)
        
        return selected
    
    def _ensure_capability_diversity(self, team: List[str], required_skills: List[str]) -> List[str]:
        """Ensure team has diverse capabilities"""
        # This would implement capability diversity logic
        # For now, return the team as-is
        return team
    
    def _estimate_team_performance(self, team: List[str], workload: WorkloadRequest) -> Dict[str, float]:
        """Estimate team performance metrics"""
        # Calculate expected success rate based on team composition
        base_success_rate = 0.7
        
        # Team size efficiency factor
        team_size_factor = 1.0 - (len(team) - 4) * 0.1 if len(team) > 4 else 1.0
        
        # Coordination complexity factor
        complexity_factor = max(0.5, 1.0 - (workload.constraints.get("coordination_complexity", 1.0) - 1.0) * 0.2)
        
        estimated_success_rate = base_success_rate * team_size_factor * complexity_factor
        
        return {
            "expected_success_rate": max(0.3, min(0.95, estimated_success_rate)),
            "estimated_completion_time": workload.estimated_effort_hours / min(len(team), 6),
            "team_coordination_score": complexity_factor,
            "team_size_efficiency": team_size_factor
        }

class WorkloadScheduler:
    """Schedules and manages workload assignment to teams"""
    
    def __init__(self):
        self.pending_workloads = []
        self.active_teams = {}
        self.completed_workloads = deque(maxlen=1000)  # Keep last 1000 completed workloads
        self.scheduling_history = []
        
    def submit_workload(self, workload: WorkloadRequest):
        """Submit a workload for scheduling"""
        # Add priority-based priority queue behavior
        workload_submission = {
            "workload": workload,
            "submission_time": datetime.now(),
            "status": "pending"
        }
        
        self.pending_workloads.append(workload_submission)
        logger.info(f"Workload {workload.request_id} ({workload.workload_type.value}) submitted")
    
    def schedule_next_workload(self, agent_manager: EnhancedAgentManager) -> Optional[WorkloadRequest]:
        """Schedule the next workload based on priority and resource availability"""
        if not self.pending_workloads:
            return None
        
        # Sort by priority (higher priority = smaller number = higher rank)
        self.pending_workloads.sort(key=lambda x: x["workload"].priority)
        
        # Select highest priority workload
        next_workload_submission = self.pending_workloads.pop(0)
        workload = next_workload_submission["workload"]
        
        # Check if deadline is approaching
        deadline_urgency = self._calculate_deadline_urgency(workload)
        if deadline_urgency > 0.8:
            workload.priority = 1  # Boost priority for urgent deadlines
        
        next_workload_submission["status"] = "scheduled"
        next_workload_submission["scheduled_time"] = datetime.now()
        
        logger.info(f"Scheduling workload {workload.request_id} (priority: {workload.priority})")
        return workload
    
    def _calculate_deadline_urgency(self, workload: WorkloadRequest) -> float:
        """Calculate urgency based on deadline proximity"""
        if not workload.deadline:
            return 0.0
        
        now = datetime.now()
        if now >= workload.deadline:
            return 1.0
        
        time_to_deadline = (workload.deadline - now).total_seconds()
        total_estimated_time = workload.estimated_effort_hours * 3600
        
        urgency = 1.0 - (time_to_deadline / (total_estimated_time * 2))  # 2x buffer time
        return max(0.0, min(1.0, urgency))

class DynamicTeamOrchestrator:
    """Main orchestrator for dynamic team formation and workload management"""
    
    def __init__(self, agent_manager: EnhancedAgentManager):
        self.agent_manager = agent_manager
        self.specialization_engine = AdaptiveSpecializationEngine()
        self.composition_optimizer = TeamCompositionOptimizer()
        self.workload_scheduler = WorkloadScheduler()
        
        # Team composition profiles
        self.team_profiles = self._initialize_team_profiles()
        
        # Orchestrator state
        self.orchestrator_running = False
        self.orchestrator_thread = None
        self.orchestration_lock = threading.Lock()
        
        # Performance tracking
        self.orchestration_metrics = {
            "workloads_processed": 0,
            "teams_formed": 0,
            "avg_team_size": 0.0,
            "success_rate": 1.0,
            "avg_completion_time": 0.0
        }
        
        logger.info("Dynamic Team Orchestrator initialized")
    
    def _initialize_team_profiles(self) -> Dict[WorkloadType, TeamCapabilityProfile]:
        """Initialize team capability profiles for different workload types"""
        profiles = {}
        
        # Research and Development teams
        profiles[WorkloadType.RESEARCH_PROJECT] = TeamCapabilityProfile(
            required_capabilities=["research", "analysis", "documentation"],
            min_agent_count=2,
            max_agent_count=5,
            skill_distribution={"research": 0.4, "analysis": 0.4, "documentation": 0.2},
            coordination_complexity=2.0,
            estimated_duration_hours=12.0
        )
        
        # Development teams
        profiles[WorkloadType.DEVELOPMENT_SPRINT] = TeamCapabilityProfile(
            required_capabilities=["coding", "testing", "code_review"],
            min_agent_count=3,
            max_agent_count=8,
            skill_distribution={"coding": 0.5, "testing": 0.3, "code_review": 0.2},
            coordination_complexity=3.0,
            estimated_duration_hours=8.0
        )
        
        # Integration teams
        profiles[WorkloadType.INTEGRATION_RELEASE] = TeamCapabilityProfile(
            required_capabilities=["integration", "deployment", "monitoring"],
            min_agent_count=4,
            max_agent_count=10,
            skill_distribution={"integration": 0.4, "deployment": 0.4, "monitoring": 0.2},
            coordination_complexity=4.0,
            estimated_duration_hours=6.0
        )
        
        # Emergency response teams
        profiles[WorkloadType.EMERGENCY_RESPONSE] = TeamCapabilityProfile(
            required_capabilities=["incident_response", "diagnostic", "resolution"],
            min_agent_count=3,
            max_agent_count=6,
            skill_distribution={"incident_response": 0.5, "diagnostic": 0.3, "resolution": 0.2},
            coordination_complexity=2.5,
            estimated_duration_hours=4.0
        )
        
        # Maintenance teams
        profiles[WorkloadType.MAINTENANCE_WINDOW] = TeamCapabilityProfile(
            required_capabilities=["maintenance", "backup", "monitoring"],
            min_agent_count=2,
            max_agent_count=4,
            skill_distribution={"maintenance": 0.5, "backup": 0.3, "monitoring": 0.2},
            coordination_complexity=1.5,
            estimated_duration_hours=3.0
        )
        
        # Cross-team collaboration
        profiles[WorkloadType.CROSS_TEAM_COLLABORATION] = TeamCapabilityProfile(
            required_capabilities=["coordination", "communication", "integration"],
            min_agent_count=4,
            max_agent_count=8,
            skill_distribution={"coordination": 0.4, "communication": 0.3, "integration": 0.3},
            coordination_complexity=5.0,
            estimated_duration_hours=10.0
        )
        
        # Performance optimization
        profiles[WorkloadType.PERFORMANCE_OPTIMIZATION] = TeamCapabilityProfile(
            required_capabilities=["performance_analysis", "optimization", "monitoring"],
            min_agent_count=2,
            max_agent_count=5,
            skill_distribution={"performance_analysis": 0.4, "optimization": 0.4, "monitoring": 0.2},
            coordination_complexity=2.5,
            estimated_duration_hours=8.0
        )
        
        return profiles
    
    def start_orchestration(self):
        """Start the dynamic team orchestration system"""
        if self.orchestrator_running:
            logger.warning("Orchestrator already running")
            return
        
        self.orchestrator_running = True
        self.orchestrator_thread = threading.Thread(target=self._orchestration_loop, daemon=True)
        self.orchestrator_thread.start()
        logger.info("Dynamic Team Orchestrator started")
    
    def stop_orchestration(self):
        """Stop the orchestration system"""
        self.orchestrator_running = False
        
        if self.orchestrator_thread:
            self.orchestrator_thread.join(timeout=5)
        
        logger.info("Dynamic Team Orchestrator stopped")
    
    def _orchestration_loop(self):
        """Main orchestration loop"""
        while self.orchestrator_running:
            try:
                # Process pending workloads
                workload = self.workload_scheduler.schedule_next_workload(self.agent_manager)
                
                if workload:
                    self._process_workload(workload)
                
                # Update specialization based on recent performance
                self._update_specializations()
                
                # Clean up completed teams
                self._cleanup_completed_teams()
                
                time.sleep(2)  # Main orchestration interval
                
            except Exception as e:
                logger.error(f"Error in orchestration loop: {str(e)}")
                time.sleep(5)
    
    def _process_workload(self, workload: WorkloadRequest):
        """Process a workload by forming optimal team"""
        with self.orchestration_lock:
            try:
                # Get available agents
                available_agents = {
                    agent_id: agent for agent_id, agent in self.agent_manager.agents.items()
                    if agent.status in [AgentStatus.RUNNING, AgentStatus.IDLE]
                }
                
                # Optimize team composition
                team_members, performance_prediction = self.composition_optimizer.optimize_team_composition(
                    workload, available_agents
                )
                
                if not team_members:
                    logger.warning(f"No suitable team found for workload {workload.request_id}")
                    return
                
                # Create team
                team_id = str(uuid.uuid4())[:8]
                team_info = {
                    "team_id": team_id,
                    "workload": workload,
                    "members": team_members,
                    "formation_time": datetime.now(),
                    "status": "active",
                    "performance_prediction": performance_prediction
                }
                
                self.workload_scheduler.active_teams[team_id] = team_info
                
                # Assign workload to team members
                for agent_id in team_members:
                    task_assignment = {
                        "task_id": f"{workload.request_id}_{agent_id}",
                        "workload_id": workload.request_id,
                        "team_id": team_id,
                        "capabilities_required": self._get_capabilities_for_agent(agent_id, workload),
                        "deadline": workload.deadline,
                        "estimated_duration": workload.estimated_effort_hours / len(team_members)
                    }
                    
                    self.agent_manager.assign_task(agent_id, task_assignment)
                
                # Update metrics
                self.orchestration_metrics["workloads_processed"] += 1
                self.orchestration_metrics["teams_formed"] += 1
                
                logger.info(f"Formed team {team_id} with {len(team_members)} agents for workload {workload.request_id}")
                
            except Exception as e:
                logger.error(f"Error processing workload {workload.request_id}: {str(e)}")
    
    def _get_capabilities_for_agent(self, agent_id: str, workload: WorkloadRequest) -> List[str]:
        """Get required capabilities for a specific agent in the workload"""
        agent = self.agent_manager.agents.get(agent_id)
        if not agent:
            return []
        
        # Match agent capabilities with workload requirements
        required_skills = set(workload.required_skills)
        agent_capabilities = {cap.name.lower() for cap in agent.capabilities}
        
        matched_skills = [skill for skill in required_skills if skill.lower() in agent_capabilities]
        return matched_skills if matched_skills else ["general"]
    
    def _update_specializations(self):
        """Update agent specializations based on performance patterns"""
        # This would analyze recent task results and update agent capabilities
        # For now, we'll simulate the process
        logger.debug("Updating agent specializations...")
    
    def _cleanup_completed_teams(self):
        """Clean up completed teams and record performance"""
        completed_teams = []
        
        for team_id, team_info in list(self.workload_scheduler.active_teams.items()):
            # Check if team workload is complete
            workload_complete = self._check_workload_completion(team_info)
            
            if workload_complete:
                completed_teams.append(team_id)
                
                # Record team performance
                performance_record = {
                    "team_id": team_id,
                    "workload_id": team_info["workload"].request_id,
                    "formation_time": team_info["formation_time"],
                    "completion_time": datetime.now(),
                    "members": team_info["members"],
                    "status": "completed"
                }
                
                self.workload_scheduler.completed_workloads.append(performance_record)
                logger.info(f"Team {team_id} workload completed")
        
        # Remove completed teams
        for team_id in completed_teams:
            del self.workload_scheduler.active_teams[team_id]
    
    def _check_workload_completion(self, team_info: Dict[str, Any]) -> bool:
        """Check if a team's workload is complete"""
        # Simplified completion check - in reality, this would involve checking task status
        # For now, we'll simulate completion after some time
        formation_time = team_info["formation_time"]
        time_elapsed = (datetime.now() - formation_time).total_seconds()
        
        # Simulate completion after 2-10 minutes
        return time_elapsed > (120 + (len(team_info["members"]) * 60))  # Variable completion time
    
    def submit_research_workload(self, description: str, domain: SpecializationDomain, 
                                priority: int = 5, estimated_hours: float = 8.0) -> str:
        """Submit a research workload"""
        request_id = str(uuid.uuid4())[:8]
        
        workload = WorkloadRequest(
            request_id=request_id,
            workload_type=WorkloadType.RESEARCH_PROJECT,
            domain=domain,
            priority=priority,
            description=description,
            required_skills=["research", "analysis", "documentation"],
            estimated_effort_hours=estimated_hours
        )
        
        self.workload_scheduler.submit_workload(workload)
        return request_id
    
    def submit_development_workload(self, description: str, domain: SpecializationDomain,
                                  requirements: List[str], priority: int = 3, 
                                  estimated_hours: float = 16.0) -> str:
        """Submit a development workload"""
        request_id = str(uuid.uuid4())[:8]
        
        workload = WorkloadRequest(
            request_id=request_id,
            workload_type=WorkloadType.DEVELOPMENT_SPRINT,
            domain=domain,
            priority=priority,
            description=description,
            required_skills=requirements,
            estimated_effort_hours=estimated_hours
        )
        
        self.workload_scheduler.submit_workload(workload)
        return request_id
    
    def submit_emergency_workload(self, description: str, incident_type: str,
                                priority: int = 1, estimated_hours: float = 4.0) -> str:
        """Submit an emergency response workload"""
        request_id = str(uuid.uuid4())[:8]
        
        workload = WorkloadRequest(
            request_id=request_id,
            workload_type=WorkloadType.EMERGENCY_RESPONSE,
            domain=SpecializationDomain.SECURITY_AUDITING,  # Default for emergencies
            priority=priority,
            description=f"Emergency: {description} ({incident_type})",
            required_skills=["incident_response", "diagnostic", "resolution"],
            estimated_effort_hours=estimated_hours
        )
        
        self.workload_scheduler.submit_workload(workload)
        return request_id
    
    def get_orchestration_status(self) -> Dict[str, Any]:
        """Get current orchestration status"""
        active_workloads = len(self.workload_scheduler.active_teams)
        pending_workloads = len(self.workload_scheduler.pending_workloads)
        completed_workloads = len(self.workload_scheduler.completed_workloads)
        
        # Calculate average team size
        if self.orchestration_metrics["teams_formed"] > 0:
            self.orchestration_metrics["avg_team_size"] = (
                sum(len(team["members"]) for team in self.workload_scheduler.active_teams.values()) +
                sum(len(record["members"]) for record in self.workload_scheduler.completed_workloads)
            ) / max(1, self.orchestration_metrics["teams_formed"])
        
        return {
            "orchestrator_running": self.orchestrator_running,
            "active_teams": active_workloads,
            "pending_workloads": pending_workloads,
            "completed_workloads": completed_workloads,
            "metrics": self.orchestration_metrics.copy(),
            "active_team_details": {
                team_id: {
                    "workload_type": team_info["workload"].workload_type.value,
                    "members_count": len(team_info["members"]),
                    "formation_time": team_info["formation_time"].isoformat()
                }
                for team_id, team_info in self.workload_scheduler.active_teams.items()
            }
        }
    
    def get_team_analytics(self) -> Dict[str, Any]:
        """Get comprehensive team analytics"""
        # Analyze team composition patterns
        workload_type_distribution = defaultdict(int)
        domain_distribution = defaultdict(int)
        team_size_distribution = defaultdict(int)
        
        # Analyze active and completed teams
        all_teams = list(self.workload_scheduler.active_teams.values())
        all_teams.extend(list(self.workload_scheduler.completed_workloads))
        
        for team in all_teams:
            if "workload" in team:
                # Active team
                workload = team["workload"]
                workload_type_distribution[workload.workload_type.value] += 1
                domain_distribution[workload.domain.value] += 1
                team_size_distribution[len(team["members"])] += 1
            else:
                # Completed team
                if "workload_type" in team:  # Simplified for completed records
                    workload_type_distribution["research_project"] += 1  # Default
                    team_size_distribution[len(team["members"])] += 1
        
        return {
            "workload_type_distribution": dict(workload_type_distribution),
            "domain_distribution": dict(domain_distribution),
            "team_size_distribution": dict(team_size_distribution),
            "performance_trends": self._analyze_performance_trends(),
            "optimization_recommendations": self._generate_optimization_recommendations()
        }
    
    def _analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        # Simplified performance analysis
        return {
            "recent_success_rate": 0.85,
            "trend": "improving",
            "avg_completion_time": 6.2,  # hours
            "trend_direction": "decreasing"  # faster completion times
        }
    
    def _generate_optimization_recommendations(self) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Analyze workload distribution
        if len(self.workload_scheduler.pending_workloads) > 10:
            recommendations.append("High workload queue detected - consider scaling up agent pool")
        
        # Analyze team composition
        avg_team_size = self.orchestration_metrics.get("avg_team_size", 0)
        if avg_team_size < 3:
            recommendations.append("Teams may be too small - consider larger team compositions")
        elif avg_team_size > 7:
            recommendations.append("Teams may be too large - consider smaller, more focused teams")
        
        # Analyze specialization effectiveness
        if self.orchestration_metrics["success_rate"] < 0.8:
            recommendations.append("Low success rate detected - review specialization and team formation logic")
        
        return recommendations

def main():
    """Main function for testing"""
    from ..core.enhanced_agent_manager import EnhancedAgentManager
    
    # Initialize with a basic agent manager (would be connected to real instance in production)
    print("Dynamic Team Orchestrator - Demo Mode")
    print("In production, this would connect to a real EnhancedAgentManager instance")
    print("\\nTo use in production:")
    print("1. Start an EnhancedAgentManager instance")
    print("2. Pass it to DynamicTeamOrchestrator(agent_manager)")
    print("3. Call orchestrator.start_orchestration()")

if __name__ == "__main__":
    main()