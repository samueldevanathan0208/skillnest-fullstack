const API_CONFIG = {
    // Automatically detect environment
    BASE_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://127.0.0.1:8000'
        : 'https://skillnest-api.vercel.app' // Replace after deployment
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
