const API_BASE = "https://skillnest-fullstack-5hws.vercel.app";

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
        const response = await fetch(API_BASE + url, {
            ...options,
            headers
        });

        if (response.status === 401 && !isPublic) {
            console.error("401 Unauthorized for:", url, "Token used:", token ? "YES (check console)" : "NO");
            if (token) console.log("Token value:", token);
            localStorage.removeItem("token");
            alert("Session expired. Please login again.");
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
