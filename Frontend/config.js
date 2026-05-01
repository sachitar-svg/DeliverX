/**
 * DeliverX Configuration
 * Central config for all UI components
 */

const config = {
  // =========================
  // 🔹 Backend API settings
  // =========================
  API: {
    BASE_URL: 'http://127.0.0.1:5000',   // ✅ Correct Flask URL
    TIMEOUT: 10000,
    HEADERS: {
      'Content-Type': 'application/json',
    },
  },

  // =========================
  // 🔹 UI Settings
  // =========================
  UI: {
    DEFAULT_HUB_ID: 1,
    REFRESH_INTERVAL: 5000,   // Auto refresh every 5 sec
    ALERT_TIMEOUT: 5000,
    OTP_EXPIRY_MINUTES: 5     // OTP validity
  },

  // =========================
  // 🔹 Quick Headers Shortcut
  // =========================
  HEADERS: {
    'Content-Type': 'application/json'
  },

  // =========================
  // 🔹 Roles
  // =========================
  ROLES: {
    CUSTOMER: {
      id: 'customer',
      label: 'Customer',
      icon: '👤',
      description: 'Place and track orders',
      color: '#3b82f6',
    },
    AGENT: {
      id: 'agent',
      label: 'Delivery Agent',
      icon: '🚚',
      description: 'Manage deliveries',
      color: '#10b981',
    },
    HUB: {
      id: 'hub',
      label: 'Hub Manager',
      icon: '📦',
      description: 'Manage local hub',
      color: '#f59e0b',
    },
    ADMIN: {
      id: 'admin',
      label: 'Admin',
      icon: '⚙️',
      description: 'System administration',
      color: '#ef4444',
    },
  },

  // =========================
  // 🔹 Order Status
  // =========================
  ORDER_STATUS: {
    PLACED: 'placed',
    DISPATCHED: 'dispatched',
    AT_HUB: 'at_hub',
    OUT_FOR_DELIVERY: 'out_for_delivery',
    DELIVERED: 'delivered',
    FAILED: 'failed'
  },

  // =========================
  // 🔹 Delivery Mode
  // =========================
  DELIVERY_MODE: {
    DIRECT: 'direct',
    MICRO_HUB: 'micro-hub'
  },

  // =========================
  // 🔹 Demo Credentials
  // =========================
  DEMO_CREDENTIALS: {
    customer: {
      email: 'customer@deliverx.local',
      password: 'customer123',
    },
    agent: {
      email: 'agent@deliverx.local',
      password: 'agent123',
    },
    hub: {
      email: 'hub@deliverx.local',
      password: 'hub123',
    },
    admin: {
      email: 'admin@deliverx.local',
      password: 'admin123',
    },
  },

  // =========================
  // 🔹 OTP Settings
  // =========================
  OTP: {
    LENGTH: 6,
    VALIDITY_MINUTES: 5,
    SMS_PROVIDER: 'mock', // 'twilio' in real system
  },

  // =========================
  // 🔹 Routing
  // =========================
  ROUTING: {
    ALGORITHM: 'tsp',
    OPTIMIZATION_ENABLED: true,
    MAP_PROVIDER: 'google',
    UPDATE_FREQUENCY: 5000,
  },

  // =========================
  // 🔹 Hub Configuration
  // =========================
  HUBS: {
    1: {
      id: '1',
      name: 'Ravi Kirana Store',
      lat: 12.9716,
      lng: 77.5946,
      open_time: '08:00',
      close_time: '20:00',
      capacity: 1000,
    },
    2: {
      id: '2',
      name: 'Anita General Store',
      lat: 12.9761,
      lng: 77.6033,
      open_time: '09:00',
      close_time: '21:00',
      capacity: 800,
    },
  },

  // =========================
  // 🔹 Delivery Modes (Costing)
  // =========================
  MODES: {
    SAME_DAY: {
      id: 'same_day',
      label: 'Same Day',
      max_distance: 15,
      base_cost: 40,
    },
    NEXT_DAY: {
      id: 'next_day',
      label: 'Next Day',
      max_distance: 30,
      base_cost: 25,
    },
    STANDARD: {
      id: 'standard',
      label: 'Standard (3-5 days)',
      max_distance: 100,
      base_cost: 15,
    },
  },

  // =========================
  // 🔹 Geolocation
  // =========================
  GEO: {
    DEFAULT_LAT: 12.9716,
    DEFAULT_LNG: 77.5946,
    DEFAULT_ZOOM: 13,
    CITY: 'Bangalore',
    COUNTRY: 'India',
  },
};


// =========================
// 🔹 Session Management
// =========================
const session = {
  role: localStorage.getItem('deliverx_role') || null,
  userId: localStorage.getItem('deliverx_user_id') || null,
  token: localStorage.getItem('deliverx_token') || null,
  hubId: localStorage.getItem('deliverx_hub_id') || null,

  setRole(role, userId, token, hubId = null) {
    this.role = role;
    this.userId = userId;
    this.token = token;
    this.hubId = hubId;

    localStorage.setItem('deliverx_role', role);
    localStorage.setItem('deliverx_user_id', userId);
    localStorage.setItem('deliverx_token', token);
    if (hubId) localStorage.setItem('deliverx_hub_id', hubId);
  },

  clear() {
    this.role = null;
    this.userId = null;
    this.token = null;
    this.hubId = null;

    localStorage.removeItem('deliverx_role');
    localStorage.removeItem('deliverx_user_id');
    localStorage.removeItem('deliverx_token');
    localStorage.removeItem('deliverx_hub_id');
  },

  isAuthenticated() {
    return !!this.token && !!this.role;
  },
};


// =========================
// 🔹 Export (IMPORTANT)
// =========================
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { config, session };
}