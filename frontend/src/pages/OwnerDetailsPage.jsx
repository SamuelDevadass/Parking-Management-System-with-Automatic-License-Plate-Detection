import { useState, useEffect } from "react";
import { Api } from "../api/client.js";

export default function OwnerDetailsPage({ data, updateData, goTo }) 
{
  const [form, setForm] = useState({ model: "", colour: "", phone: "", name: "" });
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);

  // Reset the local form + shared owner/size fields each time this page
  // is shown, same as Page1.on_show() -> clear_fields().
  useEffect(() => 
  {
    setForm({ model: "", colour: "", phone: "", name: "" });
    updateData({ ownerId: "", size: "" });
  }, []);

  function setField(key, value) 
  {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function fetchDetails() 
  {
    setError(null);
    try 
    {
      const v = await Api.getVehicle(data.licensePlate);
      updateData({ ownerId: v.owner_id ?? "", size: v.type ?? "" });
      setForm({
        model: v.model ?? "", colour: v.colour ?? "",
        phone: v.phone ?? "", name: v.name ?? "",
      });
    } 
    catch (err) 
    {
      setError(err.message);
    }
  }

  async function saveDetails() 
  {
    setError(null);
    setSaving(true);
    const ownerId = data.ownerId || data.licensePlate;
    try 
    {
      await Api.saveVehicle({ 
        owner_id: ownerId, license_plate: data.licensePlate, model: form.model,
        colour: form.colour, type: data.size, phone: form.phone, name: form.name,
      });
      updateData({ ownerId });
    } 
    catch (err) 
    {
      setError(err.message);
    } 
    finally 
    {
      setSaving(false);
    }
  }

  return (
    <div className="panel">
      <h1 className="panel__title">User Details</h1>

      {error && <div className="error-banner">{error}</div>}

      <div className="field field--mono">
        <label>License Plate</label>
        <input value={data.licensePlate}
          onChange={(e) => updateData({ licensePlate: e.target.value })}
        />
      </div>

      <div className="field">
        <label htmlFor="size-select">Vehicle Type</label>
        <select id="size-select" value={data.size}
          onChange={(e) => updateData({ size: e.target.value, floor: null, spotNumber: null })}
        >
          <option value="" disabled>
            Choose…
          </option>
          <option value="Two Wheeler">Two Wheeler</option>
          <option value="Four Wheeler">Four Wheeler</option>
        </select>
      </div>

      <div className="field-row">
        <div className="field">
          <label>Model</label>
          <input value={form.model} onChange={(e) => setField("model", e.target.value)} />
        </div>
        <div className="field">
          <label>Colour</label>
          <input value={form.colour} onChange={(e) => setField("colour", e.target.value)} />
        </div>
      </div>

      <div className="field-row">
        <div className="field">
          <label>Owner ID</label>
          <input value={data.ownerId} onChange={(e) => updateData({ ownerId: e.target.value })} />
        </div>
        <div className="field">
          <label>Phone Number</label>
          <input value={form.phone} onChange={(e) => setField("phone", e.target.value)} />
        </div>
      </div>

      <div className="field">
        <label>Name</label>
        <input value={form.name} onChange={(e) => setField("name", e.target.value)} />
      </div>

      <div className="btn-row">
        <button className="btn" onClick={fetchDetails}>
          Fetch Details
        </button>
        <button className="btn" onClick={saveDetails} disabled={saving}>
          {saving ? "Saving…" : "Save Details"}
        </button>
      </div>

      <div className="btn-row">
        <button className="btn btn--primary" onClick={() => goTo("entry-exit")}>
          Continue
        </button>
      </div>
    </div>
  );
}
