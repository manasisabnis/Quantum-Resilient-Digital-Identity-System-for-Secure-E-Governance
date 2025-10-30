const mongoose = require('mongoose');
const userSchema = new mongoose.Schema({
  username: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  encryptedData: { type: String, default: null },
  blockchainHash: { type: String, default: null }
});
module.exports = mongoose.model('User', userSchema);