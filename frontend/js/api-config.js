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
        let resource = args[0];
        let options = args[1] || {};

        // Redirect local calls to production Vercel URL
        if (typeof resource === 'string' && resource.includes('http://127.0.0.1:8000')) {
            resource = resource.replace('http://127.0.0.1:8000', API_CONFIG.BASE_URL);
            args[0] = resource;
        }

        // Force Anti-Caching for all non-GET requests (Login, Signup, Progress, etc.)
        if (options.method && options.method.toUpperCase() !== 'GET') {
            options.cache = 'no-store';
            options.headers = {
                ...options.headers,
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            };
            args[1] = options;
        }

        return originalFetch.apply(this, args);
    };
})();
