const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
require('dotenv').config();
const User = require('./models/userModel');
const userRoutes = require('./routes/userRoutes');

const app = express();
app.use(express.json());
app.use(cors({ origin: '*' }));

mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log('MongoDB connected'))
  .catch(err => console.error('Connection error:', err));

app.use('/api/users', userRoutes);

// Add a sample user once
const createSampleUser = async () => {
  const existing = await User.findOne({ username: 'testuser' });
  if (!existing) {
    const newUser = new User({ username: 'testuser', password: '1234' });
    await newUser.save();
    console.log('Sample user created: testuser / 1234');
  }
};
mongoose.connection.once('open', createSampleUser);

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));