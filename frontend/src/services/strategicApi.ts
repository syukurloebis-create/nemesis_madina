import axios from "axios";

const API_URL = "/strategic";

export async function getStrategicDashboard() {
    const response = await axios.get(
        `${API_URL}/dashboard`
    );

    return response.data;
}