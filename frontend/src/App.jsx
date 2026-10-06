import { useEffect, useMemo, useState } from "react";

import {
  cancelOrder,
  createOrder,
  fetchAirports,
  fetchAvailableSeats,
  fetchFlight,
  fetchFlights,
  fetchOrders,
  login,
} from "./api.js";

const initialFilters = {
  route__source: "",
  route__destination: "",
  departure_date_from: "",
  departure_date_to: "",
  has_available_seats: "",
};

function formatDateTime(value) {
  if (!value) {
    return "Not set";
  }

  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function formatMoney(value) {
  if (value === undefined || value === null) {
    return "-";
  }

  return new Intl.NumberFormat("en", {
    style: "currency",
    currency: "EUR",
  }).format(Number(value));
}

function getAirportLabel(airport) {
  if (!airport) {
    return "Unknown airport";
  }

  const city = airport.city?.name;
  return city ? `${airport.name}, ${city}` : airport.name;
}

function getRouteLabel(route) {
  if (!route) {
    return "Route not set";
  }

  return `${getAirportLabel(route.source)} -> ${getAirportLabel(route.destination)}`;
}

function App() {
  const [filters, setFilters] = useState(initialFilters);
  const [airports, setAirports] = useState([]);
  const [flights, setFlights] = useState([]);
  const [flightCount, setFlightCount] = useState(0);
  const [selectedFlightId, setSelectedFlightId] = useState(null);
  const [selectedFlight, setSelectedFlight] = useState(null);
  const [availableSeats, setAvailableSeats] = useState([]);
  const [selectedSeat, setSelectedSeat] = useState(null);
  const [orders, setOrders] = useState([]);
  const [token, setToken] = useState(() => localStorage.getItem("airportToken"));
  const [userEmail, setUserEmail] = useState(() => localStorage.getItem("airportEmail"));
  const [credentials, setCredentials] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [ordersLoading, setOrdersLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const selectedAvailableSeats = useMemo(() => {
    return new Set(availableSeats.map((seat) => `${seat.row}-${seat.seat}`));
  }, [availableSeats]);

  const loadFlights = async (nextFilters = filters) => {
    setLoading(true);
    setError("");

    try {
      const data = await fetchFlights(nextFilters);
      setFlights(data.results);
      setFlightCount(data.count);

      if (data.results.length && !selectedFlightId) {
        setSelectedFlightId(data.results[0].id);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadOrders = async (currentToken = token) => {
    if (!currentToken) {
      setOrders([]);
      return;
    }

    setOrdersLoading(true);

    try {
      const data = await fetchOrders(currentToken);
      setOrders(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setOrdersLoading(false);
    }
  };

  useEffect(() => {
    async function loadInitialData() {
      setLoading(true);

      try {
        const [airportList, flightData] = await Promise.all([
          fetchAirports(),
          fetchFlights(initialFilters),
        ]);
        setAirports(airportList);
        setFlights(flightData.results);
        setFlightCount(flightData.count);

        if (flightData.results.length) {
          setSelectedFlightId(flightData.results[0].id);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadInitialData();
  }, []);

  useEffect(() => {
    if (!selectedFlightId) {
      setSelectedFlight(null);
      setAvailableSeats([]);
      return;
    }

    async function loadFlightDetails() {
      setDetailLoading(true);
      setSelectedSeat(null);
      setError("");

      try {
        const [flight, seats] = await Promise.all([
          fetchFlight(selectedFlightId),
          fetchAvailableSeats(selectedFlightId),
        ]);
        setSelectedFlight(flight);
        setAvailableSeats(seats);
      } catch (err) {
        setError(err.message);
      } finally {
        setDetailLoading(false);
      }
    }

    loadFlightDetails();
  }, [selectedFlightId]);

  useEffect(() => {
    loadOrders(token);
  }, [token]);

  const handleFilterChange = (event) => {
    setFilters((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  };

  const handleSearch = (event) => {
    event.preventDefault();
    setSelectedFlightId(null);
    setSelectedFlight(null);
    loadFlights(filters);
  };

  const handleReset = () => {
    setFilters(initialFilters);
    setSelectedFlightId(null);
    setSelectedFlight(null);
    loadFlights(initialFilters);
  };

  const handleLogin = async (event) => {
    event.preventDefault();
    setError("");
    setMessage("");

    try {
      const data = await login(credentials.email, credentials.password);
      localStorage.setItem("airportToken", data.access);
      localStorage.setItem("airportEmail", credentials.email);
      setToken(data.access);
      setUserEmail(credentials.email);
      setCredentials({ email: "", password: "" });
      setMessage("Signed in.");
    } catch (err) {
      setError(err.message);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("airportToken");
    localStorage.removeItem("airportEmail");
    setToken(null);
    setUserEmail(null);
    setOrders([]);
    setMessage("Signed out.");
  };

  const handleBook = async () => {
    if (!token) {
      setError("Sign in before booking a seat.");
      return;
    }

    if (!selectedSeat || !selectedFlight) {
      setError("Choose an available seat first.");
      return;
    }

    setError("");
    setMessage("");

    try {
      await createOrder(token, selectedFlight.id, selectedSeat);
      setMessage(`Seat ${selectedSeat.row}-${selectedSeat.seat} booked.`);
      setSelectedSeat(null);
      const [seats] = await Promise.all([
        fetchAvailableSeats(selectedFlight.id),
        loadOrders(token),
        loadFlights(filters),
      ]);
      setAvailableSeats(seats);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleCancelOrder = async (orderId) => {
    if (!token) {
      return;
    }

    setError("");
    setMessage("");

    try {
      await cancelOrder(token, orderId);
      setMessage(`Order #${orderId} cancelled.`);
      await Promise.all([
        loadOrders(token),
        selectedFlightId ? fetchAvailableSeats(selectedFlightId).then(setAvailableSeats) : null,
        loadFlights(filters),
      ]);
    } catch (err) {
      setError(err.message);
    }
  };

  const seatRows = [];
  if (selectedFlight?.airplane) {
    for (let row = 1; row <= selectedFlight.airplane.rows; row += 1) {
      const seats = [];
      for (let seat = 1; seat <= selectedFlight.airplane.seats_in_row; seat += 1) {
        seats.push({ row, seat });
      }
      seatRows.push(seats);
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Airport API</p>
          <h1>Flight booking demo</h1>
        </div>

        <div className="auth-panel">
          {token ? (
            <div className="signed-in">
              <span>{userEmail}</span>
              <button className="ghost-button" type="button" onClick={handleLogout}>
                Sign out
              </button>
            </div>
          ) : (
            <form className="login-form" onSubmit={handleLogin}>
              <input
                aria-label="Email"
                placeholder="email"
                type="email"
                value={credentials.email}
                onChange={(event) =>
                  setCredentials((current) => ({
                    ...current,
                    email: event.target.value,
                  }))
                }
              />
              <input
                aria-label="Password"
                placeholder="password"
                type="password"
                value={credentials.password}
                onChange={(event) =>
                  setCredentials((current) => ({
                    ...current,
                    password: event.target.value,
                  }))
                }
              />
              <button type="submit">Sign in</button>
            </form>
          )}
        </div>
      </header>

      {(error || message) && (
        <div className={`notice ${error ? "notice-error" : "notice-success"}`}>
          {error || message}
        </div>
      )}

      <main className="workspace">
        <section className="panel search-panel">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Search</p>
              <h2>Flights</h2>
            </div>
            <span>{flightCount} found</span>
          </div>

          <form className="filters" onSubmit={handleSearch}>
            <label>
              From
              <select
                name="route__source"
                value={filters.route__source}
                onChange={handleFilterChange}
              >
                <option value="">Any airport</option>
                {airports.map((airport) => (
                  <option key={airport.id} value={airport.id}>
                    {getAirportLabel(airport)}
                  </option>
                ))}
              </select>
            </label>

            <label>
              To
              <select
                name="route__destination"
                value={filters.route__destination}
                onChange={handleFilterChange}
              >
                <option value="">Any airport</option>
                {airports.map((airport) => (
                  <option key={airport.id} value={airport.id}>
                    {getAirportLabel(airport)}
                  </option>
                ))}
              </select>
            </label>

            <label>
              From date
              <input
                name="departure_date_from"
                type="date"
                value={filters.departure_date_from}
                onChange={handleFilterChange}
              />
            </label>

            <label>
              To date
              <input
                name="departure_date_to"
                type="date"
                value={filters.departure_date_to}
                onChange={handleFilterChange}
              />
            </label>

            <label>
              Availability
              <select
                name="has_available_seats"
                value={filters.has_available_seats}
                onChange={handleFilterChange}
              >
                <option value="">All flights</option>
                <option value="true">With seats</option>
              </select>
            </label>

            <div className="filter-actions">
              <button type="submit">Search</button>
              <button className="ghost-button" type="button" onClick={handleReset}>
                Reset
              </button>
            </div>
          </form>

          <div className="flight-list" aria-busy={loading}>
            {loading && <div className="empty-state">Loading flights...</div>}

            {!loading && flights.length === 0 && (
              <div className="empty-state">No flights found.</div>
            )}

            {!loading &&
              flights.map((flight) => (
                <button
                  className={`flight-item ${
                    selectedFlightId === flight.id ? "flight-item-active" : ""
                  }`}
                  key={flight.id}
                  type="button"
                  onClick={() => setSelectedFlightId(flight.id)}
                >
                  <div>
                    <strong>{getRouteLabel(flight.route)}</strong>
                    <span>{flight.airplane?.name || "Aircraft not set"}</span>
                  </div>
                  <div className="flight-meta">
                    <span>{formatDateTime(flight.departure_time)}</span>
                    <span>{flight.available_seats} seats</span>
                    <span>{formatMoney(flight.base_price)}</span>
                  </div>
                </button>
              ))}
          </div>
        </section>

        <section className="panel detail-panel">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Booking</p>
              <h2>Flight details</h2>
            </div>
            {selectedFlight?.status && (
              <span className="status-pill">{selectedFlight.status}</span>
            )}
          </div>

          {detailLoading && <div className="empty-state">Loading flight...</div>}

          {!detailLoading && !selectedFlight && (
            <div className="empty-state">Select a flight.</div>
          )}

          {!detailLoading && selectedFlight && (
            <>
              <div className="flight-summary">
                <div>
                  <span>Route</span>
                  <strong>{getRouteLabel(selectedFlight.route)}</strong>
                </div>
                <div>
                  <span>Departure</span>
                  <strong>{formatDateTime(selectedFlight.departure_time)}</strong>
                </div>
                <div>
                  <span>Arrival</span>
                  <strong>{formatDateTime(selectedFlight.arrival_time)}</strong>
                </div>
                <div>
                  <span>Aircraft</span>
                  <strong>
                    {selectedFlight.airplane?.name} /{" "}
                    {selectedFlight.airplane?.airplane_type?.name}
                  </strong>
                </div>
              </div>

              <div className="seat-toolbar">
                <div>
                  <p className="eyebrow">Seat map</p>
                  <strong>{availableSeats.length} available</strong>
                </div>
                <button
                  type="button"
                  disabled={!selectedSeat}
                  onClick={handleBook}
                >
                  {selectedSeat
                    ? `Book ${selectedSeat.row}-${selectedSeat.seat}`
                    : "Choose seat"}
                </button>
              </div>

              <div className="seat-map">
                {seatRows.map((row) => (
                  <div
                    className="seat-row"
                    key={row[0].row}
                    style={{ "--seat-count": row.length }}
                  >
                    <span className="row-label">{row[0].row}</span>
                    {row.map((seat) => {
                      const key = `${seat.row}-${seat.seat}`;
                      const isAvailable = selectedAvailableSeats.has(key);
                      const isSelected =
                        selectedSeat?.row === seat.row &&
                        selectedSeat?.seat === seat.seat;

                      return (
                        <button
                          className={`seat ${isSelected ? "seat-selected" : ""}`}
                          disabled={!isAvailable}
                          key={key}
                          type="button"
                          onClick={() => setSelectedSeat(seat)}
                        >
                          {seat.seat}
                        </button>
                      );
                    })}
                  </div>
                ))}
              </div>
            </>
          )}
        </section>
      </main>

      <section className="panel orders-panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Account</p>
            <h2>My orders</h2>
          </div>
          {ordersLoading && <span>Loading...</span>}
        </div>

        {!token && <div className="empty-state">Sign in to see booked tickets.</div>}

        {token && !ordersLoading && orders.length === 0 && (
          <div className="empty-state">No orders yet.</div>
        )}

        {token && orders.length > 0 && (
          <div className="orders-grid">
            {orders.map((order) => (
              <article className="order-item" key={order.id}>
                <div className="order-header">
                  <div>
                    <span>Order #{order.id}</span>
                    <strong>{formatDateTime(order.created_at)}</strong>
                  </div>
                  <button
                    className="ghost-button"
                    type="button"
                    onClick={() => handleCancelOrder(order.id)}
                  >
                    Cancel
                  </button>
                </div>

                <div className="tickets">
                  {order.tickets.map((ticket) => (
                    <div className="ticket" key={ticket.id}>
                      <span>{getRouteLabel(ticket.flight?.route)}</span>
                      <strong>
                        Seat {ticket.row}-{ticket.seat} / {formatMoney(ticket.price)}
                      </strong>
                    </div>
                  ))}
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default App;
