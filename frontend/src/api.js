const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

function buildUrl(path, params = {}) {
  const url = new URL(`${API_BASE_URL}${path}`);

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, value);
    }
  });

  return url.toString();
}

async function request(path, options = {}) {
  const { token, params, ...init } = options;

  const response = await fetch(buildUrl(path, params), {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init.headers,
    },
  });

  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message =
      data.detail ||
      data.error ||
      Object.values(data).flat().join(" ") ||
      "Request failed";
    throw new Error(message);
  }

  return data;
}

function getResults(data) {
  return Array.isArray(data) ? data : data.results || [];
}

export async function login(email, password) {
  return request("/token/", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function fetchAirports() {
  const data = await request("/airport/airports/");
  return getResults(data);
}

export async function fetchFlights(params) {
  const data = await request("/flight/flights/", { params });
  return {
    results: getResults(data),
    count: data.count ?? getResults(data).length,
  };
}

export function fetchFlight(id) {
  return request(`/flight/flights/${id}/`);
}

export function fetchAvailableSeats(id) {
  return request(`/flight/flights/${id}/available-seats/`);
}

export function createOrder(token, flightId, seat) {
  return request("/order/orders/", {
    method: "POST",
    token,
    body: JSON.stringify({
      tickets: [{ flight: flightId, row: seat.row, seat: seat.seat }],
    }),
  });
}

export async function fetchOrders(token) {
  const data = await request("/order/orders/", { token });
  return getResults(data);
}

export function cancelOrder(token, orderId) {
  return request(`/order/orders/${orderId}/cancel/`, {
    method: "POST",
    token,
  });
}
