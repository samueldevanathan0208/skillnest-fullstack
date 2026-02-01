const API_CONFIG = {
    BASE_URL: 'https://skillnest-fullstack-5hws.vercel.app'
};

// --- GLOBAL FETCH INTERCEPTION ---
(function () {
    const originalFetch = window.fetch;
    window.fetch = function () {
        let args = Array.from(arguments);
        let resource = args[0];
        let options = args[1] || {};

        // Redirect local calls to production
        if (typeof resource === 'string' && resource.includes('http://127.0.0.1:8000')) {
            resource = resource.replace('http://127.0.0.1:8000', API_CONFIG.BASE_URL);
            args[0] = resource;
        }

        // --- JWT ATTACHMENT ---
        const token = localStorage.getItem('token');
        if (token) {
            options.headers = {
                ...options.headers,
                'Authorization': `Bearer ${token}`
            };
        }

        // Anti-Caching
        if (options.method && options.method.toUpperCase() !== 'GET') {
            options.cache = 'no-store';
            options.headers = {
                ...options.headers,
                'Cache-Control': 'no-cache, no-store, must-revalidate'
            };
        }

        args[1] = options;

        return originalFetch.apply(this, args).then(response => {
            // Global 401 handler (Unauthorized)
            if (response.status === 401 && !resource.includes('/login') && !resource.includes('/create_user')) {
                localStorage.removeItem('token');
                window.location.href = 'login.html';
            }
            return response;
        });
    };
})();

// --- GLOBAL AUTH GUARD ---
if (!window.location.pathname.includes('login.html') &&
    !window.location.pathname.includes('signup.html') &&
    !window.location.pathname.includes('index.html')) {
    if (!localStorage.getItem('token')) {
        window.location.href = 'login.html';
    }
}
