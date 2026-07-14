import { useState, useEffect } from "react";
import { Api } from "../api/client.js";

export default function EmptySpotsPage({ data, goTo }) 
{
  const [counts, setCounts] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  function refresh() 
  {
    setLoading(true);
    Api.getSpotAvailability(data.wing)
      .then(setCounts)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }

  // The "on_show" equivalent — re-fetch every time this page becomes active.
  useEffect(refresh, [data.wing]);

  const noneFree = counts && counts.two_wheeler === 0 && counts.four_wheeler === 0;

  return (
    <div className="panel">
      <h1 className="panel__title">{data.wing}</h1>
      <p className="panel__hint">Available spots</p>

      {error && <div className="error-banner">{error}</div>}

      {loading ? 
      (
        <p>Checking availability…</p>
      ) : noneFree ? (
        <div className="error-banner">No free spots available in this wing.</div>
      ) : 
      (
        <div className="availability-grid">
          <div className="availability-card">
            <div
              className=
              {`availability-card__count ${
                counts.two_wheeler === 0 ? "availability-card__count--zero" : ""
              }`}
            >
              {counts.two_wheeler}
            </div>
            <div className="availability-card__label">Two-Wheeler Spots Free</div>
          </div>
          <div className="availability-card">
            <div
              className=
              {`availability-card__count ${
                counts.four_wheeler === 0 ? "availability-card__count--zero" : ""
              }`}
            >
              {counts.four_wheeler}
            </div>
            <div className="availability-card__label">Four-Wheeler Spots Free</div>
          </div>
        </div>
      )}

      <div className="btn-row btn--spaced">
        <button className="btn btn--primary" onClick={() => goTo("detect")}>
          Continue
        </button>
        <button className="btn" onClick={() => goTo("wing")}>
          Select Wing
        </button>
      </div>
    </div>
  );
}
