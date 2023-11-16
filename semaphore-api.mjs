import fetch from "node-fetch";

const semaphoreUrl = 'semaphore.cansk.net'

function parseCookies(response) {
  const raw = response.headers.raw()["set-cookie"];
  return raw
    .map((entry) => {
      const parts = entry.split(";");
      const cookiePart = parts[0];
      return cookiePart;
    })
    .join(";");
}

let loginToken = null;

const getOrCreateToken = async (parsedCookies, validTokens) => {
  if (!validTokens.length) {
    const newTokenResponse = await fetch(
      `https://${semaphoreUrl}/api/user/tokens`,
      {
        method: "POST",
        headers: {
          ContentType: "application/json",
          Accept: "application/json",
          Cookie: parsedCookies,
        },
      }
    );
    console.log(newTokenResponse);

    const newTokensResponse = await fetch(
      `https://${semaphoreUrl}/api/user/tokens`,
      {
        method: "GET",
        headers: {
          ContentType: "application/json",
          Accept: "application/json",
          Cookie: parsedCookies,
        },
      }
    );

    const data = await newTokensResponse.json();

    const newValidTokens = data.filter((token) => !token.expired);

    return newValidTokens[0];
  }
  return validTokens[0];
};

const loginAndGetTokens = async () => {
  const loginResponse = await fetch(
    `https://${semaphoreUrl}/api/auth/login`,
    {
      method: "POST",
      headers: {
        ContentType: "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        auth: "teamcity",
        password: "ZR5esOuSXDgLbVsEPRLj",
      }),
    }
  );

  if (loginResponse.status !== 204) {
    console.log("login failed");
    return {
      success: false,
      tokens: [],
      cookies: null,
    };
  }

  const parsedCookies = parseCookies(loginResponse);

  const tokensResponse = await fetch(
    `https://${semaphoreUrl}/api/user/tokens`,
    {
      method: "GET",
      headers: {
        ContentType: "application/json",
        Accept: "application/json",
        Cookie: parsedCookies,
      },
    }
  );

  if (tokensResponse.status !== 200) {
    console.log("failed to retrieve tokens");
    return;
  }

  const tokens = await tokensResponse.json();

  return {
    success: true,
    tokens: tokens,
    cookies: parsedCookies,
  };
};

const login = async () => {
  try {
    if (loginToken) {
      return;
    }
    const tokensData = await loginAndGetTokens();

    if (!tokensData.success) {
      return;
    }

    const cookies = tokensData.cookies;
    const validTokens = tokensData.tokens.filter((token) => !token.expired);
    loginToken = await getOrCreateToken(cookies, validTokens);
  } catch (e) {
    console.log(e);
  }
};

const Semaphore = {
  startTask: async (project, task) => {
    await login();

    const startTaskResponse = await fetch(
      `https://${semaphoreUrl}/api/project/${project}/tasks`,
      {
        method: "POST",
        headers: {
          ContentType: "application/json",
          Accept: "application/json",
          Authorization: `Bearer ${loginToken.id}`,
        },
        body: JSON.stringify({
          template_id: task
        }),
      }
    );

    if (startTaskResponse.status !== 201) {
      console.log("failed to start task");
      console.log(startTaskResponse);
      return;
    }
    
    else {
      console.log("task started");
    }
  },
  // these IDs and names are specific to my Semaphore project, hardcoded but with names to make 
  // deployment scripts more readable
  projects: {
    HomeNetwork: 1,
  },
  tasks: {
    DeployCertbotCloudflare: 7,
    DeployDockerRegistry: 2,
    DeployDNS: 16,
    DeployHomeIngress: 4,
    DeployPiholePrimary: 14,
    DeployPiholeSecondary: 15,
    DeployPlexMediaServer: 17,
    DeployMonitoringServer: 19,
    DeployMonitoringDefault: 21,
    DeployMonitoringEnviro: 20,
    DeployTeamcity: 12,
    DeployTimescaleDB: 5,
    DeployTransmission: 18
  },
};

export default Semaphore;
