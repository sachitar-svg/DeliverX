/**
 * DeliverX API Helper
 * Compatible with config.js session object and Flask backend.
 */
class DeliverXAPI {
  constructor() {
    this.baseURL = config.API.BASE_URL;
    this.headers = config.HEADERS;
  }


  async request(method, endpoint, body = null) {
    try {
      const options = {
        method,
        headers: {
          ...this.headers,
          ...(typeof session !== 'undefined' && session.token
              ? { Authorization: `Bearer ${session.token}` }
              : {})
        }
      };
      if (body) options.body = JSON.stringify(body);
      const response = await fetch(`${this.baseURL}${endpoint}`, options);
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || data.message || `HTTP ${response.status}`);
      return data;
    } catch (err) {
      console.error(`API [${method} ${endpoint}]:`, err.message);
      throw err;
    }
  }

  // Auth (mock — no real auth backend)
  async login(email, password, role) {
    return { user_id: 'USR-' + Date.now(), token: 'demo-token', role };
  }

  // Orders
  async placeOrder(data)           {return this.request('POST', '/place-order', data); }
  async getOrderStatus(id)         { return this.request('GET',   `/order-status/${id}`); }
  async updateOrderStatus(id, s)   { return this.request('PATCH', `/order-status/${id}`, { status: s }); }
  async getAllOrders(filter = null) { return this.request('GET', filter ? `/all-orders?status=${filter}` : '/all-orders'); }
  async bundleOrders(orders)       { return this.request('POST',  '/bundle-orders', { orders }); }

  // Geocoding & routing
  async geocodeAddress(address)    { return this.request('POST', '/geocode', { address }); }
  async getRoute(start, end)       { return this.request('POST', '/route', { start, end }); }

  // Slots
  async getAvailableSlots()        { return this.request('GET',  '/available-slots'); }
  async selectSlot(id, slot)       { return this.request('POST', '/select-slot', { order_id: id, slot }); }
  async getSlot(id)                { return this.request('GET',  `/get-slot/${id}`); }
// Add this inside the DeliverXAPI class in api.js
  async bundleOrders(orders) {
    return this.request('POST', '/bundle-orders', { orders });
  }
  async getAgentStats() {
    return this.request('GET', '/agent-stats');
  }

  // OTP & notifications
  // Inside DeliverXAPI class...

async generateOTP(id, role) { 
    // This MUST match the route @otp_bp.route("/generate-otp")
    return this.request('POST', '/generate-otp', { order_id: id, role: role }); 
}

async verifyOTP(id, role, otp) { 
    // This MUST match the route @otp_bp.route("/verify-otp")
    return this.request('POST', '/verify-otp', { order_id: id, role: role, otp: otp }); 
}

  async notifyCustomer(id, phone, agent) {
    return this.request('POST', '/notify-customer', { order_id: id, phone, agent_name: agent });
  }

  // Delivery proof — photo param actually sent now
  async confirmDelivery(orderId, role, otp, lat, lng, photo = null) {
    const body = { order_id: orderId, role, otp, lat, lng };
    if (photo) body.photo = photo;
    return this.request('POST', '/confirm-delivery', body);
  }
  async getDeliveryProof(id)       { return this.request('GET', `/delivery-proof/${id}`); }

  // Hub
  // Inside DeliverXAPI class...

async generateHubAgentOTP(id) { 
    return this.request('POST', '/hub/generate-agent-otp', { order_id: id }); 
}

async verifyHubAgentOTP(id, otp) { 
    return this.request('POST', '/hub/verify-agent-otp', { order_id: id, otp: otp }); 
}

async generateHubCustomerOTP(id, phone) { 
    return this.request('POST', '/hub/generate-customer-otp', { order_id: id, customer_phone: phone }); 
}

async verifyHubCustomerOTP(id, otp, hubId) { 
    return this.request('POST', '/hub/verify-customer-otp', { order_id: id, otp: otp, hub_id: hubId }); 
}

  async getHubParcelStatus(id)     { return this.request('GET', `/hub/parcel-status/${id}`); }
  async getHubHours(hubId)         { return this.request('GET', `/hub/hours/${hubId}`); }

  // System
 async healthCheck() { 
    return this.request('GET', '/health'); 
}
}

const api = new DeliverXAPI();
if (typeof window !== 'undefined') window.api = api;
if (typeof module !== 'undefined' && module.exports) module.exports = api;