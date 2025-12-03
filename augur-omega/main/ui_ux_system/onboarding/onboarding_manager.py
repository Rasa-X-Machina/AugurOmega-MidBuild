"""
Augur Omega: Onboarding System
Comprehensive onboarding based on company size, type, industry, and user mode
"""
import json
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import logging


class CompanySize(Enum):
    """Company sizes for onboarding"""
    MICRO_STARTUP = "micro_startup"      # <10 people
    SMALL_STARTUP = "small_startup"      # 10-50 people
    MEDIUM_ENTERPRISE = "medium_enterprise"  # 50-250 people
    LARGE_ENTERPRISE = "large_enterprise"    # 250+ people
    SOLO_ENTREPRENEUR = "solo_entrepreneur"  # Individual


class CompanyType(Enum):
    """Types of companies"""
    AGENCY = "agency"
    CONSULTING_FIRM = "consulting_firm"
    TECH_COMPANY = "tech_company"
    FINANCIAL_SERVICES = "financial_services"
    HEALTHCARE = "healthcare"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    EDUCATION = "education"
    NON_PROFIT = "non_profit"
    GOVERNMENT = "government"
    OTHER = "other"


class Industry(Enum):
    """Industries for onboarding"""
    TECHNOLOGY = "technology"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    EDUCATION = "education"
    GOVERNMENT = "government"
    MEDIA = "media"
    ENERGY = "energy"
    TRANSPORTATION = "transportation"
    HOSPITALITY = "hospitality"
    REAL_ESTATE = "real_estate"
    TELECOMMUNICATIONS = "telecommunications"
    AGRICULTURE = "agriculture"
    AUTOMOTIVE = "automotive"
    AEROSPACE = "aerospace"
    PHARMACEUTICALS = "pharmaceuticals"
    BIOTECH = "biotech"
    RENEWABLE_ENERGY = "renewable_energy"
    CYBERSECURITY = "cybersecurity"
    ARTIFICIAL_INTELLIGENCE = "artificial_intelligence"
    BLOCKCHAIN = "blockchain"
    GAMING = "gaming"
    ECOMMERCE = "ecommerce"
    SOCIAL_MEDIA = "social_media"
    INSURANCE = "insurance"
    LOGISTICS = "logistics"
    CONSULTING = "consulting"
    LEGAL = "legal"
    MARKETING = "marketing"
    DESIGN = "design"
    CONSTRUCTION = "construction"
    MINING = "mining"


class UserMode(Enum):
    """User modes for onboarding"""
    TEAM = "team"
    INDIVIDUAL = "individual"


class OnboardingStage(Enum):
    """Stages in the onboarding process"""
    WELCOME = "welcome"
    COMPANY_SIZE = "company_size"
    COMPANY_TYPE = "company_type"
    INDUSTRY = "industry"
    USER_MODE = "user_mode"
    KOSHA_SELECTION = "kosha_selection"
    CUSTOMIZATION = "customization"
    REVIEW = "review"
    COMPLETION = "completion"


@dataclass
class OnboardingProfile:
    """User's onboarding profile"""
    user_id: str
    stage: OnboardingStage = OnboardingStage.WELCOME
    company_size: Optional[CompanySize] = None
    company_type: Optional[CompanyType] = None
    industry: Optional[Industry] = None
    user_mode: Optional[UserMode] = None
    kosha_option: Optional[str] = None  # full, bundle, custom, single
    selected_koshas: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    locale: str = "en-US"


@dataclass
class OnboardingStep:
    """Definition of an onboarding step"""
    stage: OnboardingStage
    title: str
    description: str
    fields: List[Dict[str, Any]]  # Each field has name, type, options, etc.
    next_stages: List[OnboardingStage]
    requirements: List[str]  # What needs to be completed before this step
    recommended_koshas: List[str] = field(default_factory=list)


class OnboardingManager:
    """Manages the onboarding process for users"""
    
    def __init__(self):
        self.profiles: Dict[str, OnboardingProfile] = {}
        self.steps = self._initialize_steps()
        self.kosha_catalog = self._initialize_kosha_catalog()
        self.localization = self._initialize_localization()
        
        logging.info("Onboarding system initialized")
    
    def _initialize_steps(self) -> List[OnboardingStep]:
        """Initialize the onboarding steps"""
        return [
            OnboardingStep(
                stage=OnboardingStage.WELCOME,
                title="Welcome to Augur Omega",
                description="Welcome to the Augur Omega platform. Let's get you set up with the right configuration for your needs.",
                fields=[],
                next_stages=[OnboardingStage.COMPANY_SIZE],
                requirements=[]
            ),
            OnboardingStep(
                stage=OnboardingStage.COMPANY_SIZE,
                title="Company Size",
                description="Select the size of your company to get tailored recommendations",
                fields=[
                    {
                        "name": "company_size",
                        "type": "radio",
                        "options": [
                            {"value": "micro_startup", "label": "Micro Startup (<10 people)"},
                            {"value": "small_startup", "label": "Small Startup (10-50 people)"},
                            {"value": "medium_enterprise", "label": "Medium Enterprise (50-250 people)"},
                            {"value": "large_enterprise", "label": "Large Enterprise (250+ people)"},
                            {"value": "solo_entrepreneur", "label": "Solo Entrepreneur"}
                        ]
                    }
                ],
                next_stages=[OnboardingStage.COMPANY_TYPE],
                requirements=[]
            ),
            OnboardingStep(
                stage=OnboardingStage.COMPANY_TYPE,
                title="Company Type",
                description="What type of organization are you?",
                fields=[
                    {
                        "name": "company_type",
                        "type": "radio",
                        "options": [
                            {"value": "agency", "label": "Agency"},
                            {"value": "consulting_firm", "label": "Consulting Firm"},
                            {"value": "tech_company", "label": "Technology Company"},
                            {"value": "financial_services", "label": "Financial Services"},
                            {"value": "healthcare", "label": "Healthcare"},
                            {"value": "retail", "label": "Retail"},
                            {"value": "manufacturing", "label": "Manufacturing"},
                            {"value": "education", "label": "Education"},
                            {"value": "non_profit", "label": "Non-Profit"},
                            {"value": "government", "label": "Government"},
                            {"value": "other", "label": "Other"}
                        ]
                    }
                ],
                next_stages=[OnboardingStage.INDUSTRY],
                requirements=["company_size"]
            ),
            OnboardingStep(
                stage=OnboardingStage.INDUSTRY,
                title="Industry",
                description="What industry does your company operate in?",
                fields=[
                    {
                        "name": "industry",
                        "type": "radio",
                        "options": [
                            {"value": "technology", "label": "Technology"},
                            {"value": "finance", "label": "Finance"},
                            {"value": "healthcare", "label": "Healthcare"},
                            {"value": "retail", "label": "Retail"},
                            {"value": "manufacturing", "label": "Manufacturing"},
                            {"value": "education", "label": "Education"},
                            {"value": "government", "label": "Government"},
                            {"value": "media", "label": "Media"},
                            {"value": "energy", "label": "Energy"},
                            {"value": "telecommunications", "label": "Telecommunications"},
                            {"value": "gaming", "label": "Gaming"},
                            {"value": "artificial_intelligence", "label": "Artificial Intelligence"},
                            {"value": "blockchain", "label": "Blockchain"},
                            {"value": "cybersecurity", "label": "Cybersecurity"},
                            {"value": "renewable_energy", "label": "Renewable Energy"},
                            {"value": "other", "label": "Other"}
                        ]
                    }
                ],
                next_stages=[OnboardingStage.USER_MODE],
                requirements=["company_size", "company_type"]
            ),
            OnboardingStep(
                stage=OnboardingStage.USER_MODE,
                title="User Mode",
                description="Are you setting up for a team or for individual use?",
                fields=[
                    {
                        "name": "user_mode",
                        "type": "radio",
                        "options": [
                            {"value": "team", "label": "Team Mode"},
                            {"value": "individual", "label": "Individual Mode"}
                        ]
                    }
                ],
                next_stages=[OnboardingStage.KOSHA_SELECTION],
                requirements=["company_size", "company_type", "industry"]
            ),
            OnboardingStep(
                stage=OnboardingStage.KOSHA_SELECTION,
                title="Kosha Selection",
                description="Choose your kosha configuration option",
                fields=[
                    {
                        "name": "kosha_option",
                        "type": "radio",
                        "options": [
                            {"value": "full_kosha_offering", "label": "Full Kosha Offering"},
                            {"value": "kosha_bundle", "label": "Kosha Bundle"},
                            {"value": "custom_kosha_selection", "label": "Custom Kosha Selection"},
                            {"value": "single_kosha", "label": "Single Kosha"}
                        ]
                    }
                ],
                next_stages=[OnboardingStage.CUSTOMIZATION, OnboardingStage.REVIEW],
                requirements=["company_size", "company_type", "industry", "user_mode"]
            ),
            OnboardingStep(
                stage=OnboardingStage.CUSTOMIZATION,
                title="Customization",
                description="Customize your selected koshas",
                fields=[
                    {
                        "name": "selected_koshas",
                        "type": "checkbox",
                        "options": []  # Will be populated dynamically based on selection
                    }
                ],
                next_stages=[OnboardingStage.REVIEW],
                requirements=["company_size", "company_type", "industry", "user_mode", "kosha_option"],
                recommended_koshas=[]
            ),
            OnboardingStep(
                stage=OnboardingStage.REVIEW,
                title="Review Your Setup",
                description="Review your selections before completing setup",
                fields=[
                    {
                        "name": "confirmation",
                        "type": "checkbox",
                        "options": [{"value": "confirmed", "label": "I confirm these selections"}]
                    }
                ],
                next_stages=[OnboardingStage.COMPLETION],
                requirements=["company_size", "company_type", "industry", "user_mode", "kosha_option"]
            ),
            OnboardingStep(
                stage=OnboardingStage.COMPLETION,
                title="Setup Complete",
                description="Your Augur Omega configuration is ready!",
                fields=[],
                next_stages=[],
                requirements=["all"]
            )
        ]
    
    def _initialize_kosha_catalog(self) -> Dict[str, Dict[str, Any]]:
        """Initialize the kosha catalog with information for different profiles"""
        return {
            # Prime Koshas
            "PRIME_STRATEGY": {
                "name": "Strategic Planning",
                "description": "Strategic planning and execution oversight",
                "categories": ["prime_kosha"],
                "suitable_for": {
                    "company_sizes": [CompanySize.LARGE_ENTERPRISE, CompanySize.MEDIUM_ENTERPRISE],
                    "industries": [Industry.TECHNOLOGY, Industry.FINANCE, Industry.CONSULTING],
                    "company_types": [CompanyType.CONSULTING_FIRM, CompanyType.TECH_COMPANY]
                }
            },
            "PRIME_CONSCIOUSNESS": {
                "name": "Consciousness & Awareness",
                "description": "System consciousness and awareness protocols",
                "categories": ["prime_kosha"],
                "suitable_for": {
                    "company_sizes": [CompanySize.ALL],
                    "industries": [Industry.ALL],
                    "company_types": [CompanyType.ALL]
                }
            },
            
            # Domain Koshas by industry
            "DOMAIN_TECH": {
                "name": "Technical Implementation",
                "description": "Technical architecture and implementation",
                "categories": ["domain_kosha"],
                "suitable_for": {
                    "company_sizes": [CompanySize.ALL],
                    "industries": [Industry.TECHNOLOGY, Industry.ARTIFICIAL_INTELLIGENCE, Industry.CYBERSECURITY],
                    "company_types": [CompanyType.TECH_COMPANY]
                }
            },
            "DOMAIN_FINANCE": {
                "name": "Financial Management",
                "description": "Financial planning and management",
                "categories": ["domain_kosha"],
                "suitable_for": {
                    "company_sizes": [CompanySize.MEDIUM_ENTERPRISE, CompanySize.LARGE_ENTERPRISE],
                    "industries": [Industry.FINANCE, Industry.INSURANCE],
                    "company_types": [CompanyType.FINANCIAL_SERVICES]
                }
            },
            "DOMAIN_HEALTHCARE": {
                "name": "Healthcare Compliance",
                "description": "Healthcare regulations and compliance",
                "categories": ["domain_kosha"],
                "suitable_for": {
                    "company_sizes": [CompanySize.MEDIUM_ENTERPRISE, CompanySize.LARGE_ENTERPRISE],
                    "industries": [Industry.HEALTHCARE],
                    "company_types": [CompanyType.HEALTHCARE]
                }
            },
            "DOMAIN_GAMING": {
                "name": "Gaming Analytics",
                "description": "Gaming user behavior and monetization",
                "categories": ["domain_kosha"],
                "suitable_for": {
                    "company_sizes": [CompanySize.SMALL_STARTUP, CompanySize.MEDIUM_ENTERPRISE],
                    "industries": [Industry.GAMING],
                    "company_types": [CompanyType.TECH_COMPANY]
                }
            },
            
            # Microagents
            "MICRO_DATA": {
                "name": "Data Processing",
                "description": "Data processing and analysis",
                "categories": ["microagent"],
                "suitable_for": {
                    "company_sizes": [CompanySize.ALL],
                    "industries": [Industry.ALL],
                    "company_types": [CompanyType.ALL]
                }
            },
            "MICRO_REPORTING": {
                "name": "Reporting & Analytics",
                "description": "Reporting and analytics generation",
                "categories": ["microagent"],
                "suitable_for": {
                    "company_sizes": [CompanySize.ALL],
                    "industries": [Industry.ALL],
                    "company_types": [CompanyType.ALL]
                }
            },
            "MICRO_SECURITY": {
                "name": "Security Monitoring",
                "description": "Security monitoring and threat detection",
                "categories": ["microagent"],
                "suitable_for": {
                    "company_sizes": [CompanySize.ALL],
                    "industries": [Industry.CYBERSECURITY, Industry.FINANCE, Industry.HEALTHCARE],
                    "company_types": [CompanyType.TECH_COMPANY, CompanyType.FINANCIAL_SERVICES, CompanyType.HEALTHCARE]
                }
            }
        }
    
    def _initialize_localization(self) -> Dict[str, Dict[str, str]]:
        """Initialize localization for onboarding content"""
        return {
            "en-US": {
                "welcome_title": "Welcome to Augur Omega",
                "welcome_desc": "Let's configure your system based on your organization's needs",
                "company_size_title": "Company Size",
                "company_size_desc": "Select your company size for tailored recommendations",
                "next": "Next",
                "previous": "Previous",
                "skip": "Skip",
                "finish": "Finish"
            },
            "zh-CN": {
                "welcome_title": "欢迎使用奥古欧米茄",
                "welcome_desc": "根据您的组织需求配置系统",
                "company_size_title": "公司规模",
                "company_size_desc": "选择公司规模以获得定制推荐",
                "next": "下一步",
                "previous": "上一步",
                "skip": "跳过",
                "finish": "完成"
            },
            "es-ES": {
                "welcome_title": "Bienvenido a Augur Omega",
                "welcome_desc": "Configuremos su sistema según las necesidades de su organización",
                "company_size_title": "Tamaño de la Empresa",
                "company_size_desc": "Seleccione el tamaño de su empresa para recomendaciones personalizadas",
                "next": "Siguiente",
                "previous": "Anterior",
                "skip": "Saltar",
                "finish": "Finalizar"
            },
            "ja-JP": {
                "welcome_title": "オーガーオメガへようこそ",
                "welcome_desc": "組織のニーズに応じてシステムを構成しましょう",
                "company_size_title": "会社規模",
                "company_size_desc": "カスタマイズされたレコメンデーションのために会社規模を選択してください",
                "next": "次へ",
                "previous": "前へ",
                "skip": "スキップ",
                "finish": "完了"
            }
        }
    
    def start_onboarding(self, user_id: str, locale: str = "en-US") -> OnboardingProfile:
        """Start the onboarding process for a user"""
        profile = OnboardingProfile(
            user_id=user_id,
            locale=locale
        )
        self.profiles[user_id] = profile
        return profile
    
    def get_profile(self, user_id: str) -> Optional[OnboardingProfile]:
        """Get the onboarding profile for a user"""
        return self.profiles.get(user_id)
    
    def update_profile(self, user_id: str, **kwargs) -> bool:
        """Update the onboarding profile with new information"""
        if user_id not in self.profiles:
            return False
        
        profile = self.profiles[user_id]
        
        # Update profile with provided information
        for key, value in kwargs.items():
            if hasattr(profile, key):
                if key == 'company_size' and isinstance(value, str):
                    try:
                        setattr(profile, key, CompanySize(value))
                    except ValueError:
                        return False
                elif key == 'company_type' and isinstance(value, str):
                    try:
                        setattr(profile, key, CompanyType(value))
                    except ValueError:
                        return False
                elif key == 'industry' and isinstance(value, str):
                    try:
                        setattr(profile, key, Industry(value))
                    except ValueError:
                        return False
                elif key == 'user_mode' and isinstance(value, str):
                    try:
                        setattr(profile, key, UserMode(value))
                    except ValueError:
                        return False
                else:
                    setattr(profile, key, value)
        
        return True
    
    def get_current_step(self, user_id: str) -> Optional[OnboardingStep]:
        """Get the current onboarding step for a user"""
        profile = self.get_profile(user_id)
        if not profile:
            return None
        
        # Find the step matching the current stage
        for step in self.steps:
            if step.stage == profile.stage:
                return step
        return None
    
    def get_recommendations(self, profile: OnboardingProfile) -> List[str]:
        """Get recommended koshas based on the user's profile"""
        recommendations = []
        
        if not all([profile.company_size, profile.industry, profile.company_type]):
            return recommendations
        
        # Filter koshas based on user profile
        for kosha_id, kosha_info in self.kosha_catalog.items():
            suitable = True
            
            # Check company size suitability
            if profile.company_size not in kosha_info["suitable_for"]["company_sizes"] and \
               "ALL" not in [cs.value for cs in kosha_info["suitable_for"]["company_sizes"]]:
                suitable = False
            
            # Check industry suitability
            if profile.industry.value not in [ind.value for ind in kosha_info["suitable_for"]["industries"]] and \
               "ALL" not in [ind.value for ind in kosha_info["suitable_for"]["industries"]]:
                suitable = False
            
            # Check company type suitability
            if profile.company_type not in kosha_info["suitable_for"]["company_types"] and \
               "ALL" not in [ct.value for ct in kosha_info["suitable_for"]["company_types"]]:
                suitable = False
            
            if suitable:
                recommendations.append(kosha_id)
        
        return recommendations
    
    def advance_stage(self, user_id: str) -> bool:
        """Advance to the next onboarding stage"""
        profile = self.get_profile(user_id)
        if not profile:
            return False
        
        current_step = self.get_current_step(user_id)
        if not current_step or not current_step.next_stages:
            return False
        
        # Determine the appropriate next stage based on profile
        if profile.stage == OnboardingStage.KOSHA_SELECTION:
            # If user selected custom kosha selection, go to customization
            if profile.kosha_option == "custom_kosha_selection":
                profile.stage = OnboardingStage.CUSTOMIZATION
            else:
                # Otherwise go to review
                profile.stage = OnboardingStage.REVIEW
        else:
            # Default behavior - go to first next stage
            profile.stage = current_step.next_stages[0]
        
        # If we've reached completion, update completion time
        if profile.stage == OnboardingStage.COMPLETION:
            profile.completed_at = datetime.now().isoformat()
        
        return True
    
    def get_available_koshas(self, profile: OnboardingProfile) -> List[Dict[str, Any]]:
        """Get list of available koshas for selection based on profile"""
        if not all([profile.company_size, profile.industry, profile.company_type]):
            # Return all koshas if profile is incomplete
            return [{"id": k, "name": v["name"], "description": v["description"]} 
                    for k, v in self.kosha_catalog.items()]
        
        # Otherwise, return only suitable koshas
        suitable_koshas = []
        for kosha_id, kosha_info in self.kosha_catalog.items():
            suitable = True
            
            # Check company size suitability
            if profile.company_size not in kosha_info["suitable_for"]["company_sizes"] and \
               "ALL" not in [cs.value for cs in kosha_info["suitable_for"]["company_sizes"]]:
                suitable = False
            
            # Check industry suitability
            if profile.industry.value not in [ind.value for ind in kosha_info["suitable_for"]["industries"]] and \
               "ALL" not in [ind.value for ind in kosha_info["suitable_for"]["industries"]]:
                suitable = False
            
            # Check company type suitability
            if profile.company_type not in kosha_info["suitable_for"]["company_types"] and \
               "ALL" not in [ct.value for ct in kosha_info["suitable_for"]["company_types"]]:
                suitable = False
            
            if suitable:
                suitable_koshas.append({
                    "id": kosha_id,
                    "name": kosha_info["name"],
                    "description": kosha_info["description"],
                    "categories": kosha_info["categories"]
                })
        
        return suitable_koshas
    
    def get_localized_text(self, user_id: str, key: str) -> str:
        """Get localized text for the user"""
        profile = self.get_profile(user_id)
        locale = profile.locale if profile else "en-US"
        
        return self.localization.get(locale, {}).get(key, self.localization["en-US"].get(key, key))
    
    def complete_onboarding(self, user_id: str) -> Dict[str, Any]:
        """Complete the onboarding process and return final configuration"""
        profile = self.get_profile(user_id)
        if not profile or profile.stage != OnboardingStage.COMPLETION:
            return {}
        
        # Generate a configuration based on the user's selections
        configuration = {
            "user_id": profile.user_id,
            "setup_date": profile.completed_at,
            "company_profile": {
                "size": profile.company_size.value if profile.company_size else None,
                "type": profile.company_type.value if profile.company_type else None,
                "industry": profile.industry.value if profile.industry else None,
                "mode": profile.user_mode.value if profile.user_mode else None
            },
            "kosha_configuration": {
                "option": profile.kosha_option,
                "selected_koshas": profile.selected_koshas,
                "recommendations_followed": len(profile.selected_koshas) > 0
            },
            "preferences": profile.preferences
        }
        
        return configuration


def create_onboarding_demo():
    """Create a demo of the onboarding system"""
    print("=== Augur Omega: Onboarding System Demo ===\n")
    
    # Initialize the onboarding manager
    onboarding = OnboardingManager()
    
    # Create a new user profile
    user_id = "demo_user_001"
    profile = onboarding.start_onboarding(user_id)
    print(f"Started onboarding for user: {user_id}\n")
    
    # Show initial stage
    current_step = onboarding.get_current_step(user_id)
    print(f"Current stage: {current_step.stage.value} - {current_step.title}\n")
    
    # Progress through onboarding steps
    print("1. Setting company size to Small Startup:")
    onboarding.update_profile(user_id, company_size=CompanySize.SMALL_STARTUP)
    print(f"   Updated company size: {onboarding.get_profile(user_id).company_size.value}\n")
    
    print("2. Setting company type to Tech Company:")
    onboarding.update_profile(user_id, company_type=CompanyType.TECH_COMPANY)
    print(f"   Updated company type: {onboarding.get_profile(user_id).company_type.value}\n")
    
    print("3. Setting industry to Technology:")
    onboarding.update_profile(user_id, industry=Industry.TECHNOLOGY)
    print(f"   Updated industry: {onboarding.get_profile(user_id).industry.value}\n")
    
    print("4. Setting user mode to Team:")
    onboarding.update_profile(user_id, user_mode=UserMode.TEAM)
    print(f"   Updated user mode: {onboarding.get_profile(user_id).user_mode.value}\n")
    
    print("5. Setting kosha option to Custom Selection:")
    onboarding.update_profile(user_id, kosha_option="custom_kosha_selection")
    print(f"   Updated kosha option: {onboarding.get_profile(user_id).kosha_option}\n")
    
    print("6. Getting available koshas for this profile:")
    available_koshas = onboarding.get_available_koshas(onboarding.get_profile(user_id))
    for kosha in available_koshas:
        print(f"   - {kosha['name']}: {kosha['description']}")
    print()
    
    print("7. Getting recommendations for this profile:")
    recommendations = onboarding.get_recommendations(onboarding.get_profile(user_id))
    for rec in recommendations:
        print(f"   - {rec}")
    print()
    
    print("8. Selecting koshas:")
    onboarding.update_profile(user_id, selected_koshas=["DOMAIN_TECH", "MICRO_DATA", "MICRO_SECURITY"])
    print(f"   Selected koshas: {onboarding.get_profile(user_id).selected_koshas}\n")
    
    print("9. Advancing through the remaining stages:")
    for _ in range(4):  # Advance several stages
        if onboarding.advance_stage(user_id):
            profile = onboarding.get_profile(user_id)
            print(f"   Advanced to stage: {profile.stage.value}")
    
    print()
    
    print("10. Completing onboarding:")
    onboarding.advance_stage(user_id)  # This should complete onboarding
    config = onboarding.complete_onboarding(user_id)
    print(f"    Configuration: {json.dumps(config, indent=2)}\n")
    
    print("Onboarding system demo completed!")


if __name__ == "__main__":
    create_onboarding_demo()