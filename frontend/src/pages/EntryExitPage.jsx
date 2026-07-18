import { useState, useEffect } from "react";
import { Api } from "../api/client.js";
import PlateChip from "../components/PlateChip.jsx";

export default function EntryExitPage({ data, updateData, goTo }) 
{
  const [spots, setSpots] = useState([]);
  const [selectedKey, setSelectedKey] = useState("");
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);

  function loadSpots() 
  {
    if (!data.size) return;
    Api.getAvailableSpots(data.wing, data.centre_id, data.size)
      .then(setSpots)
      .catch((err) => setError(err.message));
  }

  // on_show() equivalent: reset the selected spot and reload the list.
  useEffect(() => { setSelectedKey("");
                    updateData({ floor: null, spotNumber: null });
                    loadSpots();
  }, [data.size]);

  function handleSelect(e) 
  {
    const key = e.target.value;
    setSelectedKey(key);
    const spot = spots.find((s) => `${s.floor}-${s.spot_number}` === key);
    if (spot) updateData({ floor: spot.floor, spotNumber: spot.spot_number });
  }

  async function markEntry() 
  {
    setError(null);
    try 
    {
      await Api.markEntry({ license_plate: data.licensePlate, centre_id: data.centre_id,
                            wing: data.wing, floor: data.floor,
                            spot_number: data.spotNumber, folder_path: data.folderPath,});
      setMessage("Entry recorded.");
      loadSpots();
    } 
    catch (err) 
    {
      setError(err.message);
    }
  }

  async function markExit() 
  {
    setError(null);
    try 
    {
      await Api.markExit(data.licensePlate);
      setMessage("Exit recorded — bill is ready.");
      loadSpots();
    } 
    catch (err) 
    {
      setError(err.message);
    }
  }

  return (
    <div className="panel">
      <h1 className="panel__title">Mark Entry / Exit</h1>
      <PlateChip value={data.licensePlate} />

      {error && <div className="error-banner">{error}</div>}
      {message && <p className="panel__hint">{message}</p>}

      <div className="field">
        <label htmlFor="spot-select">Available Spots</label>
        <select id="spot-select" value={selectedKey} onChange={handleSelect}>
          <option value="" disabled>
            {spots.length ? "Choose a spot…" : "No spots loaded — pick a vehicle type first"}
          </option>
          {spots.map((s) => (
            <option key={`${s.floor}-${s.spot_number}`} value={`${s.floor}-${s.spot_number}`}>
              Floor {s.floor} · Spot {s.spot_number} ({s.size})
            </option>
          ))}
        </select>
      </div>

      <div className="btn-row">
        <button className="btn btn--primary" onClick={markEntry} disabled={!selectedKey}>
          Mark Entry
        </button>
        <button className="btn" onClick={markExit}>
          Mark Exit
        </button>
      </div>

      <div className="btn-row">
        <button className="btn btn--ghost" onClick={() => goTo("billing")}>
          Generate Bill
        </button>
        <button className="btn btn--ghost" onClick={() => goTo("spots")}>
          Next Car
        </button>
        <button className="btn" disabled={!data.licensePlate} 
          onClick={() => goTo("owner")}
        > Edit Owner Details
        </button>
      </div>
    </div>
  );
}
