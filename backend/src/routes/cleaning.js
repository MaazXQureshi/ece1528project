import express from "express";
import prisma from "../db.js";

const router = express.Router();

// Part of the code below includes copying/modification of code from previous courses (particularly ECE1724 - Web Development in React), official library docs and some AI tools

// GET - current cleaning mode (there should be only 1)
router.get("/:bottle_id", async (req, res) => {
  try {
    const bottle_id = parseInt(req.params.bottle_id, 10);
    if (isNaN(bottle_id)) {
      return res.status(400).json({ error: "Invalid bottle_id" });
    }

    const cleaning = await prisma.cleaning.findFirst({
      where: { bottle_id },
    });

    res.json(cleaning || {});
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// PUT - update cleaning
router.put("/:bottle_id", async (req, res) => {
  try {
    const bottle_id = parseInt(req.params.bottle_id, 10);
    const { cleaning } = req.body;

    if (isNaN(bottle_id)) {
      return res.status(400).json({ error: "Invalid bottle_id" });
    }
    if (cleaning === undefined) {
      return res.status(400).json({ error: "Missing 'cleaning' value" });
    }

    const existing = await prisma.cleaning.findFirst({
      where: { bottle_id },
    });

    let updated;

    if (existing) {
      updated = await prisma.cleaning.update({
        where: { id: existing.id },
        data: { cleaning },
      });
    } else {
      updated = await prisma.cleaning.create({
        data: { bottle_id, cleaning },
      });
    }

    res.json(updated);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

export default router;
