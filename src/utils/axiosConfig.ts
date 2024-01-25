import axios from 'axios';

const axiosInstance = axios.create({
    baseURL: 'http://localhost:5000', // Your Flask API URL
    // other configurations
});

export default axiosInstance;
