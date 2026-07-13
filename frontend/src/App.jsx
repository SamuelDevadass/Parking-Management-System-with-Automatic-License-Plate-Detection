import { useState } from "react";
import StepBar from "./components/StepBar.jsx";
import SelectWingPage from "./pages/SelectWingPage.jsx";
import EmptySpotsPage from "./pages/EmptySpotsPage.jsx";
import DetectionPage from "./pages/DetectionPage.jsx";
import OwnerDetailsPage from "./pages/OwnerDetailsPage.jsx";
import EntryExitPage from "./pages/EntryExitPage.jsx";
import BillingPage from "./pages/BillingPage.jsx";

/*
  App is the direct equivalent of your ParkingApp(tk.Tk) class:
  - `data` replaces `self.shared_data` (the dict of tk.StringVars)
  - `updateData` replaces calling `.set(...)` on those vars
  - `page` + `goTo` replace `self.show_page(page_name)` / frame.tkraise()

  The big conceptual shift: Tkinter mutated shared_data in place, and
  widgets bound to it via StringVar updated themselves automatically.
  React never mutates state in place — updateData always returns a NEW
  object, and React re-renders whatever reads that state. That's the one
  habit to build first; everything else in this codebase follows from it.
*/
export default function App() 
{
  const [page, setPage] = useState("wing");

  const [data, setData] = useState
  ({
    licensePlate: "",
    wing: "",
    centre_id: null,
    floor: null,
    spotNumber: null,
    size: "",
    ownerId: "",
    folderPath: "",
  });

  // Shallow-merges patch into data, e.g. updateData({ wing: "A" })
  function updateData(patch) 
  {
    setData((prev) => ({ ...prev, ...patch }));
  }

  function goTo(nextPage) 
  {
    setPage(nextPage);
  }

  const pageProps = { data, updateData, goTo };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">
        Parking Management System<span> - License Plate Detection</span>
        </div>
        <div className="subtitle">Parking Console</div>
      </header>

      <StepBar current={page} />

      {page === "wing" && <SelectWingPage {...pageProps} />}
      {page === "spots" && <EmptySpotsPage {...pageProps} />}
      {page === "detect" && <DetectionPage {...pageProps} />}
      {page === "owner" && <OwnerDetailsPage {...pageProps} />}
      {page === "entry-exit" && <EntryExitPage {...pageProps} />}
      {page === "billing" && <BillingPage {...pageProps} />}
    </div>
  );
}
