const express = require("express");
const router = express.Router();
const { registerUser, loginUser, verifyUser } = require("../controllers/userController");

router.post("/register", registerUser);
router.post("/login", loginUser);
router.get("/verify/:email", verifyUser);

module.exports = router;
