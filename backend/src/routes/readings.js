import express from "express";
import prisma from "../db.js";

const router = express.Router();

// POST
router.post("/", async (req, res) => {
  try {
    const { volume, angle, temperature } = req.body;
    const reading = await prisma.reading.create({
      data: { volume, angle, temperature },
    });
    res.json(reading);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET (ID)
router.get("/:id", async (req, res) => {
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

// GET - Latest X readings (use count as parameter)
router.get("/latest/:count", async (req, res) => {
  try {
    const count = Number(req.params.count);
    const readings = await prisma.reading.findMany({
      orderBy: { time: "desc" },
      take: count,
    });
    res.json(readings);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET - Returns latest entry
router.get("/latest", async (req, res) => {
  try {
    const latest = await prisma.reading.findFirst({
      orderBy: { time: "desc" },
    });
    res.json(latest);
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
