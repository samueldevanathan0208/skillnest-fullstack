const API_CONFIG = {
    // Production Vercel Backend
    BASE_URL: 'https://skillnest-fullstack-5hws.vercel.app'
};

// --- GLOBAL FETCH INTERCEPTION (Monkey Patch) ---
// Since we cannot modify HTML files, this logic redirects all hardcoded 
// 'http://127.0.0.1:8000' calls to the dynamic API_CONFIG.BASE_URL automatically.
(function () {
    const originalFetch = window.fetch;
    window.fetch = function () {
        let args = Array.from(arguments);
        if (typeof args[0] === 'string' && args[0].includes('http://127.0.0.1:8000')) {
            args[0] = args[0].replace('http://127.0.0.1:8000', API_CONFIG.BASE_URL);
            console.log(`[API_CONFIG] Redirected call: ${arguments[0]} -> ${args[0]}`);
        }
        return originalFetch.apply(this, args);
    };
})();
