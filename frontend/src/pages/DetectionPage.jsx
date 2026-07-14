import { useState, useEffect } from "react";
import { Api } from "../api/client.js";
import PlateChip from "../components/PlateChip.jsx";

export default function DetectionPage({ data, updateData, goTo }) 
{
  const [running, setRunning] = useState(false);
  const [error, setError] = useState(null);

  // Clear the plate field each time this page is shown, same as
  // Detection_Page.on_show() -> clear_fields().
  useEffect(() => 
  {
    updateData({ licensePlate: "" });
  }, []);

  // Polling loop: while detection is running, ask the backend every second
  // whether it's finished. This replaces the Tkinter combo of a background
  // thread + queue.Queue + self.after(100, poll) — same idea, just over
  // HTTP instead of in-process.
  useEffect(() => 
    {
    if (!running) return;
    const interval = setInterval(async () => 
    {
      try 
      {
        const result = await Api.getDetectionStatus();
        if (result.status === "done") 
        {
          updateData({ licensePlate: result.license_plate || "" });
          setRunning(false);
        } 
        else if (result.status === "error") 
        {
          setError("Detection failed on the backend.");
          setRunning(false);
        }
      } 
      catch (err) 
      {
        setError(err.message);
        setRunning(false);
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [running]);

  async function startDetection() 
  {
    setError(null);
    try 
    {
      await Api.startDetection();
      setRunning(true);
    } 
    catch (err) 
    {
      setError(err.message);
    }
  }

  async function stopDetection() 
  {
    try 
    {
      await Api.stopDetection();
    } 
    catch (err) 
    {
      setError(err.message);
    } 
    finally 
    {
      setRunning(false);
    }
  }

  return (
    <div className="panel">
      <h1 className="panel__title">Automatic License Plate Detection</h1>
      {error && <div className="error-banner">{error}</div>}
      <div className="status-row">
        <span className={`status-dot ${running ? "status-dot--running" : ""}`} />
        {running ? "Detection running…" : "Idle"}
      </div>
      <div className="btn-row">
        <button className="btn btn--primary" onClick={startDetection} disabled={running}>
          Start Detection
        </button>
        <button className="btn btn--danger" onClick={stopDetection} disabled={!running}>
          Stop Detection
        </button>
      </div>

      <div className="field field--mono">
        <label htmlFor="plate-input">License Plate</label>
        <input
          id="plate-input"
          value={data.licensePlate}
          onChange={(e) => updateData({ licensePlate: e.target.value })}
          placeholder="Detected plate appears here — or type it manually"
        />
      </div>

      <PlateChip value={data.licensePlate} />

      <div className="btn-row btn--spaced">
        <button className="btn btn--primary" disabled={!data.licensePlate} 
          onClick={() => goTo("owner")}
        > Continue
        </button>

        <button className="btn" disabled={!data.wing}
          onClick={() => goTo("spots")}
        > Empty Spots
        </button>
      </div>
    </div>
  );
}
