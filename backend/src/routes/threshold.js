import express from "express";
import prisma from "../db.js";

const router = express.Router();

// Part of the code below includes copying/modification of code from previous courses (particularly ECE1724 - Web Development in React), official library docs and some AI tools

// GET - current threshold (there should be only 1)
router.get("/:bottle_id", async (req, res) => {
  try {
    const bottle_id = parseInt(req.params.bottle_id, 10);
    if (isNaN(bottle_id)) {
      return res.status(400).json({ error: "Invalid bottle_id" });
    }

    const th = await prisma.threshold.findFirst({
      where: { bottle_id },
    });

    res.json(th || {});
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// PUT - update threshold
router.put("/:bottle_id", async (req, res) => {
  try {
    const bottle_id = parseInt(req.params.bottle_id, 10);
    const { th } = req.body;

    if (isNaN(bottle_id)) {
      return res.status(400).json({ error: "Invalid bottle_id" });
    }
    if (th === undefined) {
      return res.status(400).json({ error: "Missing 'threshold' value" });
    }

    const existing = await prisma.threshold.findFirst({
      where: { bottle_id },
    });

    let updated;

    if (existing) {
      updated = await prisma.threshold.update({
        where: { id: existing.id },
        data: { th },
      });
    } else {
      updated = await prisma.threshold.create({
        data: { bottle_id, th },
      });
    }

    res.json(updated);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

export default router;
