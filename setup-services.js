#!/usr/bin/env node
/**
 * Configuration Helper - Catalyst AI Full Stack
 * 
 * This script helps you configure and start all services
 * Run with: node setup-services.js
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const services = {
  python: {
    name: 'Python Backend (FastAPI)',
    cwd: 'D:\\Downloads\\LLM-Pr\\catalyst-ai-backend',
    command: 'python',
    args: ['-m', 'uvicorn', 'app.main:app', '--reload', '--host', '0.0.0.0', '--port', '8000'],
    env: { ...process.env, PYTHONUNBUFFERED: '1' },
    port: 8000,
    color: '\x1b[36m', // Cyan
  },
  nodejs: {
    name: 'Node.js Backend (Express)',
    cwd: 'D:\\Downloads\\LLM-Pr\\catalyst-ai-backend\\making ai project neural ai - Copy\\Catalyst-ai\\backend',
    command: 'npm',
    args: ['start'],
    port: 5000,
    color: '\x1b[32m', // Green
  },
  frontend: {
    name: 'React Frontend (Vite)',
    cwd: 'D:\\Downloads\\LLM-Pr\\catalyst-ai-backend\\making ai project neural ai - Copy\\Catalyst-ai\\frontend',
    command: 'npm',
    args: ['run', 'dev'],
    port: 5173,
    color: '\x1b[33m', // Yellow
  },
};

function startService(serviceName) {
  const service = services[serviceName];
  if (!service) {
    console.error(`Unknown service: ${serviceName}`);
    return;
  }

  console.log(`${service.color}[${serviceName.toUpperCase()}] Starting ${service.name} on port ${service.port}...`);
  console.log(`${service.color}Working directory: ${service.cwd}\x1b[0m`);

  const child = spawn(service.command, service.args, {
    cwd: service.cwd,
    env: service.env,
    stdio: 'inherit',
  });

  child.on('error', (err) => {
    console.error(`${service.color}[${serviceName.toUpperCase()}] Error: ${err.message}\x1b[0m`);
  });

  child.on('exit', (code) => {
    console.log(`${service.color}[${serviceName.toUpperCase()}] Exited with code ${code}\x1b[0m`);
  });

  return child;
}

function main() {
  console.log('\x1b[35m╔════════════════════════════════════════════╗\x1b[0m');
  console.log('\x1b[35m║  Catalyst AI - Full Stack Setup             ║\x1b[0m');
  console.log('\x1b[35m╚════════════════════════════════════════════╝\x1b[0m\n');

  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log('Usage: node setup-services.js [service]\n');
    console.log('Available services:');
    console.log('  all       - Start all services (Python, Node.js, React)');
    console.log('  python    - Start Python backend only');
    console.log('  nodejs    - Start Node.js backend only');
    console.log('  frontend  - Start React frontend only\n');
    console.log('Examples:');
    console.log('  node setup-services.js all');
    console.log('  node setup-services.js python\n');
    return;
  }

  if (args[0] === 'all') {
    startService('python');
    setTimeout(() => startService('nodejs'), 2000);
    setTimeout(() => startService('frontend'), 4000);
    
    console.log('\n\x1b[35m════════════════════════════════════════════\x1b[0m');
    console.log('\x1b[35mAll services started!\x1b[0m');
    console.log('\x1b[35m════════════════════════════════════════════\x1b[0m');
    console.log('\n📍 Services running at:');
    console.log('\x1b[36m   Frontend:      http://localhost:5173\x1b[0m');
    console.log('\x1b[32m   Node.js:       http://localhost:5000\x1b[0m');
    console.log('\x1b[33m   Python:        http://localhost:8000\x1b[0m');
    console.log('\x1b[33m   API Docs:      http://localhost:8000/docs\x1b[0m\n');
  } else if (args[0] === 'python' || args[0] === 'nodejs' || args[0] === 'frontend') {
    startService(args[0]);
  } else {
    console.error(`Unknown argument: ${args[0]}`);
    console.log('Use "all", "python", "nodejs", or "frontend"');
  }
}

main();
