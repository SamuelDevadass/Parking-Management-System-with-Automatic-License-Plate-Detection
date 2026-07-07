import { useState, useEffect } from "react";
import { Api } from "../api/client.js";

export default function SelectWingPage({ data, updateData, goTo }) {
  const [wings, setWings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Runs once when the page mounts — the React equivalent of your
  // get_wings_list() call that ran during __init__.
  useEffect(() => {
    Api.getWings()
      .then(setWings)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  async function handleWingChange(e) {
    const wing = e.target.value;
    updateData({ wing, centre_id: null });
    try {
      const { centre_id } = await Api.getCentreForWing(wing);
      updateData({ centre_id });
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="panel">
      <h1 className="panel__title">Select Your Wing</h1>
      <p className="panel__hint">Choose the wing you're stationed at to continue.</p>

      {error && <div className="error-banner">{error}</div>}

      {loading ? (
        <p>Loading wings…</p>
      ) : wings.length === 0 ? (
        <div className="error-banner">No wings found. Check the backend connection.</div>
      ) : (
        <div className="field">
          <label htmlFor="wing-select">Wing</label>
          <select id="wing-select" value={data.wing} onChange={handleWingChange}>
            <option value="" disabled>
              Choose a wing…
            </option>
            {wings.map((w) => (
              <option key={w} value={w}>
                {w}
              </option>
            ))}
          </select>
        </div>
      )}

      <div className="btn-row">
        <button
          className="btn btn--primary"
          disabled={!data.wing}
          onClick={() => goTo("spots")}
        >
          Continue
        </button>
      </div>
    </div>
  );
}
