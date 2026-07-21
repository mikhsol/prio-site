const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

async function captureDesktop() {
  const outputDir = "/Users/mikhail/.copilot/session-state/10c93ad5-2784-4faf-9489-3a42de116530/files";
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 1024 } });

  try {
    console.log("Navigating to http://127.0.0.1:4174/");
    await page.goto("http://127.0.0.1:4174/", { waitUntil: "networkidle" });

    console.log("Screenshotting hero...");
    await page.screenshot({ path: path.join(outputDir, "surf-desktop-hero.png"), selector: ".hero-showcase" });

    console.log("Screenshotting viewport...");
    await page.screenshot({ path: path.join(outputDir, "surf-desktop-viewport.png") });

    console.log("Scrolling to gallery...");
    await page.evaluate(() => {
      document.querySelector('#screens').scrollIntoView();
    });
    await page.waitForTimeout(500);

    console.log("Screenshotting gallery...");
    await page.screenshot({ path: path.join(outputDir, "surf-desktop-gallery.png"), selector: ".gallery-grid" });

    console.log("Desktop screenshots complete!");
  } finally {
    await browser.close();
  }
}

async function captureMobile() {
  const outputDir = "/Users/mikhail/.copilot/session-state/10c93ad5-2784-4faf-9489-3a42de116530/files";
  
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 430, height: 932 } });

  try {
    console.log("Mobile: Navigating to http://127.0.0.1:4174/");
    await page.goto("http://127.0.0.1:4174/", { waitUntil: "networkidle" });

    console.log("Mobile: Screenshotting hero...");
    await page.screenshot({ path: path.join(outputDir, "surf-mobile-hero.png"), selector: ".hero-showcase" });

    console.log("Mobile: Checking horizontal overflow...");
    const overflow = await page.evaluate(() => {
      return document.documentElement.scrollWidth > window.innerWidth;
    });
    console.log(`Mobile: Horizontal overflow: ${overflow}`);

    console.log("Mobile: Scrolling to gallery...");
    await page.evaluate(() => {
      document.querySelector('#screens').scrollIntoView();
    });
    await page.waitForTimeout(500);

    console.log("Mobile: Screenshotting gallery...");
    await page.screenshot({ path: path.join(outputDir, "surf-mobile-gallery.png"), selector: "#screens" });

    console.log("Mobile screenshots complete!");
    return overflow;
  } finally {
    await browser.close();
  }
}

async function main() {
  try {
    console.log("Starting screenshot capture...");
    await captureDesktop();
    const overflow = await captureMobile();

    console.log("\n=== RESULTS ===");
    console.log(`Horizontal overflow on mobile: ${overflow}`);

    const outputDir = "/Users/mikhail/.copilot/session-state/10c93ad5-2784-4faf-9489-3a42de116530/files";
    console.log("\nFiles created:");
    const files = fs.readdirSync(outputDir).filter(f => f.startsWith("surf-")).sort();
    for (const f of files) {
      console.log(`  ${f}`);
    }
  } catch (error) {
    console.error("Error:", error);
    process.exit(1);
  }
}

main();
