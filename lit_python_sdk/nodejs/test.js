const fetch = require("node-fetch");

async function checkIsReady() {
  try {
    const response = await fetch("http://localhost:3092/isReady", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });
    const data = await response.json();
    return data.ready;
  } catch (error) {
    return false;
  }
}

async function waitUntilReady(maxAttempts = 30, delayMs = 1000) {
  for (let i = 0; i < maxAttempts; i++) {
    console.log(
      `Checking if server is ready (attempt ${i + 1}/${maxAttempts})...`
    );
    const isReady = await checkIsReady();
    if (isReady) {
      console.log("Server is ready!");
      return true;
    }
    await new Promise((resolve) => setTimeout(resolve, delayMs));
  }
  throw new Error("Server failed to become ready in time");
}

async function testExecuteJs() {
  try {
    const response = await fetch("http://localhost:3092/executeJs", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        code: `
          (async () => {
              console.log("This is a log");
              Lit.Actions.setResponse({response: "Hello, World!"});
          })()
        `,
        jsParams: {},
      }),
    });

    const data = await response.json();
    console.log("Response:", data);
  } catch (error) {
    console.error("Error:", error);
  }
}

// Run the test with readiness check
async function runTest() {
  try {
    await waitUntilReady();
    await testExecuteJs();
  } catch (error) {
    console.error("Test failed:", error);
    process.exit(1);
  }
}

runTest();
