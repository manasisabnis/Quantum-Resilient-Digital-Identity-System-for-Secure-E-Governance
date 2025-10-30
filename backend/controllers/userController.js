const User = require("../models/userModel");
const crypto = require("crypto");

const registerUser = async (req, res) => {
  try {
    const { username, email, password } = req.body;
    const encryptedData = Buffer.from(password).toString("base64");
    const blockchainHash = crypto.createHash("sha256").update(password).digest("hex");

    const newUser = new User({ username, email, password, encryptedData, blockchainHash });
    await newUser.save();
    res.status(201).json({ message: "User registered", newUser });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

const loginUser = async (req, res) => {
  try {
    const { email, password } = req.body;
    const user = await User.findOne({ email });
    if (!user) return res.status(404).json({ message: "User not found" });
    if (user.password !== password) return res.status(401).json({ message: "Invalid password" });
    res.status(200).json({ message: "Login successful", user });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

const verifyUser = async (req, res) => {
  try {
    const { email } = req.params;
    const user = await User.findOne({ email });
    if (!user) return res.status(404).json({ message: "User not found" });
    res.status(200).json({ message: "Identity verified", blockchainHash: user.blockchainHash });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

module.exports = { registerUser, loginUser, verifyUser };
