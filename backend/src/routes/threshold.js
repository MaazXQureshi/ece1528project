import express from "express";
import prisma from "../db.js";

const router = express.Router();

// Part of the code below includes copying/modification of code from previous courses (particularly ECE1724 - Web Development in React), official library docs and some AI tools

// GET - current threshold (there should be only 1)
router.get("/", async (req, res) => {
  const threshold = await prisma.threshold.findFirst();
  res.json(threshold || {});
});

// PUT - update threshold
router.put("/", async (req, res) => {
  try {
    const { threshold } = req.body;
    const existing = await prisma.threshold.findFirst();
    let updated;

    if (existing) {
      updated = await prisma.threshold.update({
        where: { id: existing.id },
        data: { threshold },
      });
    } else {
      updated = await prisma.threshold.create({ data: { threshold } });
    }

    res.json(updated);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

export default router;
