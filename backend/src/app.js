import express from "express";
import cors from "cors";
import dotenv from "dotenv";

import readingsRouter from "./routes/readings.js";
import thresholdRouter from "./routes/threshold.js";
import cleaningRouter from "./routes/cleaning.js";

dotenv.config();
const app = express();

app.use(cors());
app.use(express.json());

app.use("/readings", readingsRouter);
app.use("/threshold", thresholdRouter);
app.use("/cleaning", cleaningRouter);

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
