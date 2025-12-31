/**
 * Sistema de internacionalización (i18n) centralizado
 * Soporta múltiples idiomas y almacenamiento en localStorage
 */

const i18n = {
    currentLanguage: localStorage.getItem('app_language') || 'es',
    
    translations: {
        es: {
            // Títulos y encabezados
            'page_title': '📄 Generador de Documentos',
            'page_subtitle': 'Crea documentos profesionales en segundos',
            'instructions': 'ℹ️ Instrucciones',
            'instructions_text': 'Selecciona una plantilla y arrastra tus archivos JSON aquí (puedes seleccionar múltiples). Los documentos se descargarán automáticamente apenas estén listos.',
            
            // Formulario
            'template_label': 'Tipo de Plantilla *',
            'template_placeholder': '-- Selecciona una plantilla --',
            'template_contract': 'Contrato',
            'template_invoice': 'Factura',
            'template_certificate': 'Certificado',
            'files_label': 'Archivos JSON *',
            'drag_drop_primary': 'Arrastra tus archivos aquí',
            'drag_drop_secondary': 'o haz clic para seleccionar múltiples archivos',
            'btn_submit': '✓ Generar Documentos',
            'btn_reset': '⟲ Limpiar',
            
            // Lista de archivos
            'btn_remove': '✕ Eliminar',
            
            // Lista de trabajos
            'jobs_list_title': '📋 Documentos en Proceso',
            
            // Estados de trabajos
            'status_pending': 'Pendiente',
            'status_running': 'En proceso',
            'status_completed': 'Completado',
            'status_failed': 'Error',
            'status_emoji_pending': '⏳',
            'status_emoji_running': '⚙️',
            'status_emoji_completed': '✓',
            'status_emoji_failed': '❌',
            'status_emoji_unknown': '❓',
            
            // Detalles de trabajos
            'job_created': 'Creado',
            'btn_download': '⬇️ Descargar',
            'btn_remove_job': '🗑️ Eliminar',
            
            // Alertas y errores
            'error_no_template': 'Selecciona una plantilla',
            'error_no_files': 'Selecciona al menos un archivo JSON',
            'error_invalid_json': 'Por favor, selecciona solo archivos JSON',
            'error_title': '❌ Error',
            'warning_title': '⚠️ Advertencia',
            'warning_invalid_json': 'Por favor, selecciona solo archivos JSON válidos',
            'error_upload': 'Error desconocido',
            'error_checking_status': 'No se pudo verificar el estado',
            
            // Idioma
            'language': 'Idioma',
            'language_es': 'Español',
            'language_en': 'English',
        },
        
        en: {
            // Titles and headers
            'page_title': '📄 Document Generator',
            'page_subtitle': 'Create professional documents in seconds',
            'instructions': 'ℹ️ Instructions',
            'instructions_text': 'Select a template and drag your JSON files here (you can select multiple files). Documents will download automatically as soon as they are ready.',
            
            // Form
            'template_label': 'Template Type *',
            'template_placeholder': '-- Select a template --',
            'template_contract': 'Contract',
            'template_invoice': 'Invoice',
            'template_certificate': 'Certificate',
            'files_label': 'JSON Files *',
            'drag_drop_primary': 'Drag your files here',
            'drag_drop_secondary': 'or click to select multiple files',
            'btn_submit': '✓ Generate Documents',
            'btn_reset': '⟲ Clear',
            
            // File list
            'btn_remove': '✕ Remove',
            
            // Jobs list
            'jobs_list_title': '📋 Documents Processing',
            
            // Job statuses
            'status_pending': 'Pending',
            'status_running': 'Processing',
            'status_completed': 'Completed',
            'status_failed': 'Error',
            'status_emoji_pending': '⏳',
            'status_emoji_running': '⚙️',
            'status_emoji_completed': '✓',
            'status_emoji_failed': '❌',
            'status_emoji_unknown': '❓',
            
            // Job details
            'job_created': 'Created',
            'btn_download': '⬇️ Download',
            'btn_remove_job': '🗑️ Remove',
            
            // Alerts and errors
            'error_no_template': 'Select a template',
            'error_no_files': 'Select at least one JSON file',
            'error_invalid_json': 'Please select only valid JSON files',
            'error_title': '❌ Error',
            'warning_title': '⚠️ Warning',
            'warning_invalid_json': 'Please select only valid JSON files',
            'error_upload': 'Unknown error',
            'error_checking_status': 'Could not verify status',
            
            // Language
            'language': 'Language',
            'language_es': 'Español',
            'language_en': 'English',
        }
    },
    
    /**
     * Obtiene la traducción de una clave
     * @param {string} key - Clave de traducción
     * @param {object} params - Parámetros para reemplazar en la traducción
     * @returns {string} Traducción
     */
    t(key, params = {}) {
        let text = this.translations[this.currentLanguage]?.[key] || this.translations['es']?.[key] || key;
        
        // Reemplazar parámetros si existen
        Object.keys(params).forEach(param => {
            text = text.replace(`{${param}}`, params[param]);
        });
        
        return text;
    },
    
    /**
     * Establece el idioma actual
     * @param {string} lang - Código de idioma ('es' o 'en')
     */
    setLanguage(lang) {
        if (this.translations[lang]) {
            this.currentLanguage = lang;
            localStorage.setItem('app_language', lang);
            
            // Disparar evento para que otros componentes se actualicen
            document.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: lang } }));
        }
    },
    
    /**
     * Obtiene el idioma actual
     * @returns {string} Código de idioma
     */
    getLanguage() {
        return this.currentLanguage;
    },
    
    /**
     * Obtiene todos los idiomas disponibles
     * @returns {array} Array de códigos de idioma
     */
    getAvailableLanguages() {
        return Object.keys(this.translations);
    }
};

// Exportar para uso en otros módulos (si es necesario)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = i18n;
}
