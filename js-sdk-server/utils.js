const {
  LitAbility,
  LitActionResource,
  LitPKPResource,
  createSiweMessage,
  generateAuthSig,
} = require("@lit-protocol/auth-helpers");
const { LIT_ABILITY } = require("@lit-protocol/constants");

async function getSessionSigs(app) {
  if (!app.locals.ethersWallet) {
    throw new Error("No Lit auth token set");
  }

  // get session sigs
  const sessionSigs = await app.locals.litNodeClient.getSessionSigs({
    chain: "ethereum",
    expiration: new Date(Date.now() + 1000 * 60 * 10).toISOString(), // 10 minutes
    resourceAbilityRequests: [
      {
        resource: new LitActionResource("*"),
        ability: LIT_ABILITY.LitActionExecution,
      },
      {
        resource: new LitPKPResource("*"),
        ability: LIT_ABILITY.PKPSigning,
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
  return sessionSigs;
}

module.exports = {
  getSessionSigs,
};
