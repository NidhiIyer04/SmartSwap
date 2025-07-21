// API Service for SmartSwapML
class APIService {
    constructor() {
        this.baseURL = window.location.protocol + '//' + window.location.hostname + ':8000';
        this.token = localStorage.getItem('access_token');
    }

    async login(username, password) {
        try {
            const response = await fetch(`${this.baseURL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            if (!response.ok) {
                throw new Error('Login failed');
            }

            const data = await response.json();
            this.token = data.access_token;
            localStorage.setItem('access_token', this.token);
            return data;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    }

    async makeRequest(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        if (this.token) {
            config.headers.Authorization = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(url, config);

            if (response.status === 401) {
                localStorage.removeItem('access_token');
                this.token = null;
                throw new Error('Authentication required');
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API request error:', error);
            throw error;
        }
    }

    // API Methods
    async getBatteries() {
        return this.makeRequest('/api/batteries');
    }

    async getBattery(batteryId) {
        return this.makeRequest(`/api/batteries/${batteryId}`);
    }

    async getStations() {
        return this.makeRequest('/api/stations');
    }

    async getRouteOptimization(fromLoc, toLoc, batteryId = null) {
        const params = new URLSearchParams({ from_loc: fromLoc, to_loc: toLoc });
        if (batteryId) params.append('battery_id', batteryId);
        return this.makeRequest(`/api/route-optimization?${params}`);
    }

    async getCircularEconomyData() {
        return this.makeRequest('/api/analytics/circular-economy');
    }

    async getMLPerformanceData() {
        return this.makeRequest('/api/analytics/ml-performance');
    }

    async getWeather(location) {
        return this.makeRequest(`/api/weather/${location}`);
    }

    isAuthenticated() {
        return !!this.token;
    }

    logout() {
        localStorage.removeItem('access_token');
        this.token = null;
    }
}

// Export for use in main app
window.APIService = APIService;
