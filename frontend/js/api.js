const API = "https://skillnest-fullstack-5hws.vercel.app";

async function apiFetch(url, options = {}) {

    const token = localStorage.getItem("token");

    if (!token) {
        alert("Please log in to continue");
        window.location.href = "/pages/login.html";
        return;
    }

    options.headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token,
        ...(options.headers || {})
    };

    const res = await fetch(API + url, options);

    if (res.status === 401) {
        localStorage.removeItem("token");
        alert("Session expired. Please login again.");
        window.location.href = "/pages/login.html";
        return;
    }

    return res.json();
}
