const API = "https://skillnest-fullstack-5hws.vercel.app";

async function apiFetch(url, options = {}) {

    const token = localStorage.getItem("token");
    const isPublic = url === "/login" || url === "/create_user";

    if (!token && !isPublic) {
        alert("Please log in to continue");
        window.location.href = "/pages/login.html";
        return;
    }

    options.headers = {
        "Content-Type": "application/json",
        ...(token ? { "Authorization": "Bearer " + token } : {}),
        ...(options.headers || {})
    };

    const res = await fetch(API + url, options);

    if (res.status === 401 && !isPublic) {
        localStorage.removeItem("token");
        alert("Session expired. Please login again.");
        window.location.href = "/pages/login.html";
        return;
    }

    return res.json();
}

// const API = "https://skillnest-fullstack-5hws.vercel.app";

// window.apiFetch = async function (url, options = {}) {

//     const token = localStorage.getItem("token");

//     options.headers = {
//         "Content-Type": "application/json",
//         ...(options.headers || {})
//     };

//     if (token) {
//         options.headers["Authorization"] = "Bearer " + token;
//     }

//     const res = await fetch(API + url, options);

//     if (res.status === 401) {
//         localStorage.removeItem("token");
//         window.location.href = "/pages/login.html";
//         return;
//     }

//     return res;
// };
