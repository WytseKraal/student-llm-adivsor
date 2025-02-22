interface Environment {
  apiUrl: string;
  cognitoConfig: {
    UserPoolId: string;
    ClientId: string;
    region: string;
  };
  corsOrigin: string;
}

const dev: Environment = {
  apiUrl: "http://localhost:3001",
  cognitoConfig: {
    UserPoolId: "eu-north-1_cXdMnsSwH", // Your dev user pool
    ClientId: "29sfsu3nvhqfsjjnimcgh9ejab",
    region: "eu-north-1",
  },
  corsOrigin: "http://localhost:3000",
};

const prod: Environment = {
  apiUrl: "https://26jbdrdk5g.execute-api.eu-north-1.amazonaws.com/Prod",
  cognitoConfig: {
    UserPoolId: "eu-north-1_cXdMnsSwH", // Your prod user pool
    ClientId: "29sfsu3nvhqfsjjnimcgh9ejab",
    region: "eu-north-1",
  },
  corsOrigin: "http://13.53.152.71",
};

const getEnvironment = (): Environment => {
  if (typeof window !== "undefined") {
    const isProd = window.location.origin.includes("13.53");
    return isProd ? prod : dev;
  }
  return process.env.NEXT_PUBLIC_ENV === "production" ? prod : dev;
};

export const env = getEnvironment();
