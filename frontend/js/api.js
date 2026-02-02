const API_BASE = "https://skillnest-fullstack-5hws.vercel.app";
console.log("Using API_BASE:", API_BASE);
console.log("Current App Path:", window.location.pathname);

async function apiFetch(url, options = {}) {
    const token = localStorage.getItem("token");
    const isPublic = url === "/login" || url === "/create_user";

    const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {})
    };

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
        console.log(`Sending token for ${url}`);
    } else {
        console.warn(`No token found for ${url}`);
    }

    try {
        console.log(`Fetching from: ${API_BASE}${url}`);
        const response = await fetch(API_BASE + url, {
            ...options,
            headers
        });

        if (response.status === 401 && !isPublic) {
            const errorBody = await response.json().catch(() => ({}));
            const detail = errorBody.detail || "Unknown error";

            console.error("401 Unauthorized for:", url, "Token used:", token ? "YES (check console)" : "NO");
            if (token) console.log("Token value:", token);
            console.log("Error Detail:", detail);

            localStorage.removeItem("token");
            alert(`Session expired. Please login again.\nReason: ${detail}`);
            window.location.href = "/pages/login.html";
            return;
        }

        if (!response.ok) {
            const errorData = await response.json();
            console.error(`API Error (${response.status}):`, errorData);
            return errorData;
        }

        return await response.json();
    } catch (error) {
        console.error("Fetch Error:", error);
        throw error;
    }
}
