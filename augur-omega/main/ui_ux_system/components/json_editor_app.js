// Augur Omega JSON Settings Editor
// Provides a split-screen interface for natural language input and JSON editing

document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const naturalInput = document.getElementById('natural-input');
    const jsonEditor = document.getElementById('json-editor');
    const jsonPreview = document.getElementById('json-preview');
    const convertBtn = document.getElementById('convert-btn');
    const applyBtn = document.getElementById('apply-btn');
    const formatBtn = document.getElementById('format-btn');
    const validationIcon = document.getElementById('validation-icon');
    const validationStatus = document.getElementById('validation-status');
    const validationMessage = document.getElementById('validation-message');
    const loadDefaultsBtn = document.getElementById('load-defaults');
    const importJsonBtn = document.getElementById('import-json');
    const exportJsonBtn = document.getElementById('export-json');
    
    // Default settings configuration
    const defaultSettings = {
        "appearance": {
            "theme": "dark",
            "background": "var(--deep-space)",
            "primary_color": "purple",
            "resolution": "1920x1080"
        },
        "agent_formation": {
            "optimization_enabled": true,
            "smart_mode": true,
            "efficiency_target": 0.9,
            "max_agents": 10,
            "formation_algorithm": "mathematical",
            "subject_matter_matching": true
        },
        "performance": {
            "level": "high",
            "boost_enabled": true,
            "concurrency": 10,
            "memory_allocation": 32
        },
        "integration": {
            "sync_enabled": true,
            "api_key": "",
            "endpoint": "https://api.augur-omega.example.com"
        },
        "general": {
            "auto_optimize": true,
            "verbosity": "medium",
            "debug_mode": false
        }
    };
    
    // Initialize the editor with default settings
    let currentSettings = { ...defaultSettings };
    jsonEditor.value = JSON.stringify(currentSettings, null, 2);
    updatePreview();
    validateJson();
    
    // Event listeners
    naturalInput.addEventListener('input', function() {
        // Clear the JSON editor when typing in natural language input
        if (naturalInput.value.trim() !== '') {
            jsonEditor.value = '';
        }
    });
    
    jsonEditor.addEventListener('input', function() {
        validateJson();
        updatePreview();
    });
    
    convertBtn.addEventListener('click', function() {
        convertNaturalLanguageToJSON();
    });
    
    applyBtn.addEventListener('click', function() {
        applyChanges();
    });
    
    formatBtn.addEventListener('click', function() {
        formatJson();
    });
    
    loadDefaultsBtn.addEventListener('click', function() {
        loadDefaultSettings();
    });
    
    importJsonBtn.addEventListener('click', function() {
        importJsonSettings();
    });
    
    exportJsonBtn.addEventListener('click', function() {
        exportJsonSettings();
    });
    
    // Function to convert natural language to JSON
    function convertNaturalLanguageToJSON() {
        const input = naturalInput.value.trim();
        
        if (!input) {
            alert('Please enter a description in the natural language input field.');
            return;
        }
        
        // Show loading state
        convertBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Converting...';
        convertBtn.disabled = true;
        
        // Simulate API call delay for demo
        setTimeout(() => {
            // In a real implementation, this would call an API
            // For demo purposes, we'll simulate a response
            const simulatedResponse = generateJsonFromNaturalLanguage(input);
            
            try {
                // Validate the simulated response
                JSON.parse(simulatedResponse);
                
                // Update the JSON editor
                jsonEditor.value = simulatedResponse;
                validateJson();
                updatePreview();
                
                // Clear natural language input
                naturalInput.value = '';
                
                alert('Conversion successful! Check the JSON Editor and Preview panels.');
            } catch (e) {
                alert('Error in generated JSON: ' + e.message);
            }
            
            // Reset button
            convertBtn.innerHTML = '<i class="fas fa-bolt"></i> Convert to JSON';
            convertBtn.disabled = false;
        }, 1000);
    }
    
    // Function to generate JSON from natural language (simulated)
    function generateJsonFromNaturalLanguage(input) {
        // This is a simplified simulation
        // In a real implementation, this would use NLP/ML to convert natural language to JSON
        
        let newSettings = { ...currentSettings };
        
        // Simple rule-based conversion for demo
        if (input.toLowerCase().includes('theme') && input.toLowerCase().includes('light')) {
            newSettings.appearance.theme = 'light';
        }
        
        if (input.toLowerCase().includes('theme') && input.toLowerCase().includes('dark')) {
            newSettings.appearance.theme = 'dark';
        }
        
        if (input.toLowerCase().includes('performance') && input.toLowerCase().includes('high')) {
            newSettings.performance.level = 'high';
        }
        
        if (input.toLowerCase().includes('performance') && input.toLowerCase().includes('medium')) {
            newSettings.performance.level = 'medium';
        }
        
        if (input.toLowerCase().includes('performance') && input.toLowerCase().includes('low')) {
            newSettings.performance.level = 'low';
        }
        
        if (input.toLowerCase().includes('agent') && input.toLowerCase().includes('optimization')) {
            newSettings.agent_formation.optimization_enabled = true;
        }
        
        if (input.toLowerCase().includes('disable') && input.toLowerCase().includes('optimization')) {
            newSettings.agent_formation.optimization_enabled = false;
        }
        
        if (input.toLowerCase().includes('sync') && input.toLowerCase().includes('enable')) {
            newSettings.integration.sync_enabled = true;
        }
        
        if (input.toLowerCase().includes('sync') && input.toLowerCase().includes('disable')) {
            newSettings.integration.sync_enabled = false;
        }
        
        return JSON.stringify(newSettings, null, 2);
    }
    
    // Function to validate JSON
    function validateJson() {
        try {
            JSON.parse(jsonEditor.value);
            validationIcon.className = 'fas fa-check-circle status-valid';
            validationStatus.textContent = 'Valid JSON';
            validationStatus.className = 'status-valid';
            validationMessage.textContent = '';
            return true;
        } catch (e) {
            validationIcon.className = 'fas fa-times-circle status-invalid';
            validationStatus.textContent = 'Invalid JSON';
            validationStatus.className = 'status-invalid';
            validationMessage.textContent = e.message;
            return false;
        }
    }
    
    // Function to update JSON preview
    function updatePreview() {
        if (jsonEditor.value.trim() === '') {
            jsonPreview.textContent = '// Configuration preview will appear here when JSON is valid';
            return;
        }
        
        try {
            const parsed = JSON.parse(jsonEditor.value);
            jsonPreview.textContent = JSON.stringify(parsed, null, 2);
        } catch (e) {
            jsonPreview.textContent = '// Invalid JSON - preview not available';
        }
    }
    
    // Function to format JSON
    function formatJson() {
        try {
            const parsed = JSON.parse(jsonEditor.value);
            jsonEditor.value = JSON.stringify(parsed, null, 2);
            validateJson();
            updatePreview();
        } catch (e) {
            alert('Cannot format invalid JSON. Please fix errors first.');
        }
    }
    
    // Function to apply changes
    function applyChanges() {
        if (!validateJson()) {
            alert('Please fix JSON errors before applying changes.');
            return;
        }
        
        try {
            currentSettings = JSON.parse(jsonEditor.value);
            alert('Settings applied successfully!');
            
            // In a real implementation, this would call an API to save the settings
            // console.log('Applying settings:', currentSettings);
        } catch (e) {
            alert('Error applying settings: ' + e.message);
        }
    }
    
    // Function to load default settings
    function loadDefaultSettings() {
        if (confirm('Are you sure you want to load default settings? This will replace your current configuration.')) {
            jsonEditor.value = JSON.stringify(defaultSettings, null, 2);
            currentSettings = { ...defaultSettings };
            validateJson();
            updatePreview();
        }
    }
    
    // Function to import JSON settings
    function importJsonSettings() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        
        input.onchange = function(event) {
            const file = event.target.files[0];
            const reader = new FileReader();
            
            reader.onload = function(e) {
                const content = e.target.result;
                
                try {
                    JSON.parse(content);
                    jsonEditor.value = content;
                    validateJson();
                    updatePreview();
                    alert('JSON imported successfully!');
                } catch (error) {
                    alert('Invalid JSON file: ' + error.message);
                }
            };
            
            reader.readAsText(file);
        };
        
        input.click();
    }
    
    // Function to export JSON settings
    function exportJsonSettings() {
        const content = jsonEditor.value || JSON.stringify(defaultSettings, null, 2);
        const blob = new Blob([content], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = 'augur-omega-settings.json';
        document.body.appendChild(a);
        a.click();
        
        // Clean up
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 100);
    }
    
    // Initialize with default settings
    function initializeEditor() {
        jsonEditor.value = JSON.stringify(defaultSettings, null, 2);
        currentSettings = { ...defaultSettings };
        validateJson();
        updatePreview();
    }
    
    // Initialize the editor
    initializeEditor();
});

// JSON Editor Component Class for Reusability
class JsonSettingsEditor {
    constructor(containerId, settings = null) {
        this.container = document.getElementById(containerId);
        this.settings = settings || {};
        this.element = this.createEditorElement();
        this.container.appendChild(this.element);
        this.bindEvents();
    }
    
    createEditorElement() {
        const editorDiv = document.createElement('div');
        editorDiv.className = 'json-settings-editor';
        editorDiv.innerHTML = `
            <div class="editor-container">
                <div class="editor-header">
                    <h3>JSON Settings Editor</h3>
                    <div class="editor-actions">
                        <button class="btn btn-outline format-btn">Format</button>
                        <button class="btn btn-primary apply-btn">Apply</button>
                    </div>
                </div>
                <div class="editor-content">
                    <textarea class="json-editor" placeholder="Enter JSON configuration here...">${JSON.stringify(this.settings, null, 2)}</textarea>
                </div>
                <div class="editor-footer">
                    <div class="validation-status">Valid JSON</div>
                    <button class="btn btn-outline preview-btn">Preview</button>
                </div>
            </div>
        `;
        return editorDiv;
    }
    
    bindEvents() {
        const jsonEditor = this.element.querySelector('.json-editor');
        const formatBtn = this.element.querySelector('.format-btn');
        const applyBtn = this.element.querySelector('.apply-btn');
        const previewBtn = this.element.querySelector('.preview-btn');
        
        jsonEditor.addEventListener('input', () => {
            this.validateJson(jsonEditor.value);
        });
        
        formatBtn.addEventListener('click', () => {
            this.formatJson(jsonEditor);
        });
        
        applyBtn.addEventListener('click', () => {
            this.applyChanges(jsonEditor.value);
        });
        
        previewBtn.addEventListener('click', () => {
            this.showPreview(jsonEditor.value);
        });
    }
    
    validateJson(jsonString) {
        try {
            JSON.parse(jsonString);
            this.element.querySelector('.validation-status').textContent = 'Valid JSON';
            this.element.querySelector('.validation-status').className = 'validation-status valid';
            return true;
        } catch (e) {
            this.element.querySelector('.validation-status').textContent = `Invalid JSON: ${e.message}`;
            this.element.querySelector('.validation-status').className = 'validation-status invalid';
            return false;
        }
    }
    
    formatJson(editorElement) {
        try {
            const parsed = JSON.parse(editorElement.value);
            editorElement.value = JSON.stringify(parsed, null, 2);
            this.validateJson(editorElement.value);
        } catch (e) {
            alert('Cannot format invalid JSON. Please fix errors first.');
        }
    }
    
    applyChanges(jsonString) {
        if (this.validateJson(jsonString)) {
            try {
                this.settings = JSON.parse(jsonString);
                console.log('Settings applied:', this.settings);
                // In a real implementation, this would save the settings
            } catch (e) {
                console.error('Error applying settings:', e);
            }
        } else {
            alert('Please fix JSON errors before applying changes.');
        }
    }
    
    showPreview(jsonString) {
        try {
            const parsed = JSON.parse(jsonString);
            const preview = JSON.stringify(parsed, null, 2);
            alert(`Configuration Preview:\n\n${preview}`);
        } catch (e) {
            alert('Cannot preview invalid JSON.');
        }
    }
}