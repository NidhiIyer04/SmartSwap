// SmartSwapML Dashboard Application
class SmartSwapMLDashboard {
    constructor() {
        this.currentLanguage = 'en';
        this.currentSection = 'dashboard';
        this.charts = {};
        this.mockData = {
            batteries: [
                {"id": "BAT001", "health": 95, "soc": 87, "cycles": 245, "temp": 32, "location": "Mumbai", "status": "active"},
                {"id": "BAT002", "health": 87, "soc": 72, "cycles": 567, "temp": 28, "location": "Pune", "status": "active"},
                {"id": "BAT003", "health": 92, "soc": 91, "cycles": 123, "temp": 30, "location": "Bangalore", "status": "charging"},
                {"id": "BAT004", "health": 78, "soc": 45, "cycles": 892, "temp": 35, "location": "Chennai", "status": "maintenance"}
            ],
            stations: [
                {"id": "ST001", "name": "Mumbai Central", "lat": 19.0760, "lng": 72.8777, "batteries": 24, "utilization": 85},
                {"id": "ST002", "name": "Pune Highway", "lat": 18.5204, "lng": 73.8567, "batteries": 18, "utilization": 72},
                {"id": "ST003", "name": "Bangalore Tech Park", "lat": 12.9716, "lng": 77.5946, "batteries": 32, "utilization": 91}
            ],
            routes: [
                {"from": "Mumbai", "to": "Pune", "distance": 148, "elevation_gain": 650, "predicted_range": 142, "confidence": 94},
                {"from": "Pune", "to": "Bangalore", "distance": 842, "elevation_gain": 450, "predicted_range": 785, "confidence": 89}
            ],
            materials: {
                "lithium": {"recovered": 78, "target": 85, "trend": "up"},
                "cobalt": {"recovered": 85, "target": 90, "trend": "stable"},
                "nickel": {"recovered": 92, "target": 95, "trend": "up"}
            },
            translations: {
                "en": {
                    "dashboard": "Dashboard",
                    "battery_health": "Battery Health",
                    "route_optimizer": "Route Optimizer",
                    "circular_economy": "Circular Economy",
                    "station_placement": "Station Placement",
                    "analytics": "Analytics",
                    "dashboard_overview": "Dashboard Overview",
                    "dashboard_subtitle": "Real-time monitoring of your battery fleet",
                    "total_batteries": "Total Batteries",
                    "avg_health": "Average Health",
                    "active_stations": "Active Stations",
                    "utilization": "Utilization",
                    "fleet_status": "Fleet Status",
                    "recent_alerts": "Recent Alerts",
                    "health_subtitle": "Detailed health monitoring and predictions",
                    "health_overview": "Health Overview",
                    "degradation_trends": "Degradation Trends",
                    "route_subtitle": "Terrain-aware route planning with range prediction",
                    "route_planning": "Route Planning",
                    "route_analysis": "Route Analysis",
                    "from": "From",
                    "to": "To",
                    "calculate_route": "Calculate Route",
                    "circular_subtitle": "Material recovery and sustainability metrics",
                    "material_recovery": "Material Recovery",
                    "carbon_footprint": "Carbon Footprint",
                    "co2_saved": "CO₂ Saved",
                    "efficiency": "Efficiency",
                    "placement_subtitle": "Optimal station location analytics",
                    "coverage_analysis": "Coverage Analysis",
                    "demand_prediction": "Demand Prediction",
                    "analytics_subtitle": "ML predictions and performance insights",
                    "ml_performance": "ML Model Performance",
                    "prediction_accuracy": "Prediction Accuracy",
                    "connected": "Connected",
                    "loading": "Loading...",
                    "subtitle": "Intelligent Battery Management"
                },
                "es": {
                    "dashboard": "Panel de Control",
                    "battery_health": "Salud de la Batería",
                    "route_optimizer": "Optimizador de Rutas",
                    "circular_economy": "Economía Circular",
                    "station_placement": "Ubicación de Estaciones",
                    "analytics": "Análisis",
                    "dashboard_overview": "Vista General del Panel",
                    "dashboard_subtitle": "Monitoreo en tiempo real de su flota de baterías",
                    "total_batteries": "Total de Baterías",
                    "avg_health": "Salud Promedio",
                    "active_stations": "Estaciones Activas",
                    "utilization": "Utilización",
                    "fleet_status": "Estado de la Flota",
                    "recent_alerts": "Alertas Recientes",
                    "health_subtitle": "Monitoreo detallado de salud y predicciones",
                    "health_overview": "Vista General de Salud",
                    "degradation_trends": "Tendencias de Degradación",
                    "route_subtitle": "Planificación de rutas consciente del terreno",
                    "route_planning": "Planificación de Rutas",
                    "route_analysis": "Análisis de Rutas",
                    "from": "Desde",
                    "to": "Hasta",
                    "calculate_route": "Calcular Ruta",
                    "circular_subtitle": "Recuperación de materiales y métricas de sostenibilidad",
                    "material_recovery": "Recuperación de Materiales",
                    "carbon_footprint": "Huella de Carbono",
                    "co2_saved": "CO₂ Ahorrado",
                    "efficiency": "Eficiencia",
                    "placement_subtitle": "Análisis de ubicación óptima de estaciones",
                    "coverage_analysis": "Análisis de Cobertura",
                    "demand_prediction": "Predicción de Demanda",
                    "analytics_subtitle": "Predicciones de ML e insights de rendimiento",
                    "ml_performance": "Rendimiento del Modelo ML",
                    "prediction_accuracy": "Precisión de Predicción",
                    "connected": "Conectado",
                    "loading": "Cargando...",
                    "subtitle": "Gestión Inteligente de Baterías"
                },
                "fr": {
                    "dashboard": "Tableau de Bord",
                    "battery_health": "Santé des Batteries",
                    "route_optimizer": "Optimiseur de Route",
                    "circular_economy": "Économie Circulaire",
                    "station_placement": "Placement de Stations",
                    "analytics": "Analytiques",
                    "dashboard_overview": "Vue d'ensemble du Tableau de Bord",
                    "dashboard_subtitle": "Surveillance en temps réel de votre flotte de batteries",
                    "total_batteries": "Total des Batteries",
                    "avg_health": "Santé Moyenne",
                    "active_stations": "Stations Actives",
                    "utilization": "Utilisation",
                    "fleet_status": "État de la Flotte",
                    "recent_alerts": "Alertes Récentes",
                    "connected": "Connecté",
                    "loading": "Chargement...",
                    "subtitle": "Gestion Intelligente des Batteries"
                },
                "de": {
                    "dashboard": "Dashboard",
                    "battery_health": "Batteriezustand",
                    "route_optimizer": "Route Optimizer",
                    "circular_economy": "Kreislaufwirtschaft",
                    "station_placement": "Stationsplatzierung",
                    "analytics": "Analytik",
                    "connected": "Verbunden",
                    "loading": "Laden...",
                    "subtitle": "Intelligentes Batteriemanagement"
                },
                "zh": {
                    "dashboard": "仪表板",
                    "battery_health": "电池健康",
                    "route_optimizer": "路线优化器",
                    "circular_economy": "循环经济",
                    "station_placement": "站点布置",
                    "analytics": "分析",
                    "connected": "已连接",
                    "loading": "加载中...",
                    "subtitle": "智能电池管理"
                }
            }
        };

        this.init();
    }

    async init() {
        await this.setupEventListeners();
        this.updateTranslations();
        await this.loadDashboard();
        this.hideLoading();
        this.startRealTimeUpdates();
    }

    async setupEventListeners() {
        // Language selector
        const languageSelector = document.getElementById('language-selector');
        if (languageSelector) {
            languageSelector.addEventListener('change', (e) => {
                this.currentLanguage = e.target.value;
                this.updateTranslations();
                console.log('Language changed to:', this.currentLanguage);
            });
        }

        // Navigation tabs - use event delegation for better reliability
        const navTabs = document.querySelector('.nav__tabs');
        if (navTabs) {
            navTabs.addEventListener('click', (e) => {
                e.preventDefault();
                const button = e.target.closest('.nav__tab');
                if (button && button.dataset.section) {
                    const section = button.dataset.section;
                    console.log('Navigation clicked:', section);
                    this.navigateToSection(section);
                }
            });
        }

        // Route calculator - set up after DOM is ready
        setTimeout(() => {
            const calculateRouteBtn = document.getElementById('calculate-route');
            if (calculateRouteBtn) {
                calculateRouteBtn.addEventListener('click', () => {
                    console.log('Calculate route clicked');
                    this.calculateRoute();
                });
            }
        }, 100);
    }

    updateTranslations() {
        const translations = this.mockData.translations[this.currentLanguage] || this.mockData.translations.en;
        
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            if (translations[key]) {
                element.textContent = translations[key];
            }
        });
    }

    navigateToSection(sectionName) {
        console.log('Navigating to section:', sectionName);
        
        // Update active tab
        document.querySelectorAll('.nav__tab').forEach(tab => {
            tab.classList.remove('nav__tab--active');
        });
        const activeTab = document.querySelector(`[data-section="${sectionName}"]`);
        if (activeTab) {
            activeTab.classList.add('nav__tab--active');
            console.log('Tab activated:', sectionName);
        }

        // Update active section
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('section--active');
            section.style.display = 'none';
        });
        const activeSection = document.getElementById(sectionName);
        if (activeSection) {
            activeSection.classList.add('section--active');
            activeSection.style.display = 'block';
            console.log('Section displayed:', sectionName);
        }

        this.currentSection = sectionName;

        // Load section-specific content with delay to ensure DOM is ready
        setTimeout(() => {
            switch (sectionName) {
                case 'dashboard':
                    this.loadDashboard();
                    break;
                case 'battery-health':
                    this.loadBatteryHealth();
                    break;
                case 'route-optimizer':
                    this.loadRouteOptimizer();
                    break;
                case 'circular-economy':
                    this.loadCircularEconomy();
                    break;
                case 'station-placement':
                    this.loadStationPlacement();
                    break;
                case 'analytics':
                    this.loadAnalytics();
                    break;
            }
        }, 150);
    }

    async loadDashboard() {
        console.log('Loading Dashboard');
        // Update KPI cards
        this.updateKPIs();
        
        // Load battery grid
        this.loadBatteryGrid();
        
        // Load alerts
        this.loadAlerts();
    }

    updateKPIs() {
        const batteries = this.mockData.batteries;
        const stations = this.mockData.stations;

        const totalBatteriesEl = document.getElementById('total-batteries');
        const avgHealthEl = document.getElementById('avg-health');
        const activeStationsEl = document.getElementById('active-stations');
        const utilizationEl = document.getElementById('utilization');

        if (totalBatteriesEl) totalBatteriesEl.textContent = batteries.length;
        
        if (avgHealthEl) {
            const avgHealth = Math.round(batteries.reduce((sum, bat) => sum + bat.health, 0) / batteries.length);
            avgHealthEl.textContent = `${avgHealth}%`;
        }
        
        if (activeStationsEl) activeStationsEl.textContent = stations.length;
        
        if (utilizationEl) {
            const avgUtilization = Math.round(stations.reduce((sum, station) => sum + station.utilization, 0) / stations.length);
            utilizationEl.textContent = `${avgUtilization}%`;
        }
    }

    loadBatteryGrid() {
        const batteryGrid = document.getElementById('battery-grid');
        if (!batteryGrid) return;
        
        batteryGrid.innerHTML = '';

        this.mockData.batteries.forEach(battery => {
            const batteryCard = this.createBatteryCard(battery);
            batteryGrid.appendChild(batteryCard);
        });
    }

    createBatteryCard(battery) {
        const card = document.createElement('div');
        card.className = 'battery-card fade-in';
        
        const statusClass = `battery-card__status--${battery.status}`;
        
        card.innerHTML = `
            <div class="battery-card__header">
                <div class="battery-card__id">${battery.id}</div>
                <div class="battery-card__status ${statusClass}">${battery.status}</div>
            </div>
            <div class="battery-card__metrics">
                <div class="battery-metric">
                    <div class="battery-metric__value">${Math.round(battery.health)}%</div>
                    <div class="battery-metric__label">Health</div>
                </div>
                <div class="battery-metric">
                    <div class="battery-metric__value">${Math.round(battery.soc)}%</div>
                    <div class="battery-metric__label">SOC</div>
                </div>
                <div class="battery-metric">
                    <div class="battery-metric__value">${battery.cycles}</div>
                    <div class="battery-metric__label">Cycles</div>
                </div>
                <div class="battery-metric">
                    <div class="battery-metric__value">${Math.round(battery.temp)}°C</div>
                    <div class="battery-metric__label">Temp</div>
                </div>
            </div>
            <div class="battery-card__footer">
                <div class="battery-card__location">📍 ${battery.location}</div>
            </div>
        `;
        
        return card;
    }

    loadAlerts() {
        const alertsList = document.getElementById('alerts-list');
        if (!alertsList) return;
        
        alertsList.innerHTML = '';

        const alerts = [
            {
                type: 'warning',
                title: 'Battery BAT004 requires maintenance',
                time: '2 minutes ago'
            },
            {
                type: 'error',
                title: 'Station ST002 low battery inventory',
                time: '5 minutes ago'
            },
            {
                type: 'warning',
                title: 'High temperature detected at BAT004',
                time: '8 minutes ago'
            }
        ];

        alerts.forEach(alert => {
            const alertItem = document.createElement('div');
            alertItem.className = 'alert-item fade-in';
            
            alertItem.innerHTML = `
                <div class="alert-item__icon alert-item__icon--${alert.type}">
                    ${alert.type === 'warning' ? '⚠️' : '🚨'}
                </div>
                <div class="alert-item__content">
                    <div class="alert-item__title">${alert.title}</div>
                    <div class="alert-item__time">${alert.time}</div>
                </div>
            `;
            
            alertsList.appendChild(alertItem);
        });
    }

    loadBatteryHealth() {
        console.log('Loading Battery Health section');
        // Destroy existing charts first
        if (this.charts.health) this.charts.health.destroy();
        if (this.charts.degradation) this.charts.degradation.destroy();
        
        setTimeout(() => {
            this.createHealthChart();
            this.createDegradationChart();
        }, 300);
    }

    createHealthChart() {
        const canvas = document.getElementById('health-chart');
        if (!canvas) {
            console.error('Health chart canvas not found');
            return;
        }

        const ctx = canvas.getContext('2d');
        const batteries = this.mockData.batteries;
        
        this.charts.health = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: batteries.map(b => b.id),
                datasets: [{
                    data: batteries.map(b => b.health),
                    backgroundColor: ['#1FB8CD', '#FFC185', '#B4413C', '#ECEBD5'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            color: getComputedStyle(document.documentElement).getPropertyValue('--color-text').trim()
                        }
                    }
                }
            }
        });
        console.log('Health chart created');
    }

    createDegradationChart() {
        const canvas = document.getElementById('degradation-chart');
        if (!canvas) {
            console.error('Degradation chart canvas not found');
            return;
        }

        const ctx = canvas.getContext('2d');
        
        // Generate mock degradation data
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
        const degradationData = [98, 96, 94, 92, 89, 87];
        
        this.charts.degradation = new Chart(ctx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [{
                    label: 'Average Health',
                    data: degradationData,
                    borderColor: '#1FB8CD',
                    backgroundColor: 'rgba(31, 184, 205, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--color-text').trim()
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 80,
                        max: 100,
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        },
                        ticks: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--color-text-secondary').trim()
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        },
                        ticks: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--color-text-secondary').trim()
                        }
                    }
                }
            }
        });
        console.log('Degradation chart created');
    }

    loadRouteOptimizer() {
        console.log('Loading Route Optimizer section');
        // Destroy existing chart
        if (this.charts.elevation) this.charts.elevation.destroy();
        
        setTimeout(() => {
            this.initRouteMap();
            this.createElevationChart();
            this.setupRouteCalculator();
        }, 300);
    }

    setupRouteCalculator() {
        const calculateRouteBtn = document.getElementById('calculate-route');
        if (calculateRouteBtn) {
            // Remove existing listeners
            const newBtn = calculateRouteBtn.cloneNode(true);
            calculateRouteBtn.parentNode.replaceChild(newBtn, calculateRouteBtn);
            
            // Add new listener
            newBtn.addEventListener('click', () => {
                console.log('Calculate route clicked');
                this.calculateRoute();
            });
        }
    }

    initRouteMap() {
        const mapContainer = document.getElementById('route-map');
        if (!mapContainer) return;
        
        // Mock Google Maps interface since we don't have a real API key
        mapContainer.innerHTML = `
            <div style="text-align: center; padding: 40px; color: var(--color-text-secondary);">
                <div style="font-size: 48px; margin-bottom: 16px;">🗺️</div>
                <div style="font-size: 18px; margin-bottom: 8px;">Interactive Route Map</div>
                <div style="font-size: 14px;">Mumbai → Pune Route Displayed</div>
                <div style="margin-top: 20px; font-size: 12px;">
                    Distance: 148 km | Elevation: +650m | Range: 142 km
                </div>
            </div>
        `;
    }

    createElevationChart() {
        const canvas = document.getElementById('elevation-chart');
        if (!canvas) {
            console.error('Elevation chart canvas not found');
            return;
        }

        const ctx = canvas.getContext('2d');
        
        // Mock elevation data
        const distances = [0, 20, 40, 60, 80, 100, 120, 148];
        const elevations = [14, 45, 120, 245, 380, 420, 350, 180];
        
        this.charts.elevation = new Chart(ctx, {
            type: 'line',
            data: {
                labels: distances,
                datasets: [{
                    label: 'Elevation (m)',
                    data: elevations,
                    borderColor: '#5D878F',
                    backgroundColor: 'rgba(93, 135, 143, 0.2)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--color-text').trim()
                        }
                    }
                },
                scales: {
                    y: {
                        title: {
                            display: true,
                            text: 'Elevation (m)',
                            color: getComputedStyle(document.documentElement).getPropertyValue('--color-text').trim()
                        },
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        },
                        ticks: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--color-text-secondary').trim()
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Distance (km)',
                            color: getComputedStyle(document.documentElement).getPropertyValue('--color-text').trim()
                        },
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        },
                        ticks: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--color-text-secondary').trim()
                        }
                    }
                }
            }
        });
        console.log('Elevation chart created');
    }

    calculateRoute() {
        console.log('calculateRoute method called');
        const fromSelect = document.getElementById('route-from');
        const toSelect = document.getElementById('route-to');
        
        if (!fromSelect || !toSelect) {
            console.error('Route selectors not found');
            return;
        }
        
        const from = fromSelect.value;
        const to = toSelect.value;
        
        console.log(`Calculating route from ${from} to ${to}`);
        
        // Simulate route calculation
        const routeInfo = this.mockData.routes.find(r => r.from === from && r.to === to) || 
                         this.mockData.routes.find(r => r.from === to && r.to === from) ||
                         { distance: 250, elevation_gain: 300, predicted_range: 235, confidence: 88 };
        
        // Update map display
        const mapContainer = document.getElementById('route-map');
        if (mapContainer) {
            mapContainer.innerHTML = `
                <div style="text-align: center; padding: 40px; color: var(--color-text-secondary);">
                    <div style="font-size: 48px; margin-bottom: 16px;">🗺️</div>
                    <div style="font-size: 18px; margin-bottom: 8px; color: var(--color-primary);">Route: ${from} → ${to}</div>
                    <div style="margin-top: 20px; font-size: 12px;">
                        Distance: ${routeInfo.distance} km | Elevation: +${routeInfo.elevation_gain}m<br>
                        Predicted Range: ${routeInfo.predicted_range} km | Confidence: ${routeInfo.confidence}%
                    </div>
                </div>
            `;
            console.log('Route updated in map');
        }
    }

    loadCircularEconomy() {
        console.log('Loading Circular Economy section');
        // Destroy existing chart
        if (this.charts.materials) this.charts.materials.destroy();
        
        setTimeout(() => {
            this.createMaterialsChart();
        }, 300);
    }

    createMaterialsChart() {
        const canvas = document.getElementById('materials-chart');
        if (!canvas) {
            console.error('Materials chart canvas not found');
            return;
        }

        const ctx = canvas.getContext('2d');
        const materials = this.mockData.materials;
        
        this.charts.materials = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Lithium', 'Cobalt', 'Nickel'],
                datasets: [
                    {
                        label: 'Recovered (%)',
                        data: [materials.lithium.recovered, materials.cobalt.recovered, materials.nickel.recovered],
                        backgroundColor: '#1FB8CD',
                        borderRadius: 8
                    },
                    {
                        label: 'Target (%)',
                        data: [materials.lithium.target, materials.cobalt.target, materials.nickel.target],
                        backgroundColor: '#FFC185',
                        borderRadius: 8
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--color-text').trim()
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        },
                        ticks: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--color-text-secondary').trim()
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        },
                        ticks: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--color-text-secondary').trim()
                        }
                    }
                }
            }
        });
        console.log('Materials chart created');
    }

    loadStationPlacement() {
        console.log('Loading Station Placement section');
        // Destroy existing chart
        if (this.charts.demand) this.charts.demand.destroy();
        
        setTimeout(() => {
            this.initPlacementMap();
            this.createDemandChart();
        }, 300);
    }

    initPlacementMap() {
        const mapContainer = document.getElementById('placement-map');
        if (!mapContainer) return;
        
        mapContainer.innerHTML = `
            <div style="text-align: center; padding: 40px; color: var(--color-text-secondary);">
                <div style="font-size: 48px; margin-bottom: 16px;">📍</div>
                <div style="font-size: 18px; margin-bottom: 8px;">Station Coverage Map</div>
                <div style="font-size: 14px;">Optimal Placement Analysis</div>
                <div style="margin-top: 20px; font-size: 12px;">
                    Current Stations: 3 | Recommended: 2 new locations
                </div>
            </div>
        `;
    }

    createDemandChart() {
        const canvas = document.getElementById('demand-chart');
        if (!canvas) {
            console.error('Demand chart canvas not found');
            return;
        }

        const ctx = canvas.getContext('2d');
        
        this.charts.demand = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Mumbai', 'Pune', 'Bangalore', 'Chennai', 'Delhi', 'Kolkata'],
                datasets: [{
                    label: 'Demand Score',
                    data: [95, 85, 92, 78, 88, 72],
                    borderColor: '#1FB8CD',
                    backgroundColor: 'rgba(31, 184, 205, 0.2)',
                    pointBackgroundColor: '#1FB8CD'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--color-text').trim()
                        }
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        },
                        ticks: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--color-text-secondary').trim()
                        }
                    }
                }
            }
        });
        console.log('Demand chart created');
    }

    loadAnalytics() {
        console.log('Loading Analytics section');
        // Destroy existing charts
        if (this.charts.ml) this.charts.ml.destroy();
        if (this.charts.accuracy) this.charts.accuracy.destroy();
        
        setTimeout(() => {
            this.createMLChart();
            this.createAccuracyChart();
        }, 300);
    }

    createMLChart() {
        const canvas = document.getElementById('ml-chart');
        if (!canvas) {
            console.error('ML chart canvas not found');
            return;
        }

        const ctx = canvas.getContext('2d');
        
        const weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
        const accuracyData = [89, 92, 94, 96];
        
        this.charts.ml = new Chart(ctx, {
            type: 'line',
            data: {
                labels: weeks,
                datasets: [{
                    label: 'Model Accuracy (%)',
                    data: accuracyData,
                    borderColor: '#B4413C',
                    backgroundColor: 'rgba(180, 65, 60, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--color-text').trim()
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 80,
                        max: 100,
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        },
                        ticks: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--color-text-secondary').trim()
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        },
                        ticks: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--color-text-secondary').trim()
                        }
                    }
                }
            }
        });
        console.log('ML chart created');
    }

    createAccuracyChart() {
        const canvas = document.getElementById('accuracy-chart');
        if (!canvas) {
            console.error('Accuracy chart canvas not found');
            return;
        }

        const ctx = canvas.getContext('2d');
        
        this.charts.accuracy = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Health Prediction', 'Range Estimation', 'Degradation', 'Maintenance'],
                datasets: [{
                    label: 'Accuracy (%)',
                    data: [94, 89, 92, 87],
                    backgroundColor: ['#1FB8CD', '#FFC185', '#B4413C', '#5D878F'],
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        },
                        ticks: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--color-text-secondary').trim()
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        },
                        ticks: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--color-text-secondary').trim()
                        }
                    }
                }
            }
        });
        console.log('Accuracy chart created');
    }

    startRealTimeUpdates() {
        // Simulate real-time updates every 30 seconds
        setInterval(() => {
            this.updateRealTimeData();
        }, 30000);
    }

    updateRealTimeData() {
        // Simulate small changes in battery data
        this.mockData.batteries.forEach(battery => {
            // Small random variations
            battery.soc += Math.random() * 4 - 2; // ±2%
            battery.soc = Math.max(0, Math.min(100, battery.soc));
            
            battery.temp += Math.random() * 2 - 1; // ±1°C
            battery.temp = Math.max(20, Math.min(40, battery.temp));
        });

        // Update dashboard if currently active
        if (this.currentSection === 'dashboard') {
            this.updateKPIs();
            this.loadBatteryGrid();
        }
    }

    hideLoading() {
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.classList.add('hidden');
            
            setTimeout(() => {
                loadingOverlay.style.display = 'none';
            }, 300);
        }
    }

    // Mock API methods
    async mockApiCall(endpoint, delay = 500) {
        return new Promise(resolve => {
            setTimeout(() => {
                resolve({ success: true, data: this.mockData });
            }, delay);
        });
    }
}

// Service Worker Registration for PWA
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing SmartSwapML Dashboard');
    window.smartSwapApp = new SmartSwapMLDashboard();
});

// Handle theme changes
const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");
prefersDarkScheme.addListener((e) => {
    // Update charts when theme changes
    if (window.smartSwapApp && window.smartSwapApp.charts) {
        Object.values(window.smartSwapApp.charts).forEach(chart => {
            if (chart && chart.update) {
                chart.update();
            }
        });
    }
});

// Handle window resize for responsive charts
window.addEventListener('resize', () => {
    if (window.smartSwapApp && window.smartSwapApp.charts) {
        Object.values(window.smartSwapApp.charts).forEach(chart => {
            if (chart && chart.resize) {
                chart.resize();
            }
        });
    }
});

// Export for external access
window.SmartSwapMLDashboard = SmartSwapMLDashboard;