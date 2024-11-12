const express = require("express");
const bodyParser = require("body-parser");
const LitJsSdk = require("@lit-protocol/lit-node-client-nodejs");
const { LitNetwork, LIT_RPC } = require("@lit-protocol/constants");
const ethers = require("ethers");
const {
  LitAbility,
  LitActionResource,
  createSiweMessage,
  generateAuthSig,
} = require("@lit-protocol/auth-helpers");

if (typeof localStorage === "undefined" || localStorage === null) {
  var LocalStorage = require("node-localstorage").LocalStorage;
  localStorage = new LocalStorage("./lit-session-storage");
}

const app = express();
const port = 3092;

// Middleware
app.use(bodyParser.json());

// Enable CORS for localhost development
app.use((req, res, next) => {
  res.header("Access-Control-Allow-Origin", "*");
  res.header(
    "Access-Control-Allow-Headers",
    "Origin, X-Requested-With, Content-Type, Accept"
  );
  res.header("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  next();
});

// generate session key and get session delegation
app.post("/isReady", (req, res) => {
  try {
    res.json({
      ready: app.locals.litNodeClient.ready,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

app.post("/executeJs", async (req, res) => {
  try {
    const { code, jsParams } = req.body;

    if (!code) {
      return res.status(400).json({
        success: false,
        error: "No code provided",
      });
    }

    // get session sigs
    const sessionSigs = await app.locals.litNodeClient.getSessionSigs({
      chain: "ethereum",
      expiration: new Date(Date.now() + 1000 * 60 * 10).toISOString(), // 10 minutes
      resourceAbilityRequests: [
        {
          resource: new LitActionResource("*"),
          ability: LitAbility.LitActionExecution,
        },
      ],
      authNeededCallback: async ({
        uri,
        expiration,
        resourceAbilityRequests,
      }) => {
        const toSign = await createSiweMessage({
          uri,
          expiration,
          resources: resourceAbilityRequests,
          walletAddress: await app.locals.ethersWallet.getAddress(),
          nonce: await app.locals.litNodeClient.getLatestBlockhash(),
          litNodeClient: app.locals.litNodeClient,
        });

        return await generateAuthSig({
          signer: app.locals.ethersWallet,
          toSign,
        });
      },
    });

    // execute js
    const response = await app.locals.litNodeClient.executeJs({
      sessionSigs: sessionSigs,
      code,
      jsParams,
    });

    res.json(response);
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error,
      stack: error.stack,
      message: error.message,
    });
  }
});

// Basic health check endpoint
app.get("/", (req, res) => {
  res.json({ status: "Server is running" });
});

// Start the server
app.listen(port, async () => {
  app.locals.litNodeClient = new LitJsSdk.LitNodeClientNodeJs({
    litNetwork: LitNetwork.DatilDev,
  });
  await app.locals.litNodeClient.connect();
  app.locals.ethersWallet = new ethers.Wallet(
    process.env.LIT_SDK_SERVER_DEPLOYER_PRIVATE_KEY,
    new ethers.providers.JsonRpcProvider(LIT_RPC.CHRONICLE_YELLOWSTONE)
  );
  console.log(`Server running at http://localhost:${port}`);
});
