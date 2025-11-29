import express from "express";
import prisma from "../db.js";
import { sendAlertEmail } from "../app.js";

const router = express.Router();

// Part of the code below includes copying/modification of code from previous courses (particularly ECE1724 - Web Development in React), official library docs and some AI tools

// POST (use bottle_id as parameter)
router.post("/:bottle_id", async (req, res) => {
  try {
    const { vol, temp } = req.body;
    const bottle_id = parseInt(req.params.bottle_id, 10);
    const reading = await prisma.reading.create({
      data: {
        vol,
        temp,
        bottle_id,
      },
    });

    // Threshold checking for email sending
    const thresholdRecord = await prisma.threshold.findFirst({
      where: { bottle_id },
    });

    if (thresholdRecord && vol < thresholdRecord.th) {
      if (process.env.EMAIL_ON === "true") {
        await sendAlertEmail({
          bottle_id,
          vol,
          th: thresholdRecord.th,
        });
      }
    }

    res.json(reading);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET (ID)
router.get("/id/:id", async (req, res) => {
  try {
    const reading = await prisma.reading.findUnique({
      where: { id: Number(req.params.id) },
    });
    if (!reading) return res.status(404).json({ error: "Not found" });
    res.json(reading);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET - Latest X readings (use bottle_id and count as parameter)
router.get("/:bottle_id/latest/:count", async (req, res) => {
  try {
    const count = Number(req.params.count);
    const readings = await prisma.reading.findMany({
      where: { bottle_id: Number(req.params.bottle_id) },
      orderBy: { time: "desc" },
      take: count,
    });
    res.json(readings);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// DELETE
router.delete("/:id", async (req, res) => {
  try {
    await prisma.reading.delete({ where: { id: Number(req.params.id) } });
    res.json({ message: "Deleted successfully" });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

export default router;
