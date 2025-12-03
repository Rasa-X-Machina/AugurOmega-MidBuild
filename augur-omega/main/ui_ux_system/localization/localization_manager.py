"""
Augur Omega: Localization System
Supports top 30 economies, 30 languages, and 30 countries relevant for ROI maximization
"""
import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import logging

# Define top 30 economies by GDP (nominal, 2023)
TOP_30_ECONOMIES = [
    "United States", "China", "Japan", "Germany", "India", "United Kingdom", 
    "France", "Italy", "Brazil", "Canada", "South Korea", "Russia", 
    "Australia", "Spain", "Mexico", "Indonesia", "Netherlands", "Saudi Arabia", 
    "Turkey", "Switzerland", "Poland", "Argentina", "Sweden", "Belgium", 
    "Thailand", "South Africa", "Austria", "Norway", "Israel", "Ireland"
]

# Define top 30 languages from entrepreneurship, tech, and gaming forums
TOP_30_LANGUAGES = [
    "en", "zh", "es", "ja", "ko", "pt", "de", "fr", "ru", "ar", 
    "hi", "it", "pl", "tr", "nl", "cs", "sv", "da", "fi", "no", 
    "th", "id", "vi", "he", "el", "ro", "hu", "uk", "ms", "ta"
]

# Define the most relevant countries for ROI maximization
ROI_RELEVANT_COUNTRIES = [
    "United States", "China", "United Kingdom", "Germany", "Japan", 
    "Canada", "Australia", "Singapore", "Switzerland", "Netherlands", 
    "France", "Hong Kong", "Sweden", "Ireland", "Israel", "South Korea", 
    "Norway", "Denmark", "Finland", "Belgium", "Luxembourg", "Qatar", 
    "United Arab Emirates", "New Zealand", "Austria", "Netherlands", 
    "Italy", "Spain", "Monaco", "Cayman Islands"
]

# Language to country mappings
LANGUAGE_COUNTRY_MAP = {
    "en": ["United States", "United Kingdom", "Canada", "Australia", "Ireland", "New Zealand", "Singapore"],
    "zh": ["China", "Taiwan", "Hong Kong", "Singapore"],
    "es": ["Spain", "Mexico", "Argentina", "Colombia", "Peru", "Venezuela"],
    "ja": ["Japan"],
    "ko": ["South Korea", "North Korea"],
    "pt": ["Brazil", "Portugal", "Angola", "Mozambique"],
    "de": ["Germany", "Austria", "Switzerland", "Luxembourg"],
    "fr": ["France", "Canada", "Belgium", "Switzerland", "Monaco"],
    "ru": ["Russia", "Kazakhstan", "Belarus", "Ukraine"],
    "ar": ["Saudi Arabia", "Egypt", "UAE", "Qatar", "Jordan", "Lebanon"],
    "hi": ["India"],
    "it": ["Italy", "Switzerland"],
    "pl": ["Poland"],
    "tr": ["Turkey"],
    "nl": ["Netherlands", "Belgium"],
    "cs": ["Czech Republic"],
    "sv": ["Sweden"],
    "da": ["Denmark"],
    "fi": ["Finland"],
    "no": ["Norway"],
    "th": ["Thailand"],
    "id": ["Indonesia"],
    "vi": ["Vietnam"],
    "he": ["Israel"],
    "el": ["Greece", "Cyprus"],
    "ro": ["Romania", "Moldova"],
    "hu": ["Hungary"],
    "uk": ["Ukraine"],
    "ms": ["Malaysia", "Brunei"],
    "ta": ["India", "Sri Lanka", "Singapore"]
}


class LocalizationManager:
    """Manages localization for top 30 economies, languages, and countries"""
    
    def __init__(self, locales_dir: str = "locales"):
        self.locales_dir = Path(locales_dir)
        self.locales_dir.mkdir(exist_ok=True)
        
        # Initialize localization data
        self.supported_locales = {}
        self.current_locale = "en-US"
        
        # Create locale directories and files
        self._initialize_locales()
        
        # Load translation files
        self.translations = self._load_all_translations()
        
        logging.info(f"Localization system initialized with {len(self.translations)} locales")
    
    def _initialize_locales(self):
        """Initialize locale directories and create basic structure"""
        for lang in TOP_30_LANGUAGES:
            lang_dir = self.locales_dir / lang
            lang_dir.mkdir(exist_ok=True)
            
            # Create common translation files for each language
            self._create_default_translations(lang, lang_dir)
            
            # Get countries for this language
            countries_for_lang = LANGUAGE_COUNTRY_MAP.get(lang, [])
            
            # Create locale-specific files for each country
            for country in countries_for_lang:
                if country in ROI_RELEVANT_COUNTRIES:
                    locale_code = f"{lang}-{country.replace(' ', '')}"
                    locale_file = lang_dir / f"{locale_code.split('-')[1]}.json"
                    
                    # Create locale-specific content
                    if not locale_file.exists():
                        locale_content = {
                            "locale": locale_code,
                            "language": lang,
                            "country": country,
                            "economy_ranking": self._get_economy_ranking(country),
                            "translation": self._get_default_translations(lang)
                        }
                        
                        with open(locale_file, 'w', encoding='utf-8') as f:
                            json.dump(locale_content, f, indent=2, ensure_ascii=False)
    
    def _create_default_translations(self, lang: str, lang_dir: Path):
        """Create default translation files for a language"""
        # Create base translation file
        base_file = lang_dir / "base.json"
        if not base_file.exists():
            base_translations = self._get_default_translations(lang)
            
            with open(base_file, 'w', encoding='utf-8') as f:
                json.dump(base_translations, f, indent=2, ensure_ascii=False)
    
    def _get_default_translations(self, lang: str) -> Dict[str, str]:
        """Get default translations for a language"""
        # Default (English) translations
        default_translations = {
            "app_title": "Augur Omega RXM Platform",
            "dashboard": "Dashboard",
            "agents": "Agent Teams",
            "koshas": "Koshas",
            "settings": "Settings",
            "mode_switch": "Mode Switch",
            "orchestration": "Orchestration",
            "integration": "Integration",
            "essence_mode": "Essence Mode",
            "smart_mode": "Smart Mode",
            "expert_mode": "Expert Mode",
            "appearance": "Appearance",
            "behavior": "Behavior",
            "integration": "Integration",
            "api_key": "API Key",
            "auto_optimize": "Auto-optimize agent formation",
            "auto_sync": "Auto-sync settings across koshas",
            "theme": "Theme",
            "dark": "Dark",
            "light": "Light",
            "performance": "Performance",
            "high": "High",
            "medium": "Medium",
            "low": "Low",
            "efficiency": "Efficiency",
            "agent_efficiency": "Agent Efficiency",
            "processing_speed": "Processing Speed",
            "system_security": "System Security",
            "needs_attention": "Needs Attention",
            "focus_task": "Focus Task",
            "continue": "Continue",
            "pause": "Pause",
            "configure": "Configure",
            "optimization_level": "Optimization Level",
            "subject_matter_expertise": "Subject Matter Expertise",
            "processing_priority": "Processing Priority",
            "prime_koshas": "Prime Koshas",
            "domain_koshas": "Domain Koshas",
            "microagents": "Microagents",
            "concurrency_level": "Concurrency Level",
            "memory_allocation": "Memory Allocation (GB)",
            "processing_threads": "Processing Threads",
            "mathematical_optimization": "Mathematical Optimization Algorithm",
            "subject_expertise_matching": "Subject Matter Expertise Matching",
            "advanced_load_balancing": "Advanced Load Balancing",
            "save": "Save",
            "reset_to_defaults": "Reset to Defaults",
            "apply_changes": "Apply Changes",
            "convert_to_json": "Convert to JSON",
            "natural_language_input": "Natural Language Input",
            "json_output": "JSON Output",
            "json_editor": "JSON Editor",
            "configuration_preview": "Configuration Preview",
            "load_defaults": "Load Defaults",
            "import": "Import",
            "export": "Export",
            "format": "Format",
            "valid_json": "Valid JSON",
            "invalid_json": "Invalid JSON",
            "backups": "Backups",
            "system_state": "System State",
            "optimization_cycle": "Optimization Cycle",
            "run_optimization": "Run Optimization",
            "sync_status": "Sync Status",
            "company_size": "Company Size",
            "company_type": "Company Type",
            "industry": "Industry",
            "team_mode": "Team Mode",
            "individual_mode": "Individual Mode",
            "onboarding": "Onboarding",
            "welcome_message": "Welcome to Augur Omega",
            "getting_started": "Getting Started",
            "full_kosha_offering": "Full Kosha Offering",
            "kosha_bundle": "Kosha Bundle",
            "custom_kosha_selection": "Custom Kosha Selection",
            "single_kosha": "Single Kosha",
            "select_company_size": "Select your company size",
            "select_company_type": "Select your company type",
            "select_industry": "Select your industry",
            "select_mode": "Select your usage mode",
            "select_kosha_option": "Select your kosha option",
            "micro_startup": "Micro Startup (<10 people)",
            "small_startup": "Small Startup (10-50 people)",
            "medium_enterprise": "Medium Enterprise (50-250 people)",
            "large_enterprise": "Large Enterprise (250+ people)",
            "solo_entrepreneur": "Solo Entrepreneur",
            "agency": "Agency",
            "consulting_firm": "Consulting Firm",
            "tech_company": "Technology Company",
            "financial_services": "Financial Services",
            "healthcare": "Healthcare",
            "retail": "Retail",
            "manufacturing": "Manufacturing",
            "education": "Education",
            "non_profit": "Non-Profit",
            "government": "Government",
            "other": "Other",
            "next": "Next",
            "previous": "Previous",
            "finish": "Finish",
            "skip": "Skip",
            "progress": "Progress",
            "step": "Step",
            "complete": "Complete",
            "in_progress": "In Progress",
            "not_started": "Not Started",
            "success": "Success",
            "error": "Error",
            "warning": "Warning",
            "info": "Information",
            "loading": "Loading",
            "search": "Search",
            "filter": "Filter",
            "sort": "Sort",
            "view": "View",
            "edit": "Edit",
            "delete": "Delete",
            "add": "Add",
            "remove": "Remove",
            "yes": "Yes",
            "no": "No",
            "ok": "OK",
            "cancel": "Cancel",
            "close": "Close",
            "help": "Help",
            "about": "About",
            "contact": "Contact",
            "support": "Support",
            "documentation": "Documentation",
            "tutorials": "Tutorials",
            "community": "Community",
            "forum": "Forum",
            "chat": "Chat",
            "feedback": "Feedback",
            "report_issue": "Report Issue",
            "privacy_policy": "Privacy Policy",
            "terms_of_service": "Terms of Service",
            "cookie_policy": "Cookie Policy"
        }
        
        # Return appropriate translations based on language
        if lang == "en":
            return default_translations
        elif lang == "zh":
            # Chinese translations
            return {
                "app_title": "奥古欧米茄 RXM 平台",
                "dashboard": "仪表板",
                "agents": "代理团队",
                "koshas": "层次",
                "settings": "设置",
                "mode_switch": "模式切换",
                "orchestration": "编排",
                "integration": "集成",
                "essence_mode": "本质模式",
                "smart_mode": "智能模式",
                "expert_mode": "专家模式",
                "appearance": "外观",
                "behavior": "行为",
                "api_key": "API 密钥",
                "auto_optimize": "自动优化代理形成",
                "auto_sync": "跨层次自动同步设置",
                "theme": "主题",
                "dark": "暗色",
                "light": "亮色",
                "performance": "性能",
                "high": "高",
                "medium": "中",
                "low": "低",
                "efficiency": "效率",
                "agent_efficiency": "代理效率",
                "processing_speed": "处理速度",
                "system_security": "系统安全",
                "needs_attention": "需要注意",
                "focus_task": "专注任务",
                "continue": "继续",
                "pause": "暂停",
                "configure": "配置",
                "optimization_level": "优化级别",
                "subject_matter_expertise": "主题专业知识",
                "processing_priority": "处理优先级",
                "prime_koshas": "主要层次",
                "domain_koshas": "领域层次",
                "microagents": "微代理",
                "concurrency_level": "并发级别",
                "memory_allocation": "内存分配 (GB)",
                "processing_threads": "处理线程",
                "mathematical_optimization": "数学优化算法",
                "subject_expertise_matching": "主题专业知识匹配",
                "advanced_load_balancing": "高级负载均衡",
                "save": "保存",
                "reset_to_defaults": "重置为默认值",
                "apply_changes": "应用更改",
                "convert_to_json": "转换为JSON",
                "natural_language_input": "自然语言输入",
                "json_output": "JSON输出",
                "json_editor": "JSON编辑器",
                "configuration_preview": "配置预览",
                "load_defaults": "加载默认值",
                "import": "导入",
                "export": "导出",
                "format": "格式化",
                "valid_json": "有效JSON",
                "invalid_json": "无效JSON",
                "backups": "备份",
                "system_state": "系统状态",
                "optimization_cycle": "优化周期",
                "run_optimization": "运行优化",
                "sync_status": "同步状态",
                "company_size": "公司规模",
                "company_type": "公司类型",
                "industry": "行业",
                "team_mode": "团队模式",
                "individual_mode": "个人模式",
                "onboarding": "新用户引导",
                "welcome_message": "欢迎使用奥古欧米茄",
                "getting_started": "开始使用",
                "full_kosha_offering": "完整层次服务",
                "kosha_bundle": "层次包",
                "custom_kosha_selection": "自定义层次选择",
                "single_kosha": "单个层次",
                "select_company_size": "选择公司规模",
                "select_company_type": "选择公司类型",
                "select_industry": "选择行业",
                "select_mode": "选择使用模式",
                "select_kosha_option": "选择层次选项",
                "micro_startup": "微型创业公司 (<10人)",
                "small_startup": "小型创业公司 (10-50人)",
                "medium_enterprise": "中型企业 (50-250人)",
                "large_enterprise": "大型企业 (250+人)",
                "solo_entrepreneur": "独立创业者",
                "agency": "代理机构",
                "consulting_firm": "咨询公司",
                "tech_company": "科技公司",
                "financial_services": "金融服务",
                "healthcare": "医疗保健",
                "retail": "零售",
                "manufacturing": "制造业",
                "education": "教育",
                "non_profit": "非营利组织",
                "government": "政府",
                "other": "其他",
                "next": "下一步",
                "previous": "上一步",
                "finish": "完成",
                "skip": "跳过",
                "progress": "进度",
                "step": "步骤",
                "complete": "完成",
                "in_progress": "进行中",
                "not_started": "未开始",
                "success": "成功",
                "error": "错误",
                "warning": "警告",
                "info": "信息",
                "loading": "加载中",
                "search": "搜索",
                "filter": "筛选",
                "sort": "排序",
                "view": "查看",
                "edit": "编辑",
                "delete": "删除",
                "add": "添加",
                "remove": "移除",
                "yes": "是",
                "no": "否",
                "ok": "确定",
                "cancel": "取消",
                "close": "关闭",
                "help": "帮助",
                "about": "关于",
                "contact": "联系",
                "support": "支持",
                "documentation": "文档",
                "tutorials": "教程",
                "community": "社区",
                "forum": "论坛",
                "chat": "聊天",
                "feedback": "反馈",
                "report_issue": "报告问题",
                "privacy_policy": "隐私政策",
                "terms_of_service": "服务条款",
                "cookie_policy": "Cookie政策"
            }
        elif lang == "es":
            # Spanish translations
            return {
                "app_title": "Plataforma Augur Omega RXM",
                "dashboard": "Panel de control",
                "agents": "Equipos de agentes",
                "koshas": "Koshas",
                "settings": "Configuración",
                "mode_switch": "Cambio de modo",
                "orchestration": "Orquestación",
                "integration": "Integración",
                "essence_mode": "Modo Esencia",
                "smart_mode": "Modo Inteligente",
                "expert_mode": "Modo Experto",
                "appearance": "Apariencia",
                "behavior": "Comportamiento",
                "api_key": "Clave API",
                "auto_optimize": "Auto-optimizar formación de agentes",
                "auto_sync": "Auto-sincronizar configuraciones entre koshas",
                "theme": "Tema",
                "dark": "Oscuro",
                "light": "Claro",
                "performance": "Rendimiento",
                "high": "Alto",
                "medium": "Medio",
                "low": "Bajo",
                "efficiency": "Eficiencia",
                "agent_efficiency": "Eficiencia del Agente",
                "processing_speed": "Velocidad de Procesamiento",
                "system_security": "Seguridad del Sistema",
                "needs_attention": "Requiere Atención",
                "focus_task": "Tarea Principal",
                "continue": "Continuar",
                "pause": "Pausar",
                "configure": "Configurar",
                "optimization_level": "Nivel de Optimización",
                "subject_matter_expertise": "Conocimiento del Tema",
                "processing_priority": "Prioridad de Procesamiento",
                "prime_koshas": "Koshas Primarias",
                "domain_koshas": "Koshas de Dominio",
                "microagents": "Microagentes",
                "concurrency_level": "Nivel de Concurrencia",
                "memory_allocation": "Asignación de Memoria (GB)",
                "processing_threads": "Hilos de Procesamiento",
                "mathematical_optimization": "Algoritmo de Optimización Matemática",
                "subject_expertise_matching": "Coincidencia de Conocimiento del Tema",
                "advanced_load_balancing": "Equilibrio de Carga Avanzado",
                "save": "Guardar",
                "reset_to_defaults": "Restablecer valores predeterminados",
                "apply_changes": "Aplicar cambios",
                "convert_to_json": "Convertir a JSON",
                "natural_language_input": "Entrada de Lenguaje Natural",
                "json_output": "Salida JSON",
                "json_editor": "Editor JSON",
                "configuration_preview": "Vista Previa de Configuración",
                "load_defaults": "Cargar valores predeterminados",
                "import": "Importar",
                "export": "Exportar",
                "format": "Formato",
                "valid_json": "JSON Válido",
                "invalid_json": "JSON Inválido",
                "backups": "Copias de Seguridad",
                "system_state": "Estado del Sistema",
                "optimization_cycle": "Ciclo de Optimización",
                "run_optimization": "Ejecutar Optimización",
                "sync_status": "Estado de Sincronización",
                "company_size": "Tamaño de la Empresa",
                "company_type": "Tipo de Empresa",
                "industry": "Industria",
                "team_mode": "Modo Equipo",
                "individual_mode": "Modo Individual",
                "onboarding": "Integración",
                "welcome_message": "Bienvenido a Augur Omega",
                "getting_started": "Empezando",
                "full_kosha_offering": "Oferta Completa de Kosha",
                "kosha_bundle": "Paquete de Kosha",
                "custom_kosha_selection": "Selección Personalizada de Kosha",
                "single_kosha": "Kosha Individual",
                "select_company_size": "Seleccione el tamaño de su empresa",
                "select_company_type": "Seleccione el tipo de su empresa",
                "select_industry": "Seleccione su industria",
                "select_mode": "Seleccione su modo de uso",
                "select_kosha_option": "Seleccione su opción de kosha",
                "micro_startup": "Micro Startup (<10 personas)",
                "small_startup": "Pequeña Startup (10-50 personas)",
                "medium_enterprise": "Empresa Mediana (50-250 personas)",
                "large_enterprise": "Gran Empresa (250+ personas)",
                "solo_entrepreneur": "Emprendedor Individual",
                "agency": "Agencia",
                "consulting_firm": "Firma de Consultoría",
                "tech_company": "Compañía de Tecnología",
                "financial_services": "Servicios Financieros",
                "healthcare": "Atención Médica",
                "retail": "Minorista",
                "manufacturing": "Manufactura",
                "education": "Educación",
                "non_profit": "Sin Fines de Lucro",
                "government": "Gobierno",
                "other": "Otro",
                "next": "Siguiente",
                "previous": "Anterior",
                "finish": "Finalizar",
                "skip": "Saltar",
                "progress": "Progreso",
                "step": "Paso",
                "complete": "Completo",
                "in_progress": "En Progreso",
                "not_started": "No Iniciado",
                "success": "Éxito",
                "error": "Error",
                "warning": "Advertencia",
                "info": "Información",
                "loading": "Cargando",
                "search": "Buscar",
                "filter": "Filtrar",
                "sort": "Ordenar",
                "view": "Ver",
                "edit": "Editar",
                "delete": "Eliminar",
                "add": "Agregar",
                "remove": "Eliminar",
                "yes": "Sí",
                "no": "No",
                "ok": "Aceptar",
                "cancel": "Cancelar",
                "close": "Cerrar",
                "help": "Ayuda",
                "about": "Acerca de",
                "contact": "Contacto",
                "support": "Soporte",
                "documentation": "Documentación",
                "tutorials": "Tutoriales",
                "community": "Comunidad",
                "forum": "Foro",
                "chat": "Chat",
                "feedback": "Comentarios",
                "report_issue": "Reportar Problema",
                "privacy_policy": "Política de Privacidad",
                "terms_of_service": "Términos de Servicio",
                "cookie_policy": "Política de Cookies"
            }
        elif lang == "ja":
            # Japanese translations
            return {
                "app_title": "オーガーオメガRXMプラットフォーム",
                "dashboard": "ダッシュボード",
                "agents": "エージェントチーム",
                "koshas": "コシャ",
                "settings": "設定",
                "mode_switch": "モード切替",
                "orchestration": "オーケストレーション",
                "integration": "統合",
                "essence_mode": "エッセンスモード",
                "smart_mode": "スマートモード",
                "expert_mode": "エキスパートモード",
                "appearance": "外観",
                "behavior": "動作",
                "api_key": "APIキー",
                "auto_optimize": "エージェント形成の自動最適化",
                "auto_sync": "コシャ間での設定自動同期",
                "theme": "テーマ",
                "dark": "ダーク",
                "light": "ライト",
                "performance": "パフォーマンス",
                "high": "高",
                "medium": "中",
                "low": "低",
                "efficiency": "効率",
                "agent_efficiency": "エージェント効率",
                "processing_speed": "処理速度",
                "system_security": "システムセキュリティ",
                "needs_attention": "注意が必要",
                "focus_task": "フォーカスタスク",
                "continue": "続行",
                "pause": "一時停止",
                "configure": "構成",
                "optimization_level": "最適化レベル",
                "subject_matter_expertise": "専門知識",
                "processing_priority": "処理優先度",
                "prime_koshas": "プライムコシャ",
                "domain_koshas": "ドメインコシャ",
                "microagents": "マイクロエージェント",
                "concurrency_level": "並行レベル",
                "memory_allocation": "メモリ割当 (GB)",
                "processing_threads": "処理スレッド",
                "mathematical_optimization": "数理最適化アルゴリズム",
                "subject_expertise_matching": "専門知識一致",
                "advanced_load_balancing": "高度なロードバランシング",
                "save": "保存",
                "reset_to_defaults": "デフォルトにリセット",
                "apply_changes": "変更を適用",
                "convert_to_json": "JSONに変換",
                "natural_language_input": "自然言語入力",
                "json_output": "JSON出力",
                "json_editor": "JSONエディター",
                "configuration_preview": "構成プレビュー",
                "load_defaults": "デフォルトを読み込む",
                "import": "インポート",
                "export": "エクスポート",
                "format": "フォーマット",
                "valid_json": "有効なJSON",
                "invalid_json": "無効なJSON",
                "backups": "バックアップ",
                "system_state": "システム状態",
                "optimization_cycle": "最適化サイクル",
                "run_optimization": "最適化を実行",
                "sync_status": "同期ステータス",
                "company_size": "会社規模",
                "company_type": "会社タイプ",
                "industry": "業界",
                "team_mode": "チームモード",
                "individual_mode": "個人モード",
                "onboarding": "オンボーディング",
                "welcome_message": "オーガーオメガへようこそ",
                "getting_started": "入門",
                "full_kosha_offering": "完全コシャオファー",
                "kosha_bundle": "コシャバンドル",
                "custom_kosha_selection": "カスタムコシャ選択",
                "single_kosha": "単一コシャ",
                "select_company_size": "会社規模を選択してください",
                "select_company_type": "会社タイプを選択してください",
                "select_industry": "業界を選択してください",
                "select_mode": "使用モードを選択してください",
                "select_kosha_option": "コシャオプションを選択してください",
                "micro_startup": "マイクロスタートアップ (<10人)",
                "small_startup": "小規模スタートアップ (10-50人)",
                "medium_enterprise": "中規模企業 (50-250人)",
                "large_enterprise": "大規模企業 (250+人)",
                "solo_entrepreneur": "単独起業家",
                "agency": "代理店",
                "consulting_firm": "コンサルティング会社",
                "tech_company": "テクノロジー会社",
                "financial_services": "金融サービス",
                "healthcare": "医療",
                "retail": "小売",
                "manufacturing": "製造業",
                "education": "教育",
                "non_profit": "非営利",
                "government": "政府",
                "other": "その他",
                "next": "次へ",
                "previous": "前へ",
                "finish": "完了",
                "skip": "スキップ",
                "progress": "進捗",
                "step": "ステップ",
                "complete": "完了",
                "in_progress": "進行中",
                "not_started": "未開始",
                "success": "成功",
                "error": "エラー",
                "warning": "警告",
                "info": "情報",
                "loading": "読み込み中",
                "search": "検索",
                "filter": "フィルター",
                "sort": "ソート",
                "view": "表示",
                "edit": "編集",
                "delete": "削除",
                "add": "追加",
                "remove": "削除",
                "yes": "はい",
                "no": "いいえ",
                "ok": "OK",
                "cancel": "キャンセル",
                "close": "閉じる",
                "help": "ヘルプ",
                "about": "概要",
                "contact": "連絡先",
                "support": "サポート",
                "documentation": "ドキュメント",
                "tutorials": "チュートリアル",
                "community": "コミュニティ",
                "forum": "フォーラム",
                "chat": "チャット",
                "feedback": "フィードバック",
                "report_issue": "問題を報告",
                "privacy_policy": "プライバシーポリシー",
                "terms_of_service": "利用規約",
                "cookie_policy": "クッキーポリシー"
            }
        else:
            # For other languages, return English as fallback
            return default_translations
    
    def _get_economy_ranking(self, country: str) -> int:
        """Get economy ranking for a country"""
        try:
            return TOP_30_ECONOMIES.index(country) + 1
        except ValueError:
            return 999  # Not in top 30
    
    def _load_all_translations(self) -> Dict[str, Dict[str, str]]:
        """Load all available translations"""
        translations = {}
        
        for lang_dir in self.locales_dir.iterdir():
            if lang_dir.is_dir():
                lang = lang_dir.name
                
                # Load base translations
                base_file = lang_dir / "base.json"
                if base_file.exists():
                    with open(base_file, 'r', encoding='utf-8') as f:
                        translations[f"{lang}-base"] = json.load(f)
                
                # Load locale-specific translations
                for locale_file in lang_dir.glob("*.json"):
                    if locale_file.name != "base.json":
                        locale_code = f"{lang}-{locale_file.stem}"
                        with open(locale_file, 'r', encoding='utf-8') as f:
                            translations[locale_code] = json.load(f)
        
        return translations
    
    def get_translation(self, key: str, locale: str = None) -> str:
        """Get a translation for a specific key and locale"""
        if locale is None:
            locale = self.current_locale
        
        # Try to find translation in the specified locale
        translation = self.translations.get(locale, {}).get(key)
        
        # If not found, try base language translation
        if translation is None:
            lang = locale.split('-')[0]
            translation = self.translations.get(f"{lang}-base", {}).get(key)
        
        # If still not found, use English default
        if translation is None:
            translation = self.translations.get("en-base", {}).get(key, key)
        
        return translation
    
    def set_locale(self, locale: str) -> bool:
        """Set the current locale"""
        if locale in self.translations:
            self.current_locale = locale
            return True
        else:
            # Try to find a suitable locale by language
            lang = locale.split('-')[0] if '-' in locale else locale
            for trans_locale in self.translations:
                if trans_locale.startswith(f"{lang}-"):
                    self.current_locale = trans_locale
                    return True
        
        return False
    
    def get_supported_locales(self) -> List[str]:
        """Get list of all supported locales"""
        return list(self.translations.keys())
    
    def get_locales_for_language(self, language: str) -> List[str]:
        """Get all locales for a specific language"""
        return [loc for loc in self.translations.keys() if loc.startswith(f"{language}-")]
    
    def get_locales_for_country(self, country: str) -> List[str]:
        """Get all locales for a specific country"""
        return [
            loc for loc in self.translations.keys() 
            if self.translations[loc].get('country') == country
        ]
    
    def add_custom_translation(self, locale: str, key: str, value: str):
        """Add or update a custom translation"""
        if locale not in self.translations:
            self.translations[locale] = {}
        
        self.translations[locale][key] = value
        
        # Save to file
        self._save_translation_file(locale)
    
    def _save_translation_file(self, locale: str):
        """Save translation file to disk"""
        if locale in self.translations:
            # Determine path
            lang, country = locale.split('-', 1) if '-' in locale else (locale, 'base')
            lang_dir = self.locales_dir / lang
            lang_dir.mkdir(exist_ok=True)
            
            if country == 'base':
                file_path = lang_dir / "base.json"
            else:
                file_path = lang_dir / f"{country}.json"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.translations[locale], f, indent=2, ensure_ascii=False)
    
    def get_economy_info(self) -> Dict[str, int]:
        """Get economy ranking information"""
        return {country: idx+1 for idx, country in enumerate(TOP_30_ECONOMIES)}
    
    def get_relevant_countries(self) -> List[str]:
        """Get list of ROI relevant countries"""
        return ROI_RELEVANT_COUNTRIES
    
    def get_top_languages(self) -> List[str]:
        """Get list of top languages"""
        return TOP_30_LANGUAGES


def create_localization_demo():
    """Create a demo of the localization system"""
    print("=== Augur Omega: Localization System Demo ===\n")
    
    # Initialize localization manager
    loc_manager = LocalizationManager()
    
    print("Supported locales:")
    locales = loc_manager.get_supported_locales()
    print(f"  Total locales: {len(locales)}")
    
    # Show some examples
    print("\nSample translations:")
    languages_to_show = ["en-US", "zh-CN", "es-ES", "ja-JP"]
    
    for lang in languages_to_show:
        loc_manager.set_locale(lang)
        app_title = loc_manager.get_translation("app_title", lang)
        dashboard = loc_manager.get_translation("dashboard", lang)
        print(f"  {lang}: {app_title} | {dashboard}")
    
    print(f"\nTop 10 economies: {TOP_30_ECONOMIES[:10]}")
    print(f"Top 10 languages: {TOP_30_LANGUAGES[:10]}")
    print(f"ROI relevant countries: {ROI_RELEVANT_COUNTRIES[:10]}")
    
    print("\nLanguages by country (US):")
    us_langs = loc_manager.get_locales_for_country("United States")
    print(f"  {us_langs}")
    
    print("\nLocales by language (English):")
    en_locales = loc_manager.get_locales_for_language("en")
    print(f"  {en_locales}")
    
    # Demonstrate adding custom translation
    loc_manager.add_custom_translation("en-US", "demo_key", "This is a demo translation")
    demo_value = loc_manager.get_translation("demo_key", "en-US")
    print(f"\nCustom translation: {demo_value}")


if __name__ == "__main__":
    create_localization_demo()