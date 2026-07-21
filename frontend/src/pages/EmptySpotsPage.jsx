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

  function SpotGrid({ total, free }) 
  {
  return (
    <div className="spot-grid">
      {Array.from({ length: total }).map((_, i) => (
        <div
          key={i} className={`spot-square ${i < free ? "spot-square--free":"spot-square--occupied"}`}
        />))}
    </div>);
  }

  // The "on_show" equivalent — re-fetch every time this page becomes active.
  useEffect(refresh, [data.wing]);

  const noneFree = counts && counts.total_spots_two_wheeler === 0 && counts.free_spots_two_wheeler === 0  
                    && counts.total_spots_four_wheeler === 0 && counts.free_spots_four_wheeler === 0;

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
            <div className="availability-card__label">Two-Wheeler</div>
              <SpotGrid total={counts.total_spots_two_wheeler} free={counts.free_spots_two_wheeler}/>
              <div> {counts.free_spots_two_wheeler}/{counts.total_spots_two_wheeler} Available </div>
          </div>
          <div className="availability-card">
            <div className="availability-card__label">Four-Wheeler</div>
                <SpotGrid total={counts.total_spots_four_wheeler} free={counts.free_spots_four_wheeler}/>
                <div> {counts.free_spots_four_wheeler}/{counts.total_spots_four_wheeler} Available </div>
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
