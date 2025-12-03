// Augur Omega RXM UI Controller
// Handles UI interactions, mode switching, and navigation

document.addEventListener('DOMContentLoaded', function() {
    // Mode management
    const modeButtons = document.querySelectorAll('.mode-btn');
    const essenceView = document.getElementById('essence-view');
    const smartView = document.getElementById('smart-view');
    const expertView = document.getElementById('expert-view');
    
    // Settings modal
    const settingsToggle = document.getElementById('settings-toggle');
    const settingsModal = document.getElementById('settings-modal');
    const modalClose = document.getElementById('modal-close');
    
    // Navigation
    const navItems = document.querySelectorAll('.nav-item');
    
    // Initialize mode
    let currentMode = 'essence';
    
    // Mode switching functionality
    modeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const mode = this.getAttribute('data-mode');
            
            // Update UI
            modeButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Show appropriate view
            switch(mode) {
                case 'essence':
                    essenceView.classList.add('active');
                    smartView.classList.remove('active');
                    expertView.classList.remove('active');
                    break;
                case 'smart':
                    essenceView.classList.remove('active');
                    smartView.classList.add('active');
                    expertView.classList.remove('active');
                    break;
                case 'expert':
                    essenceView.classList.remove('active');
                    smartView.classList.remove('active');
                    expertView.classList.add('active');
                    break;
            }
            
            currentMode = mode;
        });
    });
    
    // Settings modal functionality
    settingsToggle.addEventListener('click', function() {
        settingsModal.style.display = 'flex';
    });
    
    modalClose.addEventListener('click', function() {
        settingsModal.style.display = 'none';
    });
    
    // Close modal when clicking outside
    settingsModal.addEventListener('click', function(e) {
        if (e.target === settingsModal) {
            settingsModal.style.display = 'none';
        }
    });
    
    // Navigation functionality
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all items
            navItems.forEach(navItem => navItem.classList.remove('active'));
            
            // Add active class to clicked item
            this.classList.add('active');
            
            // Get the section this item represents
            const section = this.getAttribute('data-section');
            
            // TODO: Add section-specific logic here
            console.log(`Navigating to section: ${section}`);
        });
    });
    
    // Natural language input functionality
    const naturalInput = document.querySelector('.natural-input');
    const speechBtn = document.querySelector('.speech-btn');
    
    naturalInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            processNaturalInput(this.value);
            this.value = '';
        }
    });
    
    speechBtn.addEventListener('click', function() {
        // TODO: Implement voice recognition
        console.log('Voice input requested');
    });
    
    // Settings save functionality
    const saveSettingsBtn = document.getElementById('save-settings');
    saveSettingsBtn.addEventListener('click', function() {
        saveSettings();
    });
    
    // Settings reset functionality
    const resetSettingsBtn = document.getElementById('reset-settings');
    resetSettingsBtn.addEventListener('click', function() {
        resetSettings();
    });
    
    // Function to process natural language input
    function processNaturalInput(input) {
        // TODO: Implement natural language processing
        console.log(`Processing natural language input: ${input}`);
        
        // For now, just log the input
        // In a real implementation, this would call the NL to JSON converter
        const response = convertNaturalLanguageToAction(input);
        console.log(`Converted to action: ${response}`);
    }
    
    // Function to convert natural language to action
    function convertNaturalLanguageToAction(input) {
        // This would be connected to the NL to JSON converter
        // For now, just return a mock response
        return `Executed action based on input: "${input}"`;
    }
    
    // Function to save settings
    function saveSettings() {
        // Get all settings from the modal
        const theme = document.getElementById('theme-selector').value;
        const autoOptimize = document.getElementById('auto-optimize').checked;
        const autoSync = document.getElementById('auto-sync').checked;
        const apiKey = document.getElementById('api-key').value;
        
        // Save settings to localStorage or send to server
        const settings = {
            theme: theme,
            autoOptimize: autoOptimize,
            autoSync: autoSync,
            apiKey: apiKey ? '***' : '' // Don't store actual API key in plain text
        };
        
        localStorage.setItem('augur-omega-settings', JSON.stringify(settings));
        console.log('Settings saved:', settings);
        
        // Close modal
        settingsModal.style.display = 'none';
        
        // Apply theme change
        applyTheme(theme);
    }
    
    // Function to reset settings to defaults
    function resetSettings() {
        if (confirm('Are you sure you want to reset all settings to defaults?')) {
            document.getElementById('theme-selector').value = 'dark';
            document.getElementById('auto-optimize').checked = true;
            document.getElementById('auto-sync').checked = true;
            document.getElementById('api-key').value = '';
            
            localStorage.removeItem('augur-omega-settings');
            console.log('Settings reset to defaults');
        }
    }
    
    // Function to apply theme
    function applyTheme(theme) {
        document.body.className = theme + '-theme';
        console.log(`Applied theme: ${theme}`);
    }
    
    // Initialize with saved settings if available
    const savedSettings = localStorage.getItem('augur-omega-settings');
    if (savedSettings) {
        const settings = JSON.parse(savedSettings);
        document.getElementById('theme-selector').value = settings.theme || 'dark';
        document.getElementById('auto-optimize').checked = settings.autoOptimize !== undefined ? settings.autoOptimize : true;
        document.getElementById('auto-sync').checked = settings.autoSync !== undefined ? settings.autoSync : true;
        
        // Apply theme
        applyTheme(settings.theme || 'dark');
    }
});

// Component for the JSON editor
class JSONEditor {
    constructor(containerId, jsonData = {}) {
        this.container = document.getElementById(containerId);
        this.jsonData = jsonData;
        this.render();
    }
    
    render() {
        this.container.innerHTML = `
            <div class="json-editor">
                <div class="json-input-section">
                    <h4>Natural Language Input</h4>
                    <textarea class="nl-input" placeholder="Describe your settings changes..."></textarea>
                    <button class="convert-btn">Convert to JSON</button>
                </div>
                <div class="json-output-section">
                    <h4>JSON Output</h4>
                    <pre class="json-output">${JSON.stringify(this.jsonData, null, 2)}</pre>
                    <button class="apply-btn">Apply Changes</button>
                </div>
            </div>
        `;
        
        // Attach event listeners
        this.container.querySelector('.convert-btn').addEventListener('click', () => {
            this.convertNLToJSON();
        });
        
        this.container.querySelector('.apply-btn').addEventListener('click', () => {
            this.applyChanges();
        });
    }
    
    convertNLToJSON() {
        const nlInput = this.container.querySelector('.nl-input').value;
        if (!nlInput.trim()) return;
        
        // This would call the NL to JSON converter service
        // For now, we'll simulate the conversion
        const convertedJSON = this.simulateNLConversion(nlInput);
        this.container.querySelector('.json-output').textContent = JSON.stringify(convertedJSON, null, 2);
    }
    
    simulateNLConversion(input) {
        // Simple simulation - in real implementation this would call an API
        const mockConversion = {
            "description": "Converted from natural language: " + input,
            "timestamp": new Date().toISOString(),
            "changes": {
                "simulation": true,
                "input": input
            }
        };
        
        return mockConversion;
    }
    
    applyChanges() {
        // Apply the JSON changes to the system
        const jsonText = this.container.querySelector('.json-output').textContent;
        let parsedJson;
        
        try {
            parsedJson = JSON.parse(jsonText);
            console.log('Applying changes:', parsedJson);
            // Here would be the actual application logic
        } catch (e) {
            console.error('Invalid JSON:', e);
            alert('Invalid JSON format. Please correct and try again.');
        }
    }
}

// Component for agent formation visualization
class AgentFormationVisualizer {
    constructor(containerId, formationData) {
        this.container = document.getElementById(containerId);
        this.formationData = formationData || {
            "mathematical_efficiency": 0.94,
            "subject_matter_experts": 36,
            "optimal_arrangement": "hierarchical_cluster"
        };
        this.render();
    }
    
    render() {
        const efficiencyPercent = Math.round(this.formationData.mathematical_efficiency * 100);
        
        this.container.innerHTML = `
            <div class="agent-formation-visualizer">
                <h4>Agent Formation Analysis</h4>
                <div class="efficiency-meter">
                    <div class="meter-circle" style="--efficiency: ${efficiencyPercent}%;">
                        <span class="meter-value">${efficiencyPercent}%</span>
                    </div>
                    <p>Mathematical Efficiency</p>
                </div>
                <div class="formation-info">
                    <p><strong>Subject Matter Experts:</strong> ${this.formationData.subject_matter_experts}</p>
                    <p><strong>Optimal Arrangement:</strong> ${this.formationData.optimal_arrangement}</p>
                </div>
            </div>
        `;
    }
}