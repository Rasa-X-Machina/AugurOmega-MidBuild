"""
Augur Omega: Natural Language to JSON Settings Converter
Converts natural language settings descriptions to JSON configuration
"""
import json
import re
from typing import Dict, Any, Union
from dataclasses import dataclass
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SettingsConversionResult:
    """Result of the natural language to JSON conversion"""
    success: bool
    json_output: Union[Dict[str, Any], str, None]
    error_message: str = ""
    confidence: float = 0.0


class NaturalLanguageToJSONConverter:
    """Converts natural language settings descriptions to JSON configuration"""
    
    def __init__(self):
        # Define common configuration patterns and their JSON mappings
        self.patterns = {
            # Theme and appearance settings
            r'change.*theme.*to\s+(light|dark)': lambda m: {"appearance": {"theme": m.group(1)}},
            r'set.*background.*to\s+(.*)': lambda m: {"appearance": {"background": m.group(1)}},
            r'use.*(blue|green|purple|red|black|white).*color': lambda m: {"appearance": {"primary_color": m.group(1)}},
            
            # Agent/formation settings
            r'optimize.*agent.*formation': lambda m: {"agent_formation": {"optimization_enabled": True}},
            r'set.*agent.*efficiency.*to\s+(\d+)%?': lambda m: {"agent_formation": {"efficiency_target": int(m.group(1))/100}},
            r'use.*(\d+).*agents?': lambda m: {"agent_formation": {"max_agents": int(m.group(1))}},
            r'enable.*smart.*mode': lambda m: {"agent_formation": {"smart_mode": True}},
            r'disable.*smart.*mode': lambda m: {"agent_formation": {"smart_mode": False}},
            
            # Performance settings
            r'set.*performance.*to\s+(high|medium|low)': lambda m: {"performance": {"level": m.group(1)}},
            r'enable.*high.*performance': lambda m: {"performance": {"level": "high", "enabled": True}},
            r'disable.*performance.*boost': lambda m: {"performance": {"boost_enabled": False}},
            
            # API and integration settings
            r'use.*api.*key.*(.+)': lambda m: {"integration": {"api_key": m.group(1)}},
            r'connect.*to.*(.+)': lambda m: {"integration": {"endpoint": m.group(1)}},
            r'enable.*sync.*across.*koshas': lambda m: {"integration": {"sync_enabled": True}},
            r'disable.*sync.*across.*koshas': lambda m: {"integration": {"sync_enabled": False}},
            
            # General settings
            r'enable.*auto.*optimize': lambda m: {"general": {"auto_optimize": True}},
            r'disable.*auto.*optimize': lambda m: {"general": {"auto_optimize": False}},
            r'set.*verbosity.*to\s+(low|medium|high)': lambda m: {"general": {"verbosity": m.group(1)}},
        }
        
        # Define keywords for different configuration sections
        self.config_sections = {
            "appearance", "agent_formation", "performance", "integration", "general"
        }
    
    def convert(self, natural_language: str) -> SettingsConversionResult:
        """
        Convert natural language settings description to JSON
        """
        try:
            # Normalize the input
            normalized_input = self._normalize_input(natural_language)
            
            # Try to match against known patterns
            json_config = self._match_patterns(normalized_input)
            
            if json_config:
                # Merge with any additional config that might have been identified
                final_config = self._merge_configurations(json_config)
                confidence = self._calculate_confidence(normalized_input, final_config)
                
                return SettingsConversionResult(
                    success=True,
                    json_output=final_config,
                    confidence=confidence
                )
            else:
                # If no patterns matched, try to create a basic configuration
                basic_config = self._create_basic_config(normalized_input)
                confidence = self._calculate_confidence(normalized_input, basic_config)
                
                return SettingsConversionResult(
                    success=True,
                    json_output=basic_config,
                    confidence=confidence
                )
        
        except Exception as e:
            logger.error(f"Error converting natural language to JSON: {str(e)}")
            return SettingsConversionResult(
                success=False,
                json_output=None,
                error_message=str(e),
                confidence=0.0
            )
    
    def _normalize_input(self, text: str) -> str:
        """Normalize the input text for pattern matching"""
        # Convert to lowercase and remove extra whitespace
        normalized = re.sub(r'\s+', ' ', text.lower().strip())
        
        # Expand common abbreviations and contractions
        expansions = {
            "don't": "do not",
            "doesn't": "does not",
            "won't": "will not",
            "can't": "cannot",
            "shouldn't": "should not",
            "couldn't": "could not",
            "wouldn't": "would not",
            "haven't": "have not",
            "hasn't": "has not",
            "hadn't": "had not",
            "i'm": "i am",
            "you're": "you are",
            "it's": "it is",
            "we're": "we are",
            "they're": "they are"
        }
        
        for abbrev, expansion in expansions.items():
            normalized = normalized.replace(abbrev, expansion)
        
        return normalized
    
    def _match_patterns(self, text: str) -> Dict[str, Any]:
        """Match the text against known patterns to generate JSON configuration"""
        result_config = {}
        
        for pattern, handler in self.patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    config_part = handler(match)
                    result_config = self._merge_dict(result_config, config_part)
                except Exception as e:
                    logger.warning(f"Error processing pattern '{pattern}' with text '{text}': {str(e)}")
        
        return result_config
    
    def _create_basic_config(self, text: str) -> Dict[str, Any]:
        """Create a basic configuration when no patterns match"""
        # Look for key-value pairs in the text
        basic_config = {}
        
        # Common pattern: setting_name = value or setting_name to value
        key_value_patterns = [
            r'(\w+)\s*(?:=|to)\s*([a-zA-Z0-9_\-]+)',
            r'(\w+)\s+(true|false|yes|no|on|off)',
        ]
        
        for pattern in key_value_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for key, value in matches:
                # Convert values to appropriate types
                if value.lower() in ('true', 'yes', 'on'):
                    processed_value = True
                elif value.lower() in ('false', 'no', 'off'):
                    processed_value = False
                else:
                    # Try to convert to number if possible
                    try:
                        processed_value = int(value)
                    except ValueError:
                        try:
                            processed_value = float(value)
                        except ValueError:
                            processed_value = value
                
                basic_config[key.lower()] = processed_value
        
        # If no matches, create a default config with the original text as a description
        if not basic_config:
            basic_config = {
                "description": text,
                "timestamp": self._get_timestamp()
            }
        
        return basic_config
    
    def _merge_configurations(self, base_config: Dict[str, Any], new_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two configuration dictionaries"""
        merged = base_config.copy()
        
        for key, value in new_config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                merged[key] = self._merge_dict(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def _merge_dict(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge two dictionaries"""
        result = base.copy()
        
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_dict(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _calculate_confidence(self, input_text: str, config: Dict[str, Any]) -> float:
        """Calculate confidence in the conversion result"""
        confidence = 0.0
        
        # Base confidence on number of recognized keywords
        recognized_keywords = 0
        for pattern in self.patterns.keys():
            if re.search(pattern, input_text, re.IGNORECASE):
                recognized_keywords += 1
        
        # Add confidence based on recognized keywords (max 0.7 for keywords)
        confidence += min(0.7, recognized_keywords * 0.15)
        
        # Add confidence based on number of configuration keys created (max 0.2 for config)
        config_complexity = min(0.2, len(config) * 0.05)
        confidence += config_complexity
        
        # Add confidence based on how much of the input was used
        config_str = json.dumps(config)
        if input_text and len(input_text) > 0:
            coverage_ratio = len(config_str) / len(input_text)
            coverage_bonus = min(0.1, coverage_ratio * 0.2)
            confidence += coverage_bonus
        
        return min(1.0, confidence)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for configuration"""
        from datetime import datetime
        return datetime.now().isoformat()


class SettingsManager:
    """Manages settings with NL to JSON conversion capabilities"""
    
    def __init__(self, settings_file: str = "settings.json"):
        self.settings_file = settings_file
        self.converter = NaturalLanguageToJSONConverter()
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file"""
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return default settings if file doesn't exist
            default_settings = {
                "appearance": {
                    "theme": "dark",
                    "background": "var(--deep-space)",
                    "primary_color": "purple"
                },
                "agent_formation": {
                    "optimization_enabled": True,
                    "smart_mode": True,
                    "efficiency_target": 0.9
                },
                "performance": {
                    "level": "high",
                    "boost_enabled": True
                },
                "integration": {
                    "sync_enabled": True
                },
                "general": {
                    "auto_optimize": True,
                    "verbosity": "medium"
                }
            }
            self._save_settings(default_settings)
            return default_settings
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in settings file {self.settings_file}")
            return {}
    
    def _save_settings(self, settings: Dict[str, Any]) -> None:
        """Save settings to file"""
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)
    
    def update_settings_from_natural_language(self, nl_description: str) -> SettingsConversionResult:
        """Update settings based on natural language description"""
        result = self.converter.convert(nl_description)
        
        if result.success and result.json_output:
            # Merge the new configuration with existing settings
            self.settings = self.converter._merge_configurations(self.settings, result.json_output)
            self._save_settings(self.settings)
        
        return result
    
    def get_setting(self, key_path: str, default_value: Any = None) -> Any:
        """Get a setting value using dot notation (e.g., 'appearance.theme')"""
        keys = key_path.split('.')
        value = self.settings
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default_value
        
        return value
    
    def set_setting(self, key_path: str, value: Any) -> None:
        """Set a setting value using dot notation (e.g., 'appearance.theme')"""
        keys = key_path.split('.')
        current = self.settings
        
        for key in keys[:-1]:
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
        self._save_settings(self.settings)
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings as a dictionary"""
        return self.settings.copy()


def demonstrate_converter():
    """Demonstrate the natural language to JSON converter"""
    print("=== Augur Omega: Natural Language to JSON Settings Converter ===\n")
    
    converter = NaturalLanguageToJSONConverter()
    settings_manager = SettingsManager()
    
    # Sample natural language inputs
    sample_inputs = [
        "Change theme to light mode and set background to blue",
        "Optimize agent formation for maximum efficiency",
        "Enable smart mode and disable performance boost",
        "Use API key abc123 and connect to https://api.example.com",
        "Enable auto-optimize and set verbosity to high",
        "Set agent efficiency to 95% and use 10 agents",
        "Set performance to high and enable sync across koshas"
    ]
    
    print("Sample Conversions:")
    for i, input_text in enumerate(sample_inputs, 1):
        result = converter.convert(input_text)
        print(f"\n{i}. Input: '{input_text}'")
        print(f"   Success: {result.success}")
        print(f"   Confidence: {result.confidence:.2f}")
        if result.success and result.json_output:
            print(f"   Output: {json.dumps(result.json_output, indent=2)}")
        if result.error_message:
            print(f"   Error: {result.error_message}")
    
    print(f"\nCurrent Settings: {json.dumps(settings_manager.get_all_settings(), indent=2)}")
    
    # Test updating settings from natural language
    print(f"\nUpdating settings with: 'Change theme to dark and enable auto-optimize'")
    result = settings_manager.update_settings_from_natural_language("Change theme to dark and enable auto-optimize")
    print(f"Update result: {result.success}, Confidence: {result.confidence:.2f}")
    print(f"Updated settings: {json.dumps(settings_manager.get_all_settings(), indent=2)}")


if __name__ == "__main__":
    demonstrate_converter()