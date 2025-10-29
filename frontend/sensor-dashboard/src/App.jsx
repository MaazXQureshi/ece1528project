import { useEffect, useState } from "react";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL;

function App() {
  const [reading, setReading] = useState(null);
  const [threshold, setThreshold] = useState("");
  const [newThreshold, setNewThreshold] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchLatestReading = async () => {
    try {
      console.log(API_URL);
      const res = await axios.get(`${API_URL}/readings/latest/1`);
      setReading(res.data[0]);
    } catch (err) {
      console.error("Error fetching latest reading:", err);
    }
  };

  const fetchThreshold = async () => {
    try {
      const res = await axios.get(`${API_URL}/threshold`);
      setThreshold(res.data?.threshold || 0);
    } catch (err) {
      console.error("Error fetching threshold:", err);
    }
  };

  const updateThreshold = async () => {
    try {
      await axios.put(`${API_URL}/threshold`, {
        threshold: parseFloat(newThreshold),
      });
      setThreshold(newThreshold);
      setNewThreshold("");
      alert("Threshold updated successfully!");
    } catch (err) {
      console.error("Error updating threshold:", err);
      alert("Failed to update threshold.");
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      await Promise.all([fetchLatestReading(), fetchThreshold()]);
      setLoading(false);
    };

    fetchData();
    const interval = setInterval(fetchLatestReading, 60000); // Can change this to refresh every X ms - currently 60s
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
      <div className="justify-center max-w-3xl bg-gray-800 rounded-2xl shadow-2xl border border-gray-700 p-8 mx-auto">
        <h1 className="text-3xl font-bold text-center text-blue-400 mb-8">
          Sensor Dashboard
        </h1>

        {/* Latest Reading Section */}
        <div className="mb-10">
          <h2 className="text-xl font-semibold text-gray-200 mb-3">
            Latest Reading
          </h2>
          {reading ? (
            <div className="grid grid-cols-2 gap-y-2 text-gray-300 text-lg">
              <p>
                <strong>Volume:</strong> {reading.volume} ml
              </p>
              <p>
                <strong>Angle:</strong> {reading.angle}°
              </p>
              <p>
                <strong>Temperature:</strong> {reading.temperature}° C
              </p>
              <p>
                <strong>Time:</strong> {new Date(reading.time).toLocaleString()}
              </p>
            </div>
          ) : (
            <p>No readings found.</p>
          )}
        </div>

        {/* Threshold Section */}
        <div className="pt-4 border-t border-gray-700">
          <h2 className="text-xl font-semibold text-gray-200 mb-3">
            Volume Threshold Control
          </h2>
          <p className="mb-4 text-gray-400">
            Current threshold:{" "}
            <span className="font-bold text-blue-400">{threshold} ml</span>
          </p>

          <div className="flex items-center gap-3">
            <input
              type="number"
              value={newThreshold}
              onChange={(e) => setNewThreshold(e.target.value)}
              className="bg-gray-700 text-gray-100 border border-gray-600 rounded-lg px-4 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-400 placeholder-gray-400"
              placeholder="Enter new volume threshold"
            />
            <button
              onClick={updateThreshold}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-500 transition"
            >
              Update
            </button>
          </div>
        </div>
      </div>

      <p className="mt-6 text-gray-500 text-sm">
        Auto-refreshing every 60 seconds
      </p>
    </div>
  );
}

export default App;
