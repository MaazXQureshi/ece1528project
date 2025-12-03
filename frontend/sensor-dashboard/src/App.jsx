import { useEffect, useState } from "react";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL;

// Part of the code below includes copying/modification of code from previous courses (particularly ECE1724 - Web Development in React), official library docs and some AI tools

const bottle_ids = [1, 2];

function App() {
  const [readings, setReadings] = useState([null, null]);
  const [thresholds, setThresholds] = useState([0, 0]);
  const [cleanings, setCleanings] = useState([false, false]);
  const [spillings, setSpillings] = useState([false, false]);
  const [newThresholds, setNewThresholds] = useState(["", ""]);
  const [loading, setLoading] = useState(true);
  const [errors, setErrors] = useState(["", ""]);

  const fetchLatestReading = async (bottle_id) => {
    try {
      console.log(API_URL);
      const res = await axios.get(`${API_URL}/readings/${bottle_id}/latest/1`);
      setReadings((prev) => {
        const updated = [...prev];
        updated[bottle_id - 1] = res.data[0];
        return updated;
      });
    } catch (error) {
      console.error("Error fetching latest reading:", error);
    }
  };

  const fetchThreshold = async (bottle_id) => {
    try {
      const res = await axios.get(`${API_URL}/threshold/${bottle_id}`);
      setThresholds((prev) => {
        const updated = [...prev];
        updated[bottle_id - 1] = res.data?.th || 0;
        return updated;
      });
    } catch (error) {
      console.error("Error fetching threshold:", error);
    }
  };

  const fetchCleaning = async (bottle_id) => {
    try {
      const res = await axios.get(`${API_URL}/cleaning/${bottle_id}`);
      setCleanings((prev) => {
        const updated = [...prev];
        updated[bottle_id - 1] = res.data?.clean || false;
        return updated;
      });
    } catch (error) {
      console.error("Error fetching cleaning:", error);
    }
  };

  const fetchSpilling = async (bottle_id) => {
    try {
      const res = await axios.get(`${API_URL}/spilling/${bottle_id}`);
      setSpillings((prev) => {
        const updated = [...prev];
        updated[bottle_id - 1] = res.data?.flag || false;
        return updated;
      });
    } catch (error) {
      console.error("Error fetching spilling:", error);
    }
  };

  const updateThreshold = async (bottle_id) => {
    try {
      if (parseFloat(newThresholds[bottle_id - 1]) < 0) {
        setErrors((prev) => {
          const updated = [...prev];
          updated[bottle_id - 1] = "Only positive thresholds allowed";
          return updated;
        });
        return;
      }

      setErrors((prev) => {
        const updated = [...prev];
        updated[bottle_id - 1] = "";
        return updated;
      });

      await axios.put(`${API_URL}/threshold/${bottle_id}`, {
        th: parseFloat(newThresholds[bottle_id - 1]),
      });
      setThresholds((prev) => {
        const updated = [...prev];
        updated[bottle_id - 1] = newThresholds[bottle_id - 1];
        return updated;
      });
      setNewThresholds((prev) => {
        const updated = [...prev];
        updated[bottle_id - 1] = "";
        return updated;
      });
      alert(`Threshold updated successfully for bottle ${bottle_id}`);
    } catch (error) {
      console.error("Error updating threshold:", error);
      alert("Failed to update threshold");
    }
  };

  const updateCleaning = async (bottle_id) => {
    try {
      const newCleaning = !cleanings[bottle_id - 1];
      await axios.put(`${API_URL}/cleaning/${bottle_id}`, {
        clean: newCleaning,
      });
      setCleanings((prev) => {
        const updated = [...prev];
        updated[bottle_id - 1] = newCleaning;
        return updated;
      });
      alert(`Cleaning mode updated successfully for bottle ${bottle_id}`);
    } catch (error) {
      console.error("Error updating cleaning:", error);
      alert("Failed to update cleaning mode");
    }
  };

  // https://stackoverflow.com/questions/64363561/refresh-data-received-from-an-api-every-minute-react-javascript
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      await Promise.all(
        bottle_ids.map(async (id) => {
          await Promise.all([
            fetchLatestReading(id),
            fetchThreshold(id),
            fetchCleaning(id),
            fetchSpilling(id),
          ]);
        })
      );
      setLoading(false);
    };

    fetchData();
    const interval = setInterval(fetchData, 10000); // Can change this to refresh every X ms - currently 60s - change to 60s or more later
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen text-gray-600">
        Loading dashboard...
      </div>
    );
  }

  return (
    <div className="min-h-screen min-w-screen flex flex-col items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-gray-100 p-6">
      <h1 className="text-3xl font-bold text-center text-blue-400 mb-8 items-center">
        Sensor Dashboard
      </h1>

      {/* Bottle Info Cards */}
      <div className="w-full grid grid-cols-1 md:grid-cols-2 gap-8 max-w-7xl">
        {bottle_ids.map((bottle_id) => (
          <div
            key={bottle_id}
            className="bg-gray-800 rounded-2xl shadow-2xl border border-gray-700 p-8"
          >
            <h2 className="text-2xl font-semibold text-center text-blue-300 mb-6">
              Bottle {bottle_id}
            </h2>

            {/* Readings Section */}
            <div className="mb-10">
              <h3 className="text-xl font-semibold text-gray-200 mb-3">
                Latest Reading
              </h3>
              {!cleanings[bottle_id - 1] ? (
                readings[bottle_id - 1] ? (
                  <div>
                    <div className="grid grid-cols-2 gap-y-2 text-gray-300 text-lg">
                      <p>
                        <strong>Volume:</strong> {readings[bottle_id - 1].vol.toFixed(2)}{" "}
                        ml
                      </p>
                      <p>
                        <strong>Temperature:</strong>{" "}
                        {readings[bottle_id - 1].temp.toFixed(2)}° C
                      </p>
                      <p>
                        <strong>Time:</strong>{" "}
                        {new Date(
                          readings[bottle_id - 1].time
                        ).toLocaleString()}
                      </p>
                    </div>
                    <div className="text-gray-300 text-lg">
                      {spillings[bottle_id - 1] ? (
                        <div className="text-red-500">
                          Spilling Hazard Warning
                        </div>
                      ) : (
                        <div className="text-green-600">
                          Bottle is safe from spilling hazards
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  <p>No readings found.</p>
                )
              ) : (
                <p className="font-bold text-red-400">
                  Readings paused. Bottle is currently in cleaning mode.
                </p>
              )}
            </div>

            {/* Threshold Section */}
            <div className="pt-4 border-t border-gray-700">
              <h3 className="text-xl font-semibold text-gray-200 mb-3">
                Volume Threshold Control
              </h3>
              <p className="mb-4 text-gray-400">
                Current threshold:{" "}
                <span className="font-bold text-blue-400">
                  {thresholds[bottle_id - 1]} ml
                </span>
              </p>

              <div className="flex items-center gap-3">
                <input
                  type="number"
                  value={newThresholds[bottle_id - 1]}
                  onChange={(e) => {
                    setNewThresholds((prev) => {
                      const updated = [...prev];
                      updated[bottle_id - 1] = e.target.value.toString();
                      return updated;
                    });
                  }}
                  className="bg-gray-700 text-gray-100 border border-gray-600 rounded-lg px-4 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-400 placeholder-gray-400"
                  placeholder="Enter new volume threshold"
                />
                <button
                  onClick={() => updateThreshold(bottle_id)}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-500 transition"
                >
                  Update
                </button>
              </div>
              {errors[bottle_id - 1] && (
                <div className="text-red-400">{errors[bottle_id - 1]}</div>
              )}
            </div>

            {/* Cleaning Mode Section */}
            <div className="pt-4 border-t border-gray-700 mt-6">
              <h3 className="text-xl font-semibold text-gray-200 mb-3">
                Cleaning Mode Control
              </h3>
              <p className="mb-4 text-gray-400">
                <span className="font-bold text-blue-400">
                  {cleanings[bottle_id - 1]
                    ? "Bottle in cleaning mode"
                    : "Bottle in measuring mode"}
                </span>
              </p>

              <div className="flex items-center gap-3">
                <button
                  onClick={() => updateCleaning(bottle_id)}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-500 transition"
                >
                  Toggle Cleaning Mode
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
