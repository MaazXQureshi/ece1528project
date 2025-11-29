import express from "express";
import prisma from "../db.js";
import { sendSpillingEmail } from "../app.js";

const router = express.Router();

// Part of the code below includes copying/modification of code from previous courses (particularly ECE1724 - Web Development in React), official library docs and some AI tools

// GET - current spilling flag (there should be only 1)
router.get("/:bottle_id", async (req, res) => {
  try {
    const bottle_id = parseInt(req.params.bottle_id, 10);
    if (isNaN(bottle_id)) {
      return res.status(400).json({ error: "Invalid bottle_id" });
    }

    const flag = await prisma.spilling.findFirst({
      where: { bottle_id },
    });

    res.json(flag || {});
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// PUT - update spilling
router.put("/:bottle_id", async (req, res) => {
  try {
    const bottle_id = parseInt(req.params.bottle_id, 10);
    const { flag } = req.body;

    if (isNaN(bottle_id)) {
      return res.status(400).json({ error: "Invalid bottle_id" });
    }
    if (flag === undefined) {
      return res.status(400).json({ error: "Missing 'flag' value" });
    }

    const existing = await prisma.spilling.findFirst({
      where: { bottle_id },
    });

    let updated;

    if (existing) {
      updated = await prisma.spilling.update({
        where: { id: existing.id },
        data: { flag },
      });
    } else {
      updated = await prisma.spilling.create({
        data: { bottle_id, flag },
      });
    }

    if (flag) {
      if (process.env.EMAIL_ON) {
        await sendSpillingEmail(bottle_id);
      }
    }

    res.json(updated);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

export default router;
