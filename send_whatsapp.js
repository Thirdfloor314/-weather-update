const { Client } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

const client = new Client();
client.on('qr', qr => qrcode.generate(qr, {small: true}));
client.on('ready', async () => {
  const numbers = process.env.RECIPIENT_NUMBERS.split(',');
  const message = "Your weather alert message";
  
  for (const num of numbers) {
    await client.sendMessage(num + '@c.us', message);
  }
  process.exit(0);
});

client.initialize();
