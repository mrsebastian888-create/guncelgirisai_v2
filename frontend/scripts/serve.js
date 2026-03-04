/**
 * Production server for Railway: serve build folder on PORT (0.0.0.0).
 * Ensures Railway's PORT is always used.
 */
const { spawn } = require('child_process');
const path = require('path');

const port = process.env.PORT || 8080;
const buildDir = path.join(__dirname, '..', 'build');

const child = spawn(
  'npx',
  ['serve', '-s', buildDir, '-l', String(port)],
  { stdio: 'inherit', env: { ...process.env, PORT: String(port) } }
);

child.on('exit', (code) => process.exit(code || 0));
