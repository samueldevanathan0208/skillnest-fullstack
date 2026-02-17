const API_BASE = "https://skillnest-fullstack-5hws.vercel.app";
// const API_BASE = "http://127.0.0.1:8000";
console.log("%c SKILLNEST API V3 LOADED ", "background: #222; color: #bada55; font-size: 20px;");
console.log("Current API_BASE:", API_BASE);
console.log("Current Page Path:", window.location.pathname);

async function apiFetch(url, options = {}) {
    const token = localStorage.getItem("token");
    const isPublic = url === "/login" || url === "/create_user";

    const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {})
    };

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
        console.log(`[AUTH] Sending token for: ${url} (length: ${token.length})`);
    } else {
        if (!isPublic) console.warn(`[AUTH] NO TOKEN found in storage for: ${url}`);
    }

    try {
        console.log(`[API] Fetching: ${API_BASE}${url}`);
        const response = await fetch(API_BASE + url, {
            ...options,
            headers
        });

        // Handle 401 Unauthorized
        if (response.status === 401 && !isPublic) {
            const errorBody = await response.json().catch(() => ({}));
            const detail = errorBody.detail || "No specific reason provided by server";

            console.error("%c 401 UNAUTHORIZED ", "background: red; color: white;", {
                url,
                tokenSent: !!token,
                serverReason: detail
            });

            if (token) {
                console.log("Token used during failure:", token);
            }

            // AUTO-LOGOUT ONLY IF ABSOLUTELY NECESSARY
            // To prevent immediate redirection loops during debugging, we use a confirm box
            const msg = `SESSION ERROR at ${url}\n\nReason: ${detail}\n\nDo you want to go back to LOGIN?`;

            if (confirm(msg)) {
                localStorage.removeItem("token");
                window.location.href = "/pages/login.html";
            }
            return;
        }

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ "error": "Could not parse error JSON" }));
            console.error(`[API ERROR] status: ${response.status}`, errorData);
            return errorData;
        }

        const data = await response.json();
        console.log(`[JSON RECEIVED] from ${url}:`, data);
        return data;

    } catch (error) {
        console.error("[FETCH ERROR] Network problem or CORS issue:", error);
        throw error;
    }
}
