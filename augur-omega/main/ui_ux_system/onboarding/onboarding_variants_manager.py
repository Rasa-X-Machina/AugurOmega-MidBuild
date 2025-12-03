"""
Augur Omega: Onboarding Variants by Kosha Offering
Different onboarding experiences based on selected kosha offering type
"""
import json
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import logging
from .onboarding_manager import OnboardingManager, OnboardingStage, CompanySize, CompanyType, Industry, UserMode
from .onboarding_manager import OnboardingProfile, OnboardingStep


class KoshaOfferingType(Enum):
    """Types of kosha offerings"""
    FULL_KOSHA_OFFERING = "full_kosha_offering"
    KOSHA_BUNDLE = "kosha_bundle"
    CUSTOM_KOSHA_SELECTION = "custom_kosha_selection"
    SINGLE_KOSHA = "single_kosha"


class BundleType(Enum):
    """Types of kosha bundles"""
    STARTER_BUNDLE = "starter_bundle"
    GROWTH_BUNDLE = "growth_bundle"
    ENTERPRISE_BUNDLE = "enterprise_bundle"
    INDUSTRY_SPECIALIZED_BUNDLE = "industry_specialized_bundle"
    AI_AUTOMATION_BUNDLE = "ai_automation_bundle"
    COMPLIANCE_BUNDLE = "compliance_bundle"


@dataclass
class KoshaBundle:
    """Definition of a kosha bundle"""
    id: str
    name: str
    description: str
    koshas: List[str]
    target_audience: Dict[str, List[str]]  # company_sizes, industries, company_types
    pricing_tier: str
    recommended_for: str


@dataclass
class OfferingVariant:
    """Configuration for a specific offering variant"""
    offering_type: KoshaOfferingType
    name: str
    description: str
    onboarding_steps: List[OnboardingStage]
    required_steps: List[OnboardingStage]
    kosha_selection_options: List[Dict[str, Any]]
    default_koshas: List[str]
    advanced_options: bool
    customization_level: str  # none, basic, advanced
    recommended_bundles: List[BundleType]


@dataclass
class FullKoshaOfferingProfile:
    """Extended profile for full kosha offering"""
    base_profile: OnboardingProfile
    prime_koshas: List[str] = field(default_factory=list)
    domain_koshas: List[str] = field(default_factory=list)
    microagents: List[str] = field(default_factory=list)
    integration_level: str = "standard"  # basic, standard, advanced
    security_config: str = "standard"  # basic, standard, enterprise
    performance_config: str = "standard"  # low, medium, high


@dataclass
class BundleSelectionProfile:
    """Extended profile for bundle selection"""
    base_profile: OnboardingProfile
    selected_bundle: Optional[BundleType] = None
    bundle_customizations: Dict[str, Any] = field(default_factory=dict)
    additional_koshas: List[str] = field(default_factory=list)


@dataclass
class CustomSelectionProfile:
    """Extended profile for custom selection"""
    base_profile: OnboardingProfile
    selection_category: str = "all"  # prime, domain, microagent, all
    max_selections: int = 10
    selection_filter: str = "all"  # by_capability, by_industry, by_function


@dataclass
class SingleKoshaProfile:
    """Extended profile for single kosha selection"""
    base_profile: OnboardingProfile
    selected_kosha: Optional[str] = None
    integration_depth: str = "minimal"  # minimal, standard, deep
    support_level: str = "standard"  # basic, standard, premium


class OnboardingVariantsManager:
    """Manages different onboarding variants based on kosha offering type"""
    
    def __init__(self, base_onboarding_manager: OnboardingManager):
        self.base_manager = base_onboarding_manager
        self.variants = self._initialize_variants()
        self.bundles = self._initialize_bundles()
        self.extended_profiles: Dict[str, Any] = {}
        
        logging.info("Onboarding variants manager initialized")
    
    def _initialize_variants(self) -> Dict[KoshaOfferingType, OfferingVariant]:
        """Initialize the different offering variants"""
        return {
            KoshaOfferingType.FULL_KOSHA_OFFERING: OfferingVariant(
                offering_type=KoshaOfferingType.FULL_KOSHA_OFFERING,
                name="Full Kosha Offering",
                description="Complete implementation with all kosha layers",
                onboarding_steps=[
                    OnboardingStage.WELCOME,
                    OnboardingStage.COMPANY_SIZE,
                    OnboardingStage.COMPANY_TYPE,
                    OnboardingStage.INDUSTRY,
                    OnboardingStage.USER_MODE,
                    OnboardingStage.KOSHA_SELECTION,  # This will be skipped for this offering
                    OnboardingStage.CUSTOMIZATION,   # This will be expanded
                    OnboardingStage.REVIEW,
                    OnboardingStage.COMPLETION
                ],
                required_steps=[
                    OnboardingStage.COMPANY_SIZE,
                    OnboardingStage.COMPANY_TYPE,
                    OnboardingStage.INDUSTRY,
                    OnboardingStage.USER_MODE
                ],
                kosha_selection_options=[],
                default_koshas=["PRIME_STRATEGY", "PRIME_CONSCIOUSNESS", "DOMAIN_TECH", "MICRO_DATA", "MICRO_REPORTING"],
                advanced_options=True,
                customization_level="advanced",
                recommended_bundles=[
                    BundleType.ENTERPRISE_BUNDLE,
                    BundleType.GROWTH_BUNDLE,
                    BundleType.STARTER_BUNDLE
                ]
            ),
            KoshaOfferingType.KOSHA_BUNDLE: OfferingVariant(
                offering_type=KoshaOfferingType.KOSHA_BUNDLE,
                name="Kosha Bundle",
                description="Pre-configured bundle of koshas",
                onboarding_steps=[
                    OnboardingStage.WELCOME,
                    OnboardingStage.COMPANY_SIZE,
                    OnboardingStage.COMPANY_TYPE,
                    OnboardingStage.INDUSTRY,
                    OnboardingStage.USER_MODE,
                    OnboardingStage.KOSHA_SELECTION,
                    OnboardingStage.CUSTOMIZATION,  # Bundle-specific customization
                    OnboardingStage.REVIEW,
                    OnboardingStage.COMPLETION
                ],
                required_steps=[
                    OnboardingStage.COMPANY_SIZE,
                    OnboardingStage.COMPANY_TYPE,
                    OnboardingStage.INDUSTRY,
                    OnboardingStage.USER_MODE
                ],
                kosha_selection_options=[
                    {
                        "name": "bundle_selection",
                        "type": "radio",
                        "options": [
                            {"value": "starter_bundle", "label": "Starter Bundle", "description": "Basic automation for small teams"},
                            {"value": "growth_bundle", "label": "Growth Bundle", "description": "Advanced automation for scaling companies"},
                            {"value": "enterprise_bundle", "label": "Enterprise Bundle", "description": "Complete solution for large organizations"},
                            {"value": "industry_specialized_bundle", "label": "Industry Specialized", "description": "Tailored for specific industries"},
                            {"value": "ai_automation_bundle", "label": "AI Automation", "description": "AI-powered automation suite"},
                            {"value": "compliance_bundle", "label": "Compliance", "description": "Regulatory compliance tools"}
                        ]
                    }
                ],
                default_koshas=[],
                advanced_options=False,
                customization_level="basic",
                recommended_bundles=[
                    BundleType.ENTERPRISE_BUNDLE,
                    BundleType.GROWTH_BUNDLE,
                    BundleType.STARTER_BUNDLE
                ]
            ),
            KoshaOfferingType.CUSTOM_KOSHA_SELECTION: OfferingVariant(
                offering_type=KoshaOfferingType.CUSTOM_KOSHA_SELECTION,
                name="Custom Kosha Selection",
                description="Select specific koshas to meet your needs",
                onboarding_steps=[
                    OnboardingStage.WELCOME,
                    OnboardingStage.COMPANY_SIZE,
                    OnboardingStage.COMPANY_TYPE,
                    OnboardingStage.INDUSTRY,
                    OnboardingStage.USER_MODE,
                    OnboardingStage.KOSHA_SELECTION,
                    OnboardingStage.CUSTOMIZATION,  # Extended customization options
                    OnboardingStage.REVIEW,
                    OnboardingStage.COMPLETION
                ],
                required_steps=[
                    OnboardingStage.COMPANY_SIZE,
                    OnboardingStage.COMPANY_TYPE,
                    OnboardingStage.INDUSTRY,
                    OnboardingStage.USER_MODE
                ],
                kosha_selection_options=[
                    {
                        "name": "selection_category",
                        "type": "radio",
                        "options": [
                            {"value": "prime", "label": "Prime Koshas", "description": "Core strategic koshas"},
                            {"value": "domain", "label": "Domain Koshas", "description": "Industry-specific koshas"},
                            {"value": "microagent", "label": "Microagents", "description": "Task-specific agents"},
                            {"value": "all", "label": "All Koshas", "description": "All available koshas"}
                        ]
                    }
                ],
                default_koshas=[],
                advanced_options=True,
                customization_level="advanced",
                recommended_bundles=[]
            ),
            KoshaOfferingType.SINGLE_KOSHA: OfferingVariant(
                offering_type=KoshaOfferingType.SINGLE_KOSHA,
                name="Single Kosha",
                description="Implement a single kosha for specific functionality",
                onboarding_steps=[
                    OnboardingStage.WELCOME,
                    OnboardingStage.COMPANY_SIZE,
                    OnboardingStage.COMPANY_TYPE,
                    OnboardingStage.INDUSTRY,
                    OnboardingStage.USER_MODE,
                    OnboardingStage.KOSHA_SELECTION,
                    OnboardingStage.CUSTOMIZATION,  # Single kosha customization
                    OnboardingStage.REVIEW,
                    OnboardingStage.COMPLETION
                ],
                required_steps=[
                    OnboardingStage.COMPANY_SIZE,
                    OnboardingStage.COMPANY_TYPE,
                    OnboardingStage.INDUSTRY,
                    OnboardingStage.USER_MODE
                ],
                kosha_selection_options=[
                    {
                        "name": "single_kosha_selection",
                        "type": "radio",
                        "options": []  # Filled dynamically based on profile
                    }
                ],
                default_koshas=[],
                advanced_options=False,
                customization_level="basic",
                recommended_bundles=[]
            )
        }
    
    def _initialize_bundles(self) -> Dict[BundleType, KoshaBundle]:
        """Initialize available bundles"""
        return {
            BundleType.STARTER_BUNDLE: KoshaBundle(
                id="starter_bundle",
                name="Starter Bundle",
                description="Essential automation for small teams",
                koshas=["MICRO_DATA", "MICRO_REPORTING"],
                target_audience={
                    "company_sizes": [CompanySize.SOLO_ENTREPRENEUR.value, CompanySize.MICRO_STARTUP.value],
                    "industries": ["ALL"],
                    "company_types": ["ALL"]
                },
                pricing_tier="tier_1",
                recommended_for="Small teams needing basic automation"
            ),
            BundleType.GROWTH_BUNDLE: KoshaBundle(
                id="growth_bundle",
                name="Growth Bundle",
                description="Advanced automation for scaling companies",
                koshas=["DOMAIN_TECH", "MICRO_DATA", "MICRO_REPORTING", "MICRO_SECURITY"],
                target_audience={
                    "company_sizes": [CompanySize.SMALL_STARTUP.value, CompanySize.MEDIUM_ENTERPRISE.value],
                    "industries": ["ALL"],
                    "company_types": ["ALL"]
                },
                pricing_tier="tier_2",
                recommended_for="Companies scaling their operations"
            ),
            BundleType.ENTERPRISE_BUNDLE: KoshaBundle(
                id="enterprise_bundle",
                name="Enterprise Bundle",
                description="Complete solution for large organizations",
                koshas=["PRIME_STRATEGY", "PRIME_CONSCIOUSNESS", "DOMAIN_TECH", "DOMAIN_FINANCE", "MICRO_DATA", "MICRO_REPORTING", "MICRO_SECURITY"],
                target_audience={
                    "company_sizes": [CompanySize.MEDIUM_ENTERPRISE.value, CompanySize.LARGE_ENTERPRISE.value],
                    "industries": ["ALL"],
                    "company_types": ["ALL"]
                },
                pricing_tier="tier_3",
                recommended_for="Enterprise organizations requiring full automation"
            ),
            BundleType.INDUSTRY_SPECIALIZED_BUNDLE: KoshaBundle(
                id="industry_specialized_bundle",
                name="Industry Specialized Bundle",
                description="Tailored for specific industries",
                koshas=["DOMAIN_TECH", "MICRO_DATA", "MICRO_REPORTING"],
                target_audience={
                    "company_sizes": ["ALL"],
                    "industries": ["healthcare", "finance", "gaming"],
                    "company_types": ["ALL"]
                },
                pricing_tier="tier_2",
                recommended_for="Industry-specific requirements"
            ),
            BundleType.AI_AUTOMATION_BUNDLE: KoshaBundle(
                id="ai_automation_bundle",
                name="AI Automation Bundle",
                description="AI-powered automation suite",
                koshas=["PRIME_CONSCIOUSNESS", "DOMAIN_TECH", "MICRO_DATA", "MICRO_REPORTING"],
                target_audience={
                    "company_sizes": ["ALL"],
                    "industries": ["technology", "artificial_intelligence"],
                    "company_types": ["tech_company"]
                },
                pricing_tier="tier_3",
                recommended_for="AI-focused organizations"
            ),
            BundleType.COMPLIANCE_BUNDLE: KoshaBundle(
                id="compliance_bundle",
                name="Compliance Bundle",
                description="Regulatory compliance tools",
                koshas=["DOMAIN_FINANCE", "MICRO_SECURITY", "MICRO_REPORTING"],
                target_audience={
                    "company_sizes": [CompanySize.MEDIUM_ENTERPRISE.value, CompanySize.LARGE_ENTERPRISE.value],
                    "industries": ["finance", "healthcare", "government"],
                    "company_types": ["financial_services", "healthcare", "government"]
                },
                pricing_tier="tier_2",
                recommended_for="Regulated industries requiring compliance"
            )
        }
    
    def get_variant(self, offering_type: KoshaOfferingType) -> Optional[OfferingVariant]:
        """Get the onboarding variant for a specific offering type"""
        return self.variants.get(offering_type)
    
    def create_extended_profile(self, user_id: str, offering_type: KoshaOfferingType) -> Any:
        """Create an extended profile based on the offering type"""
        base_profile = self.base_manager.get_profile(user_id)
        if not base_profile:
            return None
        
        if offering_type == KoshaOfferingType.FULL_KOSHA_OFFERING:
            extended_profile = FullKoshaOfferingProfile(base_profile=base_profile)
        elif offering_type == KoshaOfferingType.KOSHA_BUNDLE:
            extended_profile = BundleSelectionProfile(base_profile=base_profile)
        elif offering_type == KoshaOfferingType.CUSTOM_KOSHA_SELECTION:
            extended_profile = CustomSelectionProfile(base_profile=base_profile)
        elif offering_type == KoshaOfferingType.SINGLE_KOSHA:
            extended_profile = SingleKoshaProfile(base_profile=base_profile)
        else:
            return None
        
        self.extended_profiles[user_id] = extended_profile
        return extended_profile
    
    def get_extended_profile(self, user_id: str) -> Optional[Any]:
        """Get the extended profile for a user"""
        return self.extended_profiles.get(user_id)
    
    def get_bundle_recommendations(self, profile: OnboardingProfile) -> List[BundleType]:
        """Get bundle recommendations based on the user's profile"""
        recommendations = []
        
        for bundle_type, bundle in self.bundles.items():
            # Check if bundle matches user's profile
            matches = True
            
            if profile.company_size and profile.company_size.value not in bundle.target_audience["company_sizes"]:
                if "ALL" not in bundle.target_audience["company_sizes"]:
                    matches = False
            
            if profile.industry and profile.industry.value not in bundle.target_audience["industries"]:
                if "ALL" not in bundle.target_audience["industries"]:
                    matches = False
            
            if profile.company_type and profile.company_type.value not in bundle.target_audience["company_types"]:
                if "ALL" not in bundle.target_audience["company_types"]:
                    matches = False
            
            if matches:
                recommendations.append(bundle_type)
        
        return recommendations
    
    def get_kosha_options_for_offering(self, profile: OnboardingProfile, offering_type: KoshaOfferingType) -> List[Dict[str, Any]]:
        """Get appropriate kosha options based on the offering type and user's profile"""
        base_options = self.base_manager.get_available_koshas(profile)
        
        if offering_type == KoshaOfferingType.SINGLE_KOSHA:
            # Filter options for single kosha selection based on profile
            filtered_options = []
            for opt in base_options:
                # Add additional filtering criteria here if needed
                filtered_options.append({
                    "value": opt["id"],
                    "label": opt["name"],
                    "description": opt["description"]
                })
            return filtered_options
        
        elif offering_type == KoshaOfferingType.CUSTOM_KOSHA_SELECTION:
            # Return options based on category selection
            # This would be customized based on the category selected
            category = getattr(self.get_extended_profile(profile.user_id), 'selection_category', 'all')
            
            if category == 'prime':
                return [{"value": opt["id"], "label": opt["name"], "description": opt["description"]} 
                        for opt in base_options if "prime_kosha" in opt.get("categories", [])]
            elif category == 'domain':
                return [{"value": opt["id"], "label": opt["name"], "description": opt["description"]} 
                        for opt in base_options if "domain_kosha" in opt.get("categories", [])]
            elif category == 'microagent':
                return [{"value": opt["id"], "label": opt["name"], "description": opt["description"]} 
                        for opt in base_options if "microagent" in opt.get("categories", [])]
            else:
                # 'all' category
                return [{"value": opt["id"], "label": opt["name"], "description": opt["description"]} 
                        for opt in base_options]
        
        elif offering_type == KoshaOfferingType.FULL_KOSHA_OFFERING:
            # For full offering, return all base options
            return [{"value": opt["id"], "label": opt["name"], "description": opt["description"]} 
                    for opt in base_options]
        
        else:  # Bundle or other offerings
            return [{"value": opt["id"], "label": opt["name"], "description": opt["description"]} 
                    for opt in base_options]
    
    def generate_config_for_offering(self, user_id: str) -> Dict[str, Any]:
        """Generate final configuration based on offering type and selections"""
        profile = self.base_manager.get_profile(user_id)
        if not profile or not profile.kosha_option:
            return {}
        
        try:
            offering_type = KoshaOfferingType(profile.kosha_option)
        except ValueError:
            return {}
        
        extended_profile = self.get_extended_profile(user_id)
        
        if offering_type == KoshaOfferingType.FULL_KOSHA_OFFERING:
            if isinstance(extended_profile, FullKoshaOfferingProfile):
                selected_koshas = (extended_profile.prime_koshas + 
                                 extended_profile.domain_koshas + 
                                 extended_profile.microagents)
            else:
                # Use defaults for full offering if extended profile not set
                selected_koshas = self.variants[offering_type].default_koshas
        
        elif offering_type == KoshaOfferingType.KOSHA_BUNDLE:
            if isinstance(extended_profile, BundleSelectionProfile) and extended_profile.selected_bundle:
                bundle = self.bundles[extended_profile.selected_bundle]
                selected_koshas = bundle.koshas + extended_profile.additional_koshas
            else:
                selected_koshas = []
        
        elif offering_type == KoshaOfferingType.CUSTOM_KOSHA_SELECTION:
            if isinstance(extended_profile, CustomSelectionProfile):
                selected_koshas = extended_profile.base_profile.selected_koshas
            else:
                selected_koshas = profile.selected_koshas or []
        
        elif offering_type == KoshaOfferingType.SINGLE_KOSHA:
            if isinstance(extended_profile, SingleKoshaProfile) and extended_profile.selected_kosha:
                selected_koshas = [extended_profile.selected_kosha]
            else:
                selected_koshas = profile.selected_koshas or []
        else:
            selected_koshas = profile.selected_koshas or []
        
        # Generate configuration with additional offering-specific settings
        configuration = self.base_manager.complete_onboarding(user_id)
        configuration["offering_type"] = offering_type.value
        configuration["selected_koshas"] = selected_koshas
        
        # Add offering-specific configurations
        if offering_type == KoshaOfferingType.FULL_KOSHA_OFFERING and isinstance(extended_profile, FullKoshaOfferingProfile):
            configuration["implementation_details"] = {
                "integration_level": extended_profile.integration_level,
                "security_config": extended_profile.security_config,
                "performance_config": extended_profile.performance_config
            }
        
        elif offering_type == KoshaOfferingType.KOSHA_BUNDLE and isinstance(extended_profile, BundleSelectionProfile):
            configuration["bundle_details"] = {
                "bundle_type": extended_profile.selected_bundle.value if extended_profile.selected_bundle else None,
                "customizations": extended_profile.bundle_customizations,
                "additional_koshas": extended_profile.additional_koshas
            }
        
        elif offering_type == KoshaOfferingType.SINGLE_KOSHA and isinstance(extended_profile, SingleKoshaProfile):
            configuration["single_kosha_details"] = {
                "integration_depth": extended_profile.integration_depth,
                "support_level": extended_profile.support_level
            }
        
        elif offering_type == KoshaOfferingType.CUSTOM_KOSHA_SELECTION and isinstance(extended_profile, CustomSelectionProfile):
            configuration["custom_selection_details"] = {
                "category": extended_profile.selection_category,
                "max_selections": extended_profile.max_selections,
                "selection_filter": extended_profile.selection_filter
            }
        
        return configuration


def create_variants_demo():
    """Create a demo of the onboarding variants system"""
    print("=== Augur Omega: Onboarding Variants by Kosha Offering Demo ===\n")
    
    # Initialize the base onboarding manager
    base_manager = OnboardingManager()
    variants_manager = OnboardingVariantsManager(base_manager)
    
    # Create a new user profile
    user_id = "demo_user_002"
    profile = base_manager.start_onboarding(user_id)
    print(f"Started onboarding for user: {user_id}\n")
    
    # Set up user profile
    base_manager.update_profile(user_id, 
                              company_size=CompanySize.MEDIUM_ENTERPRISE,
                              company_type=CompanyType.TECH_COMPANY,
                              industry=Industry.TECHNOLOGY,
                              user_mode=UserMode.TEAM)
    print("Set up user profile (Medium Enterprise, Tech Company, Technology, Team Mode)\n")
    
    # Test different offering types
    offering_types = [
        KoshaOfferingType.FULL_KOSHA_OFFERING,
        KoshaOfferingType.KOSHA_BUNDLE,
        KoshaOfferingType.CUSTOM_KOSHA_SELECTION,
        KoshaOfferingType.SINGLE_KOSHA
    ]
    
    for offering_type in offering_types:
        print(f"--- Testing {offering_type.value} ---")
        
        # Create variant-specific profile
        extended_profile = variants_manager.create_extended_profile(user_id, offering_type)
        print(f"Created extended profile for {offering_type.value}")
        
        # Get bundle recommendations for bundle offering
        if offering_type == KoshaOfferingType.KOSHA_BUNDLE:
            recommendations = variants_manager.get_bundle_recommendations(profile)
            print(f"Bundle recommendations: {[b.value for b in recommendations]}")
        
        # Get kosha options for this offering
        options = variants_manager.get_kosha_options_for_offering(profile, offering_type)
        print(f"Kosha options available: {len(options)}")
        
        # Set the kosha option in the base profile
        base_manager.update_profile(user_id, kosha_option=offering_type.value)
        
        # For bundle offering, simulate bundle selection
        if offering_type == KoshaOfferingType.KOSHA_BUNDLE and isinstance(extended_profile, BundleSelectionProfile):
            extended_profile.selected_bundle = BundleType.GROWTH_BUNDLE
            extended_profile.additional_koshas = ["MICRO_SECURITY"]
        
        # For single kosha offering, simulate kosha selection
        if offering_type == KoshaOfferingType.SINGLE_KOSHA and isinstance(extended_profile, SingleKoshaProfile):
            extended_profile.selected_kosha = "DOMAIN_TECH"
        
        # Generate configuration
        config = variants_manager.generate_config_for_offering(user_id)
        print(f"Generated configuration with {len(config.get('selected_koshas', []))} koshas")
        print(f"Configuration includes: {', '.join(config.keys())}\n")
    
    print("Onboarding variants demo completed!")


if __name__ == "__main__":
    create_variants_demo()