const API_CONFIG = {
    // Automatically detect environment
    BASE_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://127.0.0.1:8000'
        : 'https://skillnest-api.vercel.app' // Replace after deployment
};
