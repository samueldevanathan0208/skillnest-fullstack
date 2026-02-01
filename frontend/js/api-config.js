const API = "https://skillnest-fullstack-5hws.vercel.app";

window.apiFetch = async function (url, options = {}) {

    const token = localStorage.getItem("token");

    options.headers = {
        "Content-Type": "application/json",
        ...(options.headers || {})
    };

    if (token) {
        options.headers["Authorization"] = "Bearer " + token;
    }

    const res = await fetch(API + url, options);

    if (res.status === 401) {
        localStorage.removeItem("token");
        window.location.href = "/pages/login.html";
        return;
    }

    return res;
};
