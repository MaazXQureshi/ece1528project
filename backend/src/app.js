import express from "express";
import cors from "cors";
import dotenv from "dotenv";

import readingsRouter from "./routes/readings.js";
import thresholdRouter from "./routes/threshold.js";

dotenv.config();
const app = express();

app.use(cors());
app.use(express.json());

app.use("/readings", readingsRouter);
app.use("/threshold", thresholdRouter);

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
