const express = require("express");
const bodyParser = require("body-parser");
const LitJsSdk = require("@lit-protocol/lit-node-client-nodejs");
const {
  LitNetwork,
  LIT_RPC,
  AuthMethodScope,
  AuthMethodType,
  ProviderType,
  LIT_ABILITY,
} = require("@lit-protocol/constants");
const ethers = require("ethers");
const {
  LitAbility,
  LitActionResource,
  LitPKPResource,
  createSiweMessage,
  generateAuthSig,
} = require("@lit-protocol/auth-helpers");
const { LitContracts } = require("@lit-protocol/contracts-sdk");
const { getSessionSigs } = require("./utils");
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

    const sessionSigs = await getSessionSigs(app);

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

app.post("/createWallet", async (req, res) => {
  const contractClient = new LitContracts({
    signer: app.locals.ethersWallet,
    litNodeClient: app.locals.litNodeClient,
    network: LitNetwork.DatilDev,
    debug: true,
  });
  await contractClient.connect();

  const toSign = await createSiweMessage({
    uri: "http://localhost:3092/createWallet",
    expiration: new Date(Date.now() + 1000 * 60 * 10).toISOString(), // 10 minutes
    resources: [
      {
        resource: new LitActionResource("*"),
        ability: LIT_ABILITY.LitActionExecution,
      },
      {
        resource: new LitPKPResource("*"),
        ability: LIT_ABILITY.PKPSigning,
      },
    ],
    walletAddress: app.locals.ethersWallet.address,
    nonce: await app.locals.litNodeClient.getLatestBlockhash(),
    litNodeClient: app.locals.litNodeClient,
  });

  const authSig = await generateAuthSig({
    signer: app.locals.ethersWallet,
    toSign,
  });

  const authMethod = {
    authMethodType: AuthMethodType.EthWallet,
    accessToken: JSON.stringify(authSig),
  };

  const mintInfo = await contractClient.mintWithAuth({
    authMethod: authMethod,
    scopes: [AuthMethodScope.SignAnything],
  });

  // save to local storage
  localStorage.setItem("pkp", JSON.stringify(mintInfo.pkp));
  app.locals.pkp = mintInfo.pkp;

  res.json(mintInfo);
});

app.get("/pkp", (req, res) => {
  const pkp = localStorage.getItem("pkp");
  res.json(JSON.parse(pkp));
});

app.post("/sign", async (req, res) => {
  const { toSign } = req.body;

  const sessionSigs = await getSessionSigs(app);

  const signingResult = await app.locals.litNodeClient.pkpSign({
    pubKey: app.locals.pkp.publicKey,
    sessionSigs,
    toSign: ethers.utils.arrayify(toSign),
  });

  res.json({ signature: signingResult });
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
    process.env.LIT_PYTHON_SDK_PRIVATE_KEY,
    new ethers.providers.JsonRpcProvider(LIT_RPC.CHRONICLE_YELLOWSTONE)
  );
  // see if we can load the pkp from local storage
  const pkp = localStorage.getItem("pkp");
  if (pkp) {
    app.locals.pkp = JSON.parse(pkp);
  }
  console.log(`Server running at http://localhost:${port}`);
});
