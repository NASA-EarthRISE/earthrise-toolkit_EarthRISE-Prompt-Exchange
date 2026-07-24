const pa11y = require('C:/Users/washmall/AppData/Roaming/npm/node_modules/pa11y');
const fs = require('fs');

const SESSION_COOKIE = 'sessionid=qn2bhqguj0yh1y3y2vta2z48oxhclz88';

const pages = [
  { url: 'http://localhost:8000/accounts/login/', name: 'Login Page', auth: false },
  { url: 'http://localhost:8000/access-denied/', name: 'Access Denied Page', auth: true },
  { url: 'http://localhost:8000/', name: 'Home Page', auth: true },
  { url: 'http://localhost:8000/prompts/', name: 'Browse Prompts', auth: true },
  { url: 'http://localhost:8000/prompts/solution-co-development-toolkit-web-app/', name: 'Prompt Detail', auth: true },
  { url: 'http://localhost:8000/prompts/create/', name: 'Create Prompt', auth: true },
  { url: 'http://localhost:8000/my-prompts/', name: 'My Prompts', auth: true },
];

const options = {
  standard: 'WCAG2AA',
  runners: ['axe', 'htmlcs'],
  includeNotices: true,
  includeWarnings: true,
  timeout: 60000,
  wait: 1000,
  chromeLaunchConfig: {
    executablePath: 'C:\\Users\\washmall\\.cache\\puppeteer\\chrome\\win64-150.0.7871.24\\chrome-win64\\chrome.exe',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  },
};

async function runTests() {
  const allResults = [];

  for (const page of pages) {
    console.error(`Testing: ${page.name} (${page.url})`);
    try {
      const pageOptions = { ...options };
      if (page.auth) {
        pageOptions.headers = { Cookie: SESSION_COOKIE };
      }
      // Run with htmlcs
      const htmlcsResult = await pa11y(page.url, {
        ...pageOptions,
        runners: ['htmlcs'],
      });
      // Run with axe
      const axeResult = await pa11y(page.url, {
        ...pageOptions,
        runners: ['axe'],
      });

      allResults.push({
        page: page.name,
        url: page.url,
        htmlcs: htmlcsResult,
        axe: axeResult,
      });
      console.error(`  Done: ${htmlcsResult.issues.length} htmlcs issues, ${axeResult.issues.length} axe issues`);
    } catch (err) {
      console.error(`  ERROR: ${err.message}`);
      allResults.push({
        page: page.name,
        url: page.url,
        error: err.message,
      });
    }
  }

  console.log(JSON.stringify(allResults, null, 2));
}

runTests().catch(console.error);
