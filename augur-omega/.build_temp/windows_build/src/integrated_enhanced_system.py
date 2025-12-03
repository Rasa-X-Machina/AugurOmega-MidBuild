"""
Augur Omega: Main Integration Module
Integrates all enhanced UI/UX components: accessibility, localization, inter-kosha communication, and onboarding
"""
import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime
import logging

# Import all the components we've created
from .localization.localization_manager import LocalizationManager
from .communication.inter_kosha_communicator import InterKoshaCommunicator
from .onboarding.onboarding_manager import OnboardingManager
from .onboarding.onboarding_variants_manager import OnboardingVariantsManager
from .integrated_ui_ux_system import AugurOmegaUIUXSystem


class AugurOmegaEnhancedSystem:
    """Main system integrating all enhanced UI/UX components"""
    
    def __init__(self):
        # Initialize all components
        self.localization_manager = LocalizationManager()
        self.communicator = InterKoshaCommunicator()
        self.onboarding_manager = OnboardingManager()
        self.onboarding_variants_manager = OnboardingVariantsManager(self.onboarding_manager)
        self.ui_ux_system = AugurOmegaUIUXSystem()
        
        # Track system state
        self.initialized = False
        self.users: Dict[str, Dict[str, Any]] = {}
        
        logging.info("Augur Omega Enhanced System initialized")
    
    async def initialize_system(self):
        """Initialize all components"""
        # Start the communicator
        await self.communicator.start()
        
        # Register system koshas with the communicator
        await self._register_system_koshas()
        
        # Set initialization flag
        self.initialized = True
        
        logging.info("Augur Omega Enhanced System fully initialized")
    
    async def _register_system_koshas(self):
        """Register all system koshas with the communicator"""
        # Register some example koshas - in a real system, this would come from the kosha registry
        kosha_types = [
            ("PRIME_STRATEGY", "prime_kosha", ["strategic_planning", "system_coordination"]),
            ("PRIME_CONSCIOUSNESS", "prime_kosha", ["consciousness", "awareness"]),
            ("DOMAIN_TECH", "domain_kosha", ["technical_implementation", "architecture"]),
            ("DOMAIN_FINANCE", "domain_kosha", ["financial_management", "planning"]),
            ("MICRO_DATA", "microagent", ["data_processing", "analysis"]),
            ("MICRO_REPORTING", "microagent", ["reporting", "analytics"]),
            ("MICRO_SECURITY", "microagent", ["security", "monitoring"])
        ]
        
        for kosha_id, kosha_type, capabilities in kosha_types:
            await self.communicator.register_kosha(kosha_id, kosha_type, capabilities)
    
    async def register_user(self, user_id: str, locale: str = "en-US") -> bool:
        """Register a new user in the system"""
        if user_id in self.users:
            return False
        
        # Initialize user with their locale
        self.users[user_id] = {
            "locale": locale,
            "registered_at": datetime.now().isoformat(),
            "onboarding_started": False,
            "onboarding_completed": False,
            "selected_koshas": [],
            "preferences": {}
        }
        
        # Set locale in localization manager
        self.localization_manager.set_locale(locale)
        
        # Start onboarding for the user
        self.onboarding_manager.start_onboarding(user_id, locale)
        
        logging.info(f"User {user_id} registered with locale {locale}")
        return True
    
    def get_localized_text(self, user_id: str, key: str) -> str:
        """Get localized text for a user"""
        user_data = self.users.get(user_id)
        locale = user_data["locale"] if user_data else "en-US"
        return self.localization_manager.get_translation(key, locale)
    
    async def start_onboarding(self, user_id: str, offering_type: str = None) -> bool:
        """Start onboarding for a user with an optional offering type"""
        if user_id not in self.users:
            return False
        
        # Update user's onboarding status
        self.users[user_id]["onboarding_started"] = True
        
        # If an offering type is specified, create the variant profile
        if offering_type:
            try:
                from .onboarding.onboarding_variants_manager import KoshaOfferingType
                offering_enum = KoshaOfferingType(offering_type)
                self.onboarding_variants_manager.create_extended_profile(user_id, offering_enum)
                # Update the base profile to reflect the selected offering
                self.onboarding_manager.update_profile(user_id, kosha_option=offering_type)
            except ValueError:
                logging.warning(f"Invalid offering type: {offering_type}")
        
        logging.info(f"Onboarding started for user {user_id} with offering type {offering_type}")
        return True
    
    async def complete_onboarding(self, user_id: str) -> Dict[str, Any]:
        """Complete onboarding for a user and return configuration"""
        if user_id not in self.users:
            return {}
        
        # Advance to completion stage
        while True:
            current_stage = self.onboarding_manager.get_profile(user_id).stage
            if current_stage.value == "completion":
                break
            if not self.onboarding_manager.advance_stage(user_id):
                break
        
        # Generate configuration through the variants manager
        config = self.onboarding_variants_manager.generate_config_for_offering(user_id)
        
        if config:
            self.users[user_id]["onboarding_completed"] = True
            self.users[user_id]["selected_koshas"] = config.get("selected_koshas", [])
            self.users[user_id]["configuration"] = config
            
            logging.info(f"Onboarding completed for user {user_id}")
            return config
        
        return {}
    
    async def send_system_notification(self, user_id: str, message: str, message_type: str = "info") -> bool:
        """Send a system notification to a user's koshas"""
        user_config = self.users.get(user_id, {}).get("configuration", {})
        selected_koshas = user_config.get("selected_koshas", [])
        
        if not selected_koshas:
            logging.warning(f"No koshas configured for user {user_id}")
            return False
        
        # Send notification to all user's koshas
        notifications_sent = 0
        for kosha_id in selected_koshas:
            notification_msg = {
                "type": message_type,
                "source": "system",
                "target": kosha_id,
                "content": {
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                    "user_id": user_id
                }
            }
            
            # Add the notification to the communicator's queue
            from .communication.inter_kosha_communicator import Message, MessageType
            msg_obj = Message(
                source_id="system",
                target_id=kosha_id,
                type=MessageType.NOTIFICATION,
                content=notification_msg
            )
            
            if self.communicator.message_queue.put(msg_obj):
                notifications_sent += 1
        
        logging.info(f"Sent {notifications_sent} notifications to user {user_id}'s koshas")
        return notifications_sent > 0
    
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences"""
        if user_id not in self.users:
            return False
        
        self.users[user_id]["preferences"].update(preferences)
        
        # Update locale if changed
        if "locale" in preferences:
            await self.set_user_locale(user_id, preferences["locale"])
        
        logging.info(f"Updated preferences for user {user_id}")
        return True
    
    async def set_user_locale(self, user_id: str, locale: str) -> bool:
        """Set user locale for localization"""
        if user_id not in self.users:
            return False
        
        # Check if locale is supported
        supported_locales = self.localization_manager.get_supported_locales()
        if locale not in supported_locales:
            # Try to get base language if exact locale not found
            lang = locale.split('-')[0] if '-' in locale else locale
            available_locales = [loc for loc in supported_locales if loc.startswith(f"{lang}-")]
            if available_locales:
                locale = available_locales[0]
            else:
                locale = "en-US"  # Fallback to English
        
        self.users[user_id]["locale"] = locale
        self.localization_manager.set_locale(locale)
        
        logging.info(f"Set locale {locale} for user {user_id}")
        return True
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        communicator_status = await self.communicator.get_system_status()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "initialized": self.initialized,
            "registered_users": len(self.users),
            "active_onboardings": len([u for u in self.users.values() if u.get("onboarding_started") and not u.get("onboarding_completed")]),
            "completed_onboardings": len([u for u in self.users.values() if u.get("onboarding_completed")]),
            "supported_locales": len(self.localization_manager.get_supported_locales()),
            "communicator_status": communicator_status,
            "kosha_types": ["prime_kosha", "domain_kosha", "microagent"]
        }
    
    async def shutdown_system(self):
        """Shut down all system components"""
        await self.communicator.stop()
        logging.info("Augur Omega Enhanced System shut down")


def create_main_integration_demo():
    """Create a demo of the integrated system"""
    import asyncio
    
    async def demo():
        print("=== Augur Omega: Enhanced System Integration Demo ===\n")
        
        # Initialize the enhanced system
        system = AugurOmegaEnhancedSystem()
        await system.initialize_system()
        print("Enhanced system initialized\n")
        
        # Register a user
        user_id = "enhanced_user_001"
        await system.register_user(user_id, "en-US")
        print(f"Registered user: {user_id} with locale en-US\n")
        
        # Start onboarding with a specific offering
        await system.start_onboarding(user_id, "custom_kosha_selection")
        print(f"Started onboarding for {user_id} with custom selection offering\n")
        
        # Simulate updating user profile through onboarding
        onb_manager = system.onboarding_manager
        onb_manager.update_profile(user_id, 
                                  company_size="medium_enterprise",
                                  company_type="tech_company", 
                                  industry="technology",
                                  user_mode="team")
        print("Updated user profile through onboarding\n")
        
        # Get available koshas for this user's profile
        profile = onb_manager.get_profile(user_id)
        available_koshas = system.onboarding_variants_manager.get_kosha_options_for_offering(
            profile, 
            "custom_kosha_selection"
        )
        print(f"Available koshas for user: {len(available_koshas)}\n")
        
        # Select some koshas
        selected_koshas = [k["value"] for k in available_koshas[:3]]  # Select first 3
        onb_manager.update_profile(user_id, selected_koshas=selected_koshas)
        print(f"Selected koshas: {selected_koshas}\n")
        
        # Complete onboarding
        config = await system.complete_onboarding(user_id)
        print(f"Completed onboarding with configuration: {json.dumps(config, indent=2)}\n")
        
        # Send a system notification
        success = await system.send_system_notification(
            user_id, 
            "Welcome to Augur Omega! Your configuration is now active.", 
            "info"
        )
        print(f"System notification sent: {success}\n")
        
        # Update user preferences
        await system.update_user_preferences(user_id, {
            "theme": "dark",
            "notifications": True,
            "auto_backup": True
        })
        print("Updated user preferences\n")
        
        # Get system status
        status = await system.get_system_status()
        print(f"System status: {json.dumps(status, indent=2)}\n")
        
        # Test localization
        localized_text = system.get_localized_text(user_id, "welcome_message")
        print(f"Localized welcome message: {localized_text}\n")
        
        # Test with a different locale
        await system.set_user_locale(user_id, "zh-CN")
        localized_text_chinese = system.get_localized_text(user_id, "welcome_message")
        print(f"Localized welcome message in Chinese: {localized_text_chinese}\n")
        
        # Register another user with different locale
        user2_id = "enhanced_user_002"
        await system.register_user(user2_id, "es-ES")
        localized_text_spanish = system.get_localized_text(user2_id, "welcome_message")
        print(f"Localized welcome message in Spanish: {localized_text_spanish}\n")
        
        # Get updated system status
        status = await system.get_system_status()
        print(f"Updated system status: {json.dumps(status, indent=2)}\n")
        
        # Shut down the system
        await system.shutdown_system()
        print("Enhanced system demo completed!")
    
    # Run the demo
    asyncio.run(demo())


if __name__ == "__main__":
    create_main_integration_demo()