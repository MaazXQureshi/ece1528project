import express from "express";
import prisma from "../db.js";

const router = express.Router();

// Part of the code below includes copying/modification of code from previous courses (particularly ECE1724 - Web Development in React), official library docs and some AI tools

// POST (use bottle_id as parameter)
router.post("/:bottle_id", async (req, res) => {
  try {
    const { volume, roll, pitch, yaw, temperature } = req.body;
    const reading = await prisma.reading.create({
      data: {
        volume,
        roll,
        pitch,
        yaw,
        temperature,
        bottle_id: Number(req.params.bottle_id),
      },
    });
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
