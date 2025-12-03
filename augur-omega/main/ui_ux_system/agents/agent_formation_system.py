"""
Augur Omega: Agent Formation System
Optimizes agent teams for mathematical efficiency and subject matter expertise
"""
import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import numpy as np
from scipy.optimize import linear_sum_assignment


class AgentType(Enum):
    """Types of agents based on subject matter expertise"""
    PRIME_KOSHA = "prime_kosha"        # Strategic/Consciousness agents
    DOMAIN_KOSHA = "domain_kosha"      # Domain-specific agents
    MICROAGENT = "microagent"          # Task-specific agents
    SPECIALIZED = "specialized"        # Expert agents


@dataclass
class Agent:
    """Represents an individual agent with capabilities and expertise"""
    id: str
    agent_type: AgentType
    expertise_score: float  # 0.0 to 1.0
    efficiency_score: float  # 0.0 to 1.0
    domain_expertise: List[str]  # List of specialized domains
    computational_capacity: int  # Processing power rating
    communication_latency: float  # Network efficiency rating
    availability: bool = True


@dataclass
class Task:
    """Represents a task requiring agent allocation"""
    id: str
    complexity: float  # 0.0 to 1.0
    domain_requirements: List[str]  # Required expertise domains
    priority: int  # Priority level
    estimated_duration: float  # Estimated completion time


class AgentFormationOptimizer:
    """Manages optimal formation of agent teams based on mathematical efficiency and expertise"""
    
    def __init__(self):
        self.agents: List[Agent] = []
        self.tasks: List[Task] = []
        self.formation_matrix: Optional[np.ndarray] = None
    
    def add_agent(self, agent: Agent):
        """Add an agent to the pool"""
        self.agents.append(agent)
    
    def add_task(self, task: Task):
        """Add a task to the queue"""
        self.tasks.append(task)
    
    def calculate_match_score(self, agent: Agent, task: Task) -> float:
        """Calculate how well an agent matches a task based on expertise and efficiency"""
        # Calculate domain expertise match
        domain_match = 0.0
        for required_domain in task.domain_requirements:
            if required_domain in agent.domain_expertise:
                domain_match += 1.0 / len(task.domain_requirements)
        
        # Calculate complexity fit
        complexity_fit = min(1.0, agent.expertise_score / task.complexity)
        
        # Calculate capacity utilization
        capacity_utilization = min(1.0, agent.computational_capacity / (task.complexity * 100))
        
        # Weighted combination of factors
        match_score = (
            0.4 * domain_match +
            0.3 * complexity_fit +
            0.2 * capacity_utilization +
            0.1 * agent.efficiency_score
        )
        
        return match_score * (1.0 - agent.communication_latency * 0.1)  # Factor in communication latency
    
    def form_optimal_teams(self) -> Dict[str, List[Agent]]:
        """
        Form optimal teams using mathematical optimization
        Returns a mapping of task IDs to assigned agents
        """
        if not self.tasks or not self.agents:
            return {}
        
        # Create assignment matrix
        assignment_matrix = np.zeros((len(self.tasks), len(self.agents)))
        
        for i, task in enumerate(self.tasks):
            for j, agent in enumerate(self.agents):
                if agent.availability:
                    assignment_matrix[i][j] = self.calculate_match_score(agent, task)
        
        # Use Hungarian algorithm to find optimal assignment
        row_indices, col_indices = linear_sum_assignment(-assignment_matrix)
        
        # Create assignment mapping
        assignments = {}
        for i, task_idx in enumerate(row_indices):
            agent_idx = col_indices[i]
            task_id = self.tasks[task_idx].id
            agent = self.agents[agent_idx]
            
            if task_id not in assignments:
                assignments[task_id] = []
            assignments[task_id].append(agent)
            
            # Mark agent as unavailable for other tasks
            self.agents[agent_idx].availability = False
        
        # Reset agent availability after assignment
        for agent in self.agents:
            agent.availability = True
            
        return assignments
    
    def calculate_formation_efficiency(self, assignments: Dict[str, List[Agent]]) -> float:
        """Calculate overall efficiency of the formed teams"""
        if not assignments:
            return 0.0
        
        total_efficiency = 0.0
        assignment_count = 0
        
        for task_id, assigned_agents in assignments.items():
            task = next((t for t in self.tasks if t.id == task_id), None)
            if not task:
                continue
            
            # Calculate efficiency for this task's team
            team_efficiency = 0.0
            for agent in assigned_agents:
                match_score = self.calculate_match_score(agent, task)
                team_efficiency += match_score
            
            # Average efficiency for this team
            avg_team_efficiency = team_efficiency / len(assigned_agents) if assigned_agents else 0.0
            total_efficiency += avg_team_efficiency
            assignment_count += 1
        
        overall_efficiency = total_efficiency / assignment_count if assignment_count > 0 else 0.0
        return overall_efficiency
    
    def optimize_by_expertise_cluster(self) -> Dict[str, List[Agent]]:
        """
        Group agents by expertise and form specialized clusters
        """
        expertise_clusters = {}
        
        # Group agents by their primary domain expertise
        for agent in self.agents:
            for domain in agent.domain_expertise:
                if domain not in expertise_clusters:
                    expertise_clusters[domain] = []
                expertise_clusters[domain].append(agent)
        
        # Assign tasks to appropriate clusters
        assignments = {}
        
        for task in self.tasks:
            cluster_agents = []
            
            # Find agents from relevant expertise clusters
            for domain in task.domain_requirements:
                if domain in expertise_clusters:
                    cluster_agents.extend(expertise_clusters[domain])
            
            # If no specific expertise found, use all available agents
            if not cluster_agents:
                cluster_agents = self.agents
            
            # Assign top-matching agents for this task
            task_assignments = []
            sorted_agents = sorted(
                cluster_agents,
                key=lambda a: self.calculate_match_score(a, task),
                reverse=True
            )
            
            # Assign top N agents based on task complexity
            num_agents_needed = max(1, int(task.complexity * 5))  # Complexity determines team size
            task_assignments = sorted_agents[:min(len(sorted_agents), num_agents_needed)]
            
            assignments[task.id] = task_assignments
        
        return assignments
    
    def calculate_mathematical_efficiency_metrics(self, assignments: Dict[str, List[Agent]]) -> Dict[str, float]:
        """Calculate various mathematical efficiency metrics"""
        metrics = {}
        
        # Calculate formation efficiency
        metrics['formation_efficiency'] = self.calculate_formation_efficiency(assignments)
        
        # Calculate resource utilization
        total_capacity = sum(agent.computational_capacity for agent in self.agents)
        allocated_capacity = 0
        for task_agents in assignments.values():
            allocated_capacity += sum(agent.computational_capacity for agent in task_agents)
        
        metrics['resource_utilization'] = allocated_capacity / total_capacity if total_capacity > 0 else 0.0
        
        # Calculate expertise saturation
        domain_utilization = {}
        for task_id, assigned_agents in assignments.items():
            task = next((t for t in self.tasks if t.id == task_id), None)
            if task:
                for domain in task.domain_requirements:
                    if domain not in domain_utilization:
                        domain_utilization[domain] = 0
                    domain_utilization[domain] += 1
        
        total_domains = len(domain_utilization)
        covered_domains = sum(1 for count in domain_utilization.values() if count > 0)
        metrics['domain_coverage'] = covered_domains / total_domains if total_domains > 0 else 0.0
        
        # Calculate specialization index
        total_agents = len(self.agents)
        specialized_agents = sum(1 for agent in self.agents if len(agent.domain_expertise) <= 2)
        metrics['specialization_index'] = specialized_agents / total_agents if total_agents > 0 else 0.0
        
        return metrics


def create_sample_agents() -> List[Agent]:
    """Create sample agents for demonstration"""
    agents = [
        Agent(
            id="PRIME_001",
            agent_type=AgentType.PRIME_KOSHA,
            expertise_score=0.95,
            efficiency_score=0.92,
            domain_expertise=["strategy", "consciousness", "meta-optimization"],
            computational_capacity=100,
            communication_latency=0.02
        ),
        Agent(
            id="DOMAIN_001",
            agent_type=AgentType.DOMAIN_KOSHA,
            expertise_score=0.85,
            efficiency_score=0.88,
            domain_expertise=["finance", "risk", "compliance"],
            computational_capacity=80,
            communication_latency=0.03
        ),
        Agent(
            id="DOMAIN_002",
            agent_type=AgentType.DOMAIN_KOSHA,
            expertise_score=0.87,
            efficiency_score=0.85,
            domain_expertise=["technology", "ai", "ml"],
            computational_capacity=85,
            communication_latency=0.04
        ),
        Agent(
            id="MICRO_001",
            agent_type=AgentType.MICROAGENT,
            expertise_score=0.70,
            efficiency_score=0.75,
            domain_expertise=["data_processing", "calculation", "validation"],
            computational_capacity=60,
            communication_latency=0.05
        ),
        Agent(
            id="MICRO_002",
            agent_type=AgentType.MICROAGENT,
            expertise_score=0.68,
            efficiency_score=0.72,
            domain_expertise=["reporting", "visualization", "ui_generation"],
            computational_capacity=55,
            communication_latency=0.06
        ),
        Agent(
            id="SPECIALIZED_001",
            agent_type=AgentType.SPECIALIZED,
            expertise_score=0.98,
            efficiency_score=0.90,
            domain_expertise=["mathematical_optimization", "algorithm_design", "complexity_analysis"],
            computational_capacity=90,
            communication_latency=0.02
        ),
        Agent(
            id="SPECIALIZED_002",
            agent_type=AgentType.SPECIALIZED,
            expertise_score=0.96,
            efficiency_score=0.89,
            domain_expertise=["security", "privacy", "encryption"],
            computational_capacity=88,
            communication_latency=0.03
        ),
        Agent(
            id="DOMAIN_003",
            agent_type=AgentType.DOMAIN_KOSHA,
            expertise_score=0.82,
            efficiency_score=0.84,
            domain_expertise=["hr", "organization", "collaboration"],
            computational_capacity=75,
            communication_latency=0.04
        )
    ]
    return agents


def create_sample_tasks() -> List[Task]:
    """Create sample tasks for demonstration"""
    tasks = [
        Task(
            id="TASK_001",
            complexity=0.9,
            domain_requirements=["strategy", "mathematical_optimization"],
            priority=1,
            estimated_duration=2.5
        ),
        Task(
            id="TASK_002",
            complexity=0.7,
            domain_requirements=["finance", "risk"],
            priority=2,
            estimated_duration=1.8
        ),
        Task(
            id="TASK_003",
            complexity=0.6,
            domain_requirements=["technology", "ai"],
            priority=3,
            estimated_duration=1.5
        ),
        Task(
            id="TASK_004",
            complexity=0.5,
            domain_requirements=["data_processing", "calculation"],
            priority=4,
            estimated_duration=1.0
        ),
        Task(
            id="TASK_005",
            complexity=0.8,
            domain_requirements=["security", "privacy"],
            priority=1,
            estimated_duration=2.0
        )
    ]
    return tasks


def demonstrate_agent_formation():
    """Demonstrate the agent formation optimization"""
    print("=== Augur Omega: Agent Formation Optimization ===\n")
    
    # Create sample agents and tasks
    agents = create_sample_agents()
    tasks = create_sample_tasks()
    
    # Initialize optimizer
    optimizer = AgentFormationOptimizer()
    
    # Add agents and tasks
    for agent in agents:
        optimizer.add_agent(agent)
    
    for task in tasks:
        optimizer.add_task(task)
    
    print(f"Available Agents: {len(agents)}")
    print(f"Tasks to Assign: {len(tasks)}\n")
    
    # Form optimal teams
    assignments = optimizer.form_optimal_teams()
    
    print("Optimal Agent Assignments:")
    for task_id, assigned_agents in assignments.items():
        print(f"\nTask {task_id}:")
        for agent in assigned_agents:
            print(f"  - {agent.id} ({agent.agent_type.value}) - Expertise: {agent.expertise_score:.2f}")
    
    # Calculate efficiency metrics
    metrics = optimizer.calculate_mathematical_efficiency_metrics(assignments)
    
    print(f"\nEfficiency Metrics:")
    print(f"  Formation Efficiency: {metrics['formation_efficiency']:.3f}")
    print(f"  Resource Utilization: {metrics['resource_utilization']:.3f}")
    print(f"  Domain Coverage: {metrics['domain_coverage']:.3f}")
    print(f"  Specialization Index: {metrics['specialization_index']:.3f}")
    
    # Form teams by expertise clusters
    print("\n" + "="*50)
    print("Expertise-Based Clustering Approach:")
    
    cluster_assignments = optimizer.optimize_by_expertise_cluster()
    
    print("Cluster-Based Agent Assignments:")
    for task_id, assigned_agents in cluster_assignments.items():
        print(f"\nTask {task_id}:")
        for agent in assigned_agents:
            print(f"  - {agent.id} ({agent.agent_type.value}) - Expertise: {[d for d in agent.domain_expertise if any(req in d for req in next(t.domain_requirements for t in tasks if t.id == task_id))]}")
    
    # Calculate metrics for cluster approach
    cluster_metrics = optimizer.calculate_mathematical_efficiency_metrics(cluster_assignments)
    
    print(f"\nCluster Approach Metrics:")
    print(f"  Formation Efficiency: {cluster_metrics['formation_efficiency']:.3f}")
    print(f"  Resource Utilization: {cluster_metrics['resource_utilization']:.3f}")
    
    return assignments, cluster_assignments, metrics, cluster_metrics


if __name__ == "__main__":
    demonstrate_agent_formation()