import axios from "axios";

const api = axios.create({
    baseURL: "/api/v1",
    timeout: 10000,
    headers: {
        "Content-Type": "application/json",
    },
});

// Interceptor untuk menambahkan token jika ada
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("access_token");
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

export default api;
