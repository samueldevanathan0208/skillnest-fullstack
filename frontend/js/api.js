const isLocal = window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1" ||
    window.location.protocol === "file:";
const API_BASE = isLocal
    ? "http://127.0.0.1:8000"
    : "https://skillnest-fullstack-5hws.vercel.app";

console.log("%c SKILLNEST API V3 LOADED ", "background: #222; color: #bada55; font-size: 20px;");
console.log("Current API_BASE:", API_BASE);
console.log("Current Environment:", isLocal ? "Localhost" : "Production");
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
// --- Course Data ---
const COURSES_DATA = {
    html: [
        { title: "1. HTML Full Course in Tamil", duration: "Full Course", thumbnail: "https://img.youtube.com/vi/3jkub2c0kLA/hqdefault.jpg", src: "https://www.youtube.com/embed/3jkub2c0kLA" }
    ],
    css: [
        { title: "1. CSS for Beginners in Tamil (Full Course)", duration: "4:00:00", thumbnail: "https://img.youtube.com/vi/l0BTo4VGVVs/hqdefault.jpg", src: "https://www.youtube.com/embed/l0BTo4VGVVs" }
    ],
    fastapi: [
        { title: "1. FastAPI Full Course", duration: "", thumbnail: "https://img.youtube.com/vi/Lu8lXXlstvM/hqdefault.jpg", src: "https://www.youtube.com/embed/Lu8lXXlstvM" }
    ],
    python: [
        { title: "1. Python for Beginners – Basics | Print & Intro (Tamil)", duration: "", thumbnail: "https://img.youtube.com/vi/UHKACm20iS0/hqdefault.jpg", src: "https://www.youtube.com/embed/UHKACm20iS0" },
        { title: "2. Python Video 2", duration: "", thumbnail: "https://img.youtube.com/vi/EJlPeer8lG8/hqdefault.jpg", src: "https://www.youtube.com/embed/EJlPeer8lG8" },
        { title: "3. Python Video 3", duration: "", thumbnail: "https://img.youtube.com/vi/qMlmKLxRuIU/hqdefault.jpg", src: "https://www.youtube.com/embed/qMlmKLxRuIU" },
        { title: "4. Python Video 4", duration: "", thumbnail: "https://img.youtube.com/vi/qnXLERacfvc/hqdefault.jpg", src: "https://www.youtube.com/embed/qnXLERacfvc" },
        { title: "5. Python Video 5", duration: "", thumbnail: "https://img.youtube.com/vi/Xa0IXpmRD0s/hqdefault.jpg", src: "https://www.youtube.com/embed/Xa0IXpmRD0s" },
        { title: "6. Python Video 6", duration: "", thumbnail: "https://img.youtube.com/vi/KqcoSw937iM/hqdefault.jpg", src: "https://www.youtube.com/embed/KqcoSw937iM" },
        { title: "7. Python Video 7", duration: "", thumbnail: "https://img.youtube.com/vi/6KkXID81E4w/hqdefault.jpg", src: "https://www.youtube.com/embed/6KkXID81E4w" },
        { title: "8. Python Video 8", duration: "", thumbnail: "https://img.youtube.com/vi/efkCQKiFTUc/hqdefault.jpg", src: "https://www.youtube.com/embed/efkCQKiFTUc" },
        { title: "9. Python Video 9", duration: "", thumbnail: "https://img.youtube.com/vi/VKMIlMVSQCw/hqdefault.jpg", src: "https://www.youtube.com/embed/VKMIlMVSQCw" },
        { title: "10. Python Video 10", duration: "", thumbnail: "https://img.youtube.com/vi/1rw8j3jJX_E/hqdefault.jpg", src: "https://www.youtube.com/embed/1rw8j3jJX_E" },
        { title: "11. Python Video 11", duration: "", thumbnail: "https://img.youtube.com/vi/4gv-H1MBVEU/hqdefault.jpg", src: "https://www.youtube.com/embed/4gv-H1MBVEU" },
        { title: "12. Python Video 12", duration: "", thumbnail: "https://img.youtube.com/vi/QyM6bq5JzmU/hqdefault.jpg", src: "https://www.youtube.com/embed/QyM6bq5JzmU" }
    ],
    java: [
        { title: "1. Java Introduction in Tamil", duration: "10:15", thumbnail: "https://img.youtube.com/vi/8W0IIdg_Cnk/hqdefault.jpg", src: "https://www.youtube.com/embed/8W0IIdg_Cnk" },
        { title: "2. Setting up Java Environment", duration: "12:30", thumbnail: "https://img.youtube.com/vi/Vz_hKq6Z6S0/hqdefault.jpg", src: "https://www.youtube.com/embed/Vz_hKq6Z6S0" },
        { title: "3. Variables and Data Types", duration: "15:45", thumbnail: "https://img.youtube.com/vi/lMAnN6uV1eE/hqdefault.jpg", src: "https://www.youtube.com/embed/lMAnN6uV1eE" },
        { title: "4. Basic Programs in Java", duration: "11:20", thumbnail: "https://img.youtube.com/vi/r_oQvVOnvG8/hqdefault.jpg", src: "https://www.youtube.com/embed/r_oQvVOnvG8" },
        { title: "5. Operators in Java", duration: "14:10", thumbnail: "https://img.youtube.com/vi/zN9WqP-o1zI/hqdefault.jpg", src: "https://www.youtube.com/embed/zN9WqP-o1zI" },
        { title: "6. If Else Condition in Tamil", duration: "09:50", thumbnail: "https://img.youtube.com/vi/q5uN1mU7l98/hqdefault.jpg", src: "https://www.youtube.com/embed/q5uN1mU7l98" },
        { title: "7. Switch Case Explained", duration: "13:25", thumbnail: "https://img.youtube.com/vi/5H0N_jI8zK8/hqdefault.jpg", src: "https://www.youtube.com/embed/5H0N_jI8zK8" },
        { title: "8. For Loop and While Loop", duration: "16:40", thumbnail: "https://img.youtube.com/vi/6L7V2d0R0Xg/hqdefault.jpg", src: "https://www.youtube.com/embed/6L7V2d0R0Xg" },
        { title: "9. Methods/Functions in Java", duration: "18:15", thumbnail: "https://img.youtube.com/vi/f3k9wO0j_Z4/hqdefault.jpg", src: "https://www.youtube.com/embed/f3k9wO0j_Z4" },
        { title: "10. Classes and Objects Intro", duration: "20:30", thumbnail: "https://img.youtube.com/vi/T9v8xI0y_W1/hqdefault.jpg", src: "https://www.youtube.com/embed/T9v8xI0y_W1" },
        { title: "11. Abstract and Interface", duration: "15:20", thumbnail: "https://img.youtube.com/vi/8XTcagpacRg/hqdefault.jpg", src: "https://www.youtube.com/embed/8XTcagpacRg" },
        { title: "12. Exception Handling", duration: "12:10", thumbnail: "https://img.youtube.com/vi/7uXfOWalJW4/hqdefault.jpg", src: "https://www.youtube.com/embed/7uXfOWalJW4" },
        { title: "13. Collections Framework", duration: "25:00", thumbnail: "https://img.youtube.com/vi/-yJC5N3CNL8/hqdefault.jpg", src: "https://www.youtube.com/embed/-yJC5N3CNL8" },
        { title: "14. Multithreading in Java", duration: "20:00", thumbnail: "https://img.youtube.com/vi/BtaIHsGv5dA/hqdefault.jpg", src: "https://www.youtube.com/embed/BtaIHsGv5dA" },
        { title: "15. Java 8 Features", duration: "18:00", thumbnail: "https://img.youtube.com/vi/of9qSRvsgXQ/hqdefault.jpg", src: "https://www.youtube.com/embed/of9qSRvsgXQ" },
        { title: "16. Java DBMS Connection", duration: "22:00", thumbnail: "https://img.youtube.com/vi/sMI4pXjQBRU/hqdefault.jpg", src: "https://www.youtube.com/embed/sMI4pXjQBRU" }
    ],
    react: [
        { title: "1. React Video 1", duration: "", thumbnail: "https://img.youtube.com/vi/UYFtY7Acngw/hqdefault.jpg", src: "https://www.youtube.com/embed/UYFtY7Acngw" },
        { title: "2. React Video 2", duration: "", thumbnail: "https://img.youtube.com/vi/SAUBFF4e50k/hqdefault.jpg", src: "https://www.youtube.com/embed/SAUBFF4e50k" },
        { title: "3. React Video 3", duration: "", thumbnail: "https://img.youtube.com/vi/-kGdnjwTQww/hqdefault.jpg", src: "https://www.youtube.com/embed/-kGdnjwTQww" },
        { title: "4. React Video 4", duration: "", thumbnail: "https://img.youtube.com/vi/c1KKItIY8tg/hqdefault.jpg", src: "https://www.youtube.com/embed/c1KKItIY8tg" },
        { title: "5. React Video 5", duration: "", thumbnail: "https://img.youtube.com/vi/ODcSDqr9nDM/hqdefault.jpg", src: "https://www.youtube.com/embed/ODcSDqr9nDM" },
        { title: "6. React Video 6", duration: "", thumbnail: "https://img.youtube.com/vi/8Viv14aUQfY/hqdefault.jpg", src: "https://www.youtube.com/embed/8Viv14aUQfY" },
        { title: "7. React Video 7", duration: "", thumbnail: "https://img.youtube.com/vi/_0b9h0IKnA0/hqdefault.jpg", src: "https://www.youtube.com/embed/_0b9h0IKnA0" },
        { title: "8. React Video 8", duration: "", thumbnail: "https://img.youtube.com/vi/R0chQjbH6vw/hqdefault.jpg", src: "https://www.youtube.com/embed/R0chQjbH6vw" },
        { title: "9. React Video 9", duration: "", thumbnail: "https://img.youtube.com/vi/oSmvHbnPCHA/hqdefault.jpg", src: "https://www.youtube.com/embed/oSmvHbnPCHA" },
        { title: "10. React Video 10", duration: "", thumbnail: "https://img.youtube.com/vi/z3pxOkL0b04/hqdefault.jpg", src: "https://www.youtube.com/embed/z3pxOkL0b04" },
        { title: "11. React Video 11", duration: "", thumbnail: "https://img.youtube.com/vi/gxhDDT9zC0w/hqdefault.jpg", src: "https://www.youtube.com/embed/gxhDDT9zC0w" },
        { title: "12. React Video 12", duration: "", thumbnail: "https://img.youtube.com/vi/H8M9K-UVfsU/hqdefault.jpg", src: "https://www.youtube.com/embed/H8M9K-UVfsU" }
    ],
    postgresql: [
        { title: "1. Postgres Video 1", duration: "", thumbnail: "https://img.youtube.com/vi/vTyg_wHwsu0/hqdefault.jpg", src: "https://www.youtube.com/embed/vTyg_wHwsu0" },
        { title: "2. Postgres Video 2", duration: "", thumbnail: "https://img.youtube.com/vi/Ys1dFK6wsMs/hqdefault.jpg", src: "https://www.youtube.com/embed/Ys1dFK6wsMs" },
        { title: "3. Postgres Video 3", duration: "", thumbnail: "https://img.youtube.com/vi/QKxjSSF0D6M/hqdefault.jpg", src: "https://www.youtube.com/embed/QKxjSSF0D6M" },
        { title: "4. Postgres Video 4", duration: "", thumbnail: "https://img.youtube.com/vi/f7HbOH5R1fI/hqdefault.jpg", src: "https://www.youtube.com/embed/f7HbOH5R1fI" },
        { title: "5. Postgres Video 5", duration: "", thumbnail: "https://img.youtube.com/vi/UAs11wup33E/hqdefault.jpg", src: "https://www.youtube.com/embed/UAs11wup33E" },
        { title: "6. Postgres Video 6", duration: "", thumbnail: "https://img.youtube.com/vi/vvW2cRPkz4A/hqdefault.jpg", src: "https://www.youtube.com/embed/vvW2cRPkz4A" },
        { title: "7. Postgres Video 7", duration: "", thumbnail: "https://img.youtube.com/vi/9PMvJUx4DTo/hqdefault.jpg", src: "https://www.youtube.com/embed/9PMvJUx4DTo" },
        { title: "8. Postgres Video 8", duration: "", thumbnail: "https://img.youtube.com/vi/vv9ym-ml_GQ/hqdefault.jpg", src: "https://www.youtube.com/embed/vv9ym-ml_GQ" },
        { title: "9. Postgres Video 9", duration: "", thumbnail: "https://img.youtube.com/vi/dlyEme9C49Q/hqdefault.jpg", src: "https://www.youtube.com/embed/dlyEme9C49Q" },
        { title: "10. Postgres Video 10", duration: "", thumbnail: "https://img.youtube.com/vi/4Dp7mvt78pU/hqdefault.jpg", src: "https://www.youtube.com/embed/4Dp7mvt78pU" },
        { title: "11. Postgres Video 11", duration: "", thumbnail: "https://img.youtube.com/vi/kv1qS1iG7ic/hqdefault.jpg", src: "https://www.youtube.com/embed/kv1qS1iG7ic" },
        { title: "12. Postgres Video 12", duration: "", thumbnail: "https://img.youtube.com/vi/MT5mXKKg2gE/hqdefault.jpg", src: "https://www.youtube.com/embed/MT5mXKKg2gE" }
    ],
    js: [
        { title: "1. JavaScript Video 1", duration: "1", thumbnail: "https://img.youtube.com/vi/YrOkVD_YUro/hqdefault.jpg", src: "https://www.youtube.com/embed/YrOkVD_YUro" },
        { title: "2. JavaScript Video 2", duration: "1", thumbnail: "https://img.youtube.com/vi/4zlr_Ez_EYo/hqdefault.jpg", src: "https://www.youtube.com/embed/4zlr_Ez_EYo" },
        { title: "3. JavaScript Video 3", duration: "1", thumbnail: "https://img.youtube.com/vi/AoEohhf6Avc/hqdefault.jpg", src: "https://www.youtube.com/embed/AoEohhf6Avc" },
        { title: "4. JavaScript Video 4", duration: "1", thumbnail: "https://img.youtube.com/vi/xs8bTPpONqA/hqdefault.jpg", src: "https://www.youtube.com/embed/xs8bTPpONqA" },
        { title: "5. JavaScript Video 5", duration: "1", thumbnail: "https://img.youtube.com/vi/BSXQC4ZN8p4/hqdefault.jpg", src: "https://www.youtube.com/embed/BSXQC4ZN8p4" },
        { title: "6. JavaScript Video 6", duration: "1", thumbnail: "https://img.youtube.com/vi/csFBVXrsxck/hqdefault.jpg", src: "https://www.youtube.com/embed/csFBVXrsxck" },
        { title: "7. JavaScript Video 7", duration: "1", thumbnail: "https://img.youtube.com/vi/Ub87voAYIWQ/hqdefault.jpg", src: "https://www.youtube.com/embed/Ub87voAYIWQ" },
        { title: "8. JavaScript Video 8", duration: "1", thumbnail: "https://img.youtube.com/vi/eTaqetO9Ey8/hqdefault.jpg", src: "https://www.youtube.com/embed/eTaqetO9Ey8" },
        { title: "9. JavaScript Video 9", duration: "1", thumbnail: "https://img.youtube.com/vi/fbQ7xxXCusE/hqdefault.jpg", src: "https://www.youtube.com/embed/fbQ7xxXCusE" },
        { title: "10. JavaScript Video 10", duration: "1", thumbnail: "https://img.youtube.com/vi/OOHduxkXQAw/hqdefault.jpg", src: "https://www.youtube.com/embed/OOHduxkXQAw" }
    ]
};

// --- Progress Logic ---
function getProgressStats(progressData) {
    let totalVideosAcrossAll = 0;
    let totalCompletedAcrossAll = 0;
    let completedCoursesCount = 0;

    const courseStats = {};

    for (const [courseId, videos] of Object.entries(COURSES_DATA)) {
        const totalInCourse = videos.length;
        const completedInCourseList = progressData[courseId] || [];
        const completedInCourseCount = new Set(completedInCourseList).size;

        courseStats[courseId] = {
            total: totalInCourse,
            completed: completedInCourseCount,
            percentage: totalInCourse > 0 ? Math.round((completedInCourseCount / totalInCourse) * 100) : 0,
            isFinished: completedInCourseCount === totalInCourse && totalInCourse > 0
        };

        totalVideosAcrossAll += totalInCourse;
        totalCompletedAcrossAll += completedInCourseCount;
        if (courseStats[courseId].isFinished) {
            completedCoursesCount++;
        }
    }

    const overallPercentage = totalVideosAcrossAll > 0
        ? Math.round((totalCompletedAcrossAll / totalVideosAcrossAll) * 100)
        : 0;

    return {
        overallPercentage,
        totalCompletedAcrossAll,
        totalVideosAcrossAll,
        completedCoursesCount,
        totalCoursesCount: Object.keys(COURSES_DATA).length,
        courseStats
    };
}
