import { useState, useEffect } from "react";
import { Api } from "../api/client.js";
import PlateChip from "../components/PlateChip.jsx";

export default function BillingPage({ data, goTo }) 
{
  const [bill, setBill] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => 
  {
    setLoading(true);
    Api.getLatestBill(data.licensePlate)
      .then(setBill)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [data.licensePlate]);

  return (
    <div className="panel">
      <h1 className="panel__title">Billing</h1>
      <PlateChip value={data.licensePlate} />

      {error && <div className="error-banner">{error}</div>}

      {loading ? (
        <p>Fetching bill…</p>
      ) : !bill ? (
        <div className="error-banner">No completed session found for this plate.</div>
      ) : (
        <div>
          <div className="bill-row">
            <span className="bill-row__label">Owner Name</span>
            <span>{bill.owner_name || "—"}</span>
          </div>
          <div className="bill-row">
            <span className="bill-row__label">Entry Time</span>
            <span>{bill.entry_time}</span>
          </div>
          <div className="bill-row">
            <span className="bill-row__label">Exit Time</span>
            <span>{bill.exit_time}</span>
          </div>
          <div className="bill-row">
            <span className="bill-row__label">Duration</span>
            <span>{bill.duration}</span>
          </div>
          <div className="bill-total">₹{bill.amount}</div>
        </div>
      )}

      <div className="btn-row">
        <button className="btn btn--primary" onClick={() => window.print()}>
          Print Bill
        </button>
        <button className="btn btn--ghost" onClick={() => goTo("spots")}>
          Return Home
        </button>
      </div>
    </div>
  );
}
