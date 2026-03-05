/**
 * Production server for Railway: serve build folder on PORT (0.0.0.0).
 * Ensures Railway's PORT is always used.
 */
const { spawn } = require('child_process');
const path = require('path');

const port = process.env.PORT || 8080;
const buildDir = path.join(__dirname, '..', 'build');

const env = {
  ...process.env,
  PORT: String(port),
  npm_config_loglevel: 'error',
  NPM_CONFIG_LOGLEVEL: 'error',
};
const child = spawn(
  'npx',
  ['serve', '-s', buildDir, '-l', String(port)],
  { stdio: 'inherit', env }
);

child.on('exit', (code) => process.exit(code || 0));
