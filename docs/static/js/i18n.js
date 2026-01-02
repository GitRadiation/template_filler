/**
 * Centralized internationalization (i18n) system
 * Supports multiple languages and persistence via localStorage
 */

const i18n = {
    currentLanguage: localStorage.getItem("app_language") || "es",

    translations: {
        es: {
            // Titles and headers
            page_title: "📄 Generador de Documentos",
            page_subtitle: "Crea documentos profesionales en segundos",
            instructions_header: "ℹ️ Instrucciones",
            instructions_text:
                "Selecciona una plantilla y arrastra tus archivos JSON aquí (puedes seleccionar múltiples). Los documentos se descargarán automáticamente apenas estén listos.",

            // Form
            template_label: "Tipo de Plantilla *",
            template_placeholder: "-- Selecciona una plantilla --",
            template_contract: "Contrato",
            template_invoice: "Factura",
            template_certificate: "Certificado",
            files_label: "Archivos JSON *",
            drag_drop_primary: "Arrastra tus archivos aquí",
            drag_drop_secondary: "o haz clic para seleccionar múltiples archivos",
            btn_submit: "✓ Generar Documentos",
            btn_reset: "⟲ Limpiar",

            // File list
            btn_remove: "✕ Eliminar",

            // Jobs list
            jobs_list_title: "📋 Documentos en Proceso",

            // Job statuses
            status_pending: "Pendiente",
            status_running: "En proceso",
            status_completed: "Completado",
            status_failed: "Error",
            status_timeout: "Tiempo agotado",
            status_emoji_pending: "⏳",
            status_emoji_running: "⚙️",
            status_emoji_completed: "✓",
            status_emoji_failed: "❌",
            status_emoji_timeout: "⏱️",
            status_emoji_unknown: "❓",

            // Job details
            job_created: "Creado",
            btn_download: "⬇️ Descargar",
            btn_remove_job: "🗑️ Eliminar",

            // Alerts and errors
            error_no_template: "Selecciona una plantilla",
            error_no_files: "Selecciona al menos un archivo JSON",
            error_invalid_json: "Solo se permiten archivos JSON",
            error_file_too_large: "El archivo {filename} excede el tamaño máximo de {maxSize} MB",
            error_title: "❌ Error",
            warning_title: "⚠️ Advertencia",
            error_upload: "Error desconocido",
            error_network: "Error de red. Verifica tu conexión.",
            error_timeout: "El proceso tardó demasiado y se canceló",
            alert_ok: "Aceptar",
        },

        en: {
            // Titles and headers
            page_title: "📄 Document Generator",
            page_subtitle: "Create professional documents in seconds",
            instructions_header: "ℹ️ Instructions",
            instructions_text:
                "Select a template and drag your JSON files here (you can select multiple files). Documents will download automatically as soon as they are ready.",

            // Form
            template_label: "Template Type *",
            template_placeholder: "-- Select a template --",
            template_contract: "Contract",
            template_invoice: "Invoice",
            template_certificate: "Certificate",
            files_label: "JSON Files *",
            drag_drop_primary: "Drag your files here",
            drag_drop_secondary: "or click to select multiple files",
            btn_submit: "✓ Generate Documents",
            btn_reset: "⟲ Clear",

            // File list
            btn_remove: "✕ Remove",

            // Jobs list
            jobs_list_title: "📋 Documents Processing",

            // Job statuses
            status_pending: "Pending",
            status_running: "Processing",
            status_completed: "Completed",
            status_failed: "Error",
            status_timeout: "Timeout",
            status_emoji_pending: "⏳",
            status_emoji_running: "⚙️",
            status_emoji_completed: "✓",
            status_emoji_failed: "❌",
            status_emoji_timeout: "⏱️",
            status_emoji_unknown: "❓",

            // Job details
            job_created: "Created",
            btn_download: "⬇️ Download",
            btn_remove_job: "🗑️ Remove",

            // Alerts and errors
            error_no_template: "Select a template",
            error_no_files: "Select at least one JSON file",
            error_invalid_json: "Only JSON files are allowed",
            error_file_too_large: "File {filename} exceeds maximum size of {maxSize} MB",
            error_title: "❌ Error",
            warning_title: "⚠️ Warning",
            error_upload: "Unknown error",
            error_network: "Network error. Check your connection.",
            error_timeout: "Process took too long and was cancelled",
            alert_ok: "OK",
        },
    },

    /**
     * Returns the translated string for a given key
     * @param {string} key - Translation key
     * @param {object} params - Optional parameters to interpolate
     * @returns {string}
     */
    t(key, params = {}) {
        let text =
            this.translations[this.currentLanguage]?.[key] ??
            this.translations.es?.[key] ??
            key;

        Object.entries(params).forEach(([param, value]) => {
            text = text.replace(`{${param}}`, value);
        });

        return text;
    },

    /**
     * Sets the active language and persists it
     * @param {string} language - Language code (e.g. "es", "en")
     */
    setLanguage(language) {
        if (!this.translations[language]) {
            return;
        }

        this.currentLanguage = language;
        localStorage.setItem("app_language", language);

        document.dispatchEvent(
            new CustomEvent("languageChanged", {
                detail: { language },
            })
        );
    },

    /**
     * Returns the current language code
     * @returns {string}
     */
    getLanguage() {
        return this.currentLanguage;
    },

    /**
     * Returns the list of available languages
     * @returns {string[]}
     */
    getAvailableLanguages() {
        return Object.keys(this.translations);
    },
};

// Export for module-based environments
if (typeof module !== "undefined" && module.exports) {
    module.exports = i18n;
}