interface Environment {
  apiUrl: string;
  cognitoConfig: {
    UserPoolId: string;
    ClientId: string;
    region: string;
    domain: string;
  };
  corsOrigin: string;
}

const dev: Environment = {
  apiUrl: "http://localhost:3001",
  cognitoConfig: {
    UserPoolId: "eu-north-1_YxTYEALZB", // Your dev user pool
    ClientId: "1jlrpensqegf36fbaekvrr86rk",
    region: "eu-north-1",
    domain: "eu-north-1yxtyealzb.auth.eu-north-1.amazoncognito.com",
  },
  corsOrigin: "http://localhost:3000",
};

const prod: Environment = {
  apiUrl: "https://26jbdrdk5g.execute-api.eu-north-1.amazonaws.com/Prod",
  cognitoConfig: {
    UserPoolId: "eu-north-1_YxTYEALZB", // Your prod user pool
    ClientId: "1jlrpensqegf36fbaekvrr86rk",
    region: "eu-north-1",
    domain: "eu-north-1yxtyealzb.auth.eu-north-1.amazoncognito.com",
  },
  corsOrigin: "https://smartstudentadvisor.nl",
};

const getEnvironment = (): Environment => {
  if (typeof window !== "undefined") {
    const isProd = window.location.origin.includes("smart");
    return isProd ? prod : dev;
  }
  return process.env.NEXT_PUBLIC_ENV === "production" ? prod : dev;
};

export const env = getEnvironment();
