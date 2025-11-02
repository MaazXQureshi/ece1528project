import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import { MailService } from "@sendgrid/mail";

import readingsRouter from "./routes/readings.js";
import thresholdRouter from "./routes/threshold.js";
import cleaningRouter from "./routes/cleaning.js";

dotenv.config();
const app = express();

const sendgridClient = new MailService();
sendgridClient.setApiKey(process.env.SENDGRID_API_KEY);

export async function sendAlertEmail({ bottle_id, volume, threshold }) {
  const msg = {
    to: process.env.ALERT_EMAIL_RECIPIENT,
    from: process.env.FROM_EMAIL,
    subject: `Alert — Bottle ${bottle_id} below threshold`,
    text: `Bottle ${bottle_id}'s volume is currently ${volume} ml, below set threshold of ${threshold}.`,
  };

  await sendgridClient.send(msg);
}

app.use(cors());
app.use(express.json());

app.use("/readings", readingsRouter);
app.use("/threshold", thresholdRouter);
app.use("/cleaning", cleaningRouter);

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
