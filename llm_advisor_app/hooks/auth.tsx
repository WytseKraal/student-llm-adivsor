"use client";
import {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";
import {
  CognitoUserPool,
  CognitoUser,
  AuthenticationDetails,
  CognitoUserSession,
  CognitoUserAttribute,
  ISignUpResult,
} from "amazon-cognito-identity-js";
import { env } from "@/environment";

// Type definitions
interface PoolData {
  UserPoolId: string;
  ClientId: string;
}

interface AuthContextType {
  user: CognitoUser | null;
  loading: boolean;
  signIn: (
    email: string,
    password: string
  ) => Promise<CognitoUserSession | { challengeName: string }>;
  signUp: (
    email: string,
    password: string,
    name: string,
    birthday: string
  ) => Promise<ISignUpResult>;
  signOut: () => void;
  getToken: () => Promise<string>;
  completeNewPasswordChallenge: (
    newPassword: string,
    name: string
  ) => Promise<CognitoUserSession>;
  challengeUser: CognitoUser | null;
  verifyStudentExists: () => Promise<boolean>;
  getUserAttributes: () => Promise<{ [key: string]: string }>;
}

interface AuthProviderProps {
  children: ReactNode;
}

const isBrowser = typeof window !== "undefined";

const poolData: PoolData = {
  UserPoolId: env.cognitoConfig.UserPoolId,
  ClientId: env.cognitoConfig.ClientId,
};

const userPool = isBrowser ? new CognitoUserPool(poolData) : null;

const API_BASE_URL = env.apiUrl;

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  challengeUser: null,
  signIn: async () => {
    throw new Error("signIn not implemented");
  },
  signUp: async () => {
    throw new Error("signUp not implemented");
  },
  signOut: () => {
    throw new Error("signOut not implemented");
  },
  getToken: async () => {
    throw new Error("getToken not implemented");
  },
  completeNewPasswordChallenge: async () => {
    throw new Error("completeNewPasswordChallenge not implemented");
  },
  verifyStudentExists: async () => {
    throw new Error("verifyStudentExists not implemented");
  },
  getUserAttributes: async () => {
    throw new Error("getUserAttributes not implemented");
  },
});

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<CognitoUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [challengeUser, setChallengeUser] = useState<CognitoUser | null>(null);

  useEffect(() => {
    if (isBrowser) {
      checkAuth();
    } else {
      setLoading(false);
    }
  }, []);

  const checkAuth = () => {
    if (!userPool) {
      setLoading(false);
      return;
    }

    const cognitoUser = userPool.getCurrentUser();
    if (cognitoUser) {
      cognitoUser.getSession(
        (err: Error | null, session: CognitoUserSession | null) => {
          if (err) {
            setUser(null);
          } else if (session && session.isValid()) {
            setUser(cognitoUser);
          } else {
            setUser(null);
          }
          setLoading(false);
        }
      );
    } else {
      setUser(null);
      setLoading(false);
    }
  };

  const getUserAttributes = async (): Promise<{ [key: string]: string }> => {
    if (!isBrowser || !userPool) {
      return Promise.reject(
        new Error("Authentication not available on server")
      );
    }

    return new Promise((resolve, reject) => {
      const cognitoUser = userPool.getCurrentUser();
      if (!cognitoUser) {
        reject(new Error("No user found"));
        return;
      }

      cognitoUser.getSession((err: Error | null) => {
        if (err) {
          reject(err);
          return;
        }

        cognitoUser.getUserAttributes((err, attributes) => {
          if (err) {
            reject(err);
            return;
          }

          if (!attributes) {
            resolve({});
            return;
          }

          const userAttributes: { [key: string]: string } = {};
          attributes.forEach((attribute) => {
            userAttributes[attribute.getName()] = attribute.getValue();
          });

          resolve(userAttributes);
        });
      });
    });
  };

  const verifyStudentExists = async (): Promise<boolean> => {
    try {
      const token = await getToken();

      const attributes = await getUserAttributes();
      const sub = attributes.sub;

      if (!sub) {
        console.error("No sub found in user attributes");
        return false;
      }

      const response = await fetch(
        `${API_BASE_URL}/student/check?student_id=${encodeURIComponent(sub)}`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error(`Error checking student: ${response.statusText}`);
      }

      const data = await response.json();
      return data.exists;
    } catch (error) {
      console.error("Error verifying student:", error);
      return false;
    }
  };

  const signIn = async (
    email: string,
    password: string
  ): Promise<CognitoUserSession | { challengeName: string }> => {
    if (!isBrowser || !userPool) {
      return Promise.reject(
        new Error("Authentication not available on server")
      );
    }

    return new Promise((resolve, reject) => {
      const authenticationDetails = new AuthenticationDetails({
        Username: email,
        Password: password,
      });

      const cognitoUser = new CognitoUser({
        Username: email,
        Pool: userPool,
      });

      cognitoUser.authenticateUser(authenticationDetails, {
        onSuccess: (result: CognitoUserSession) => {
          setUser(cognitoUser);
          setChallengeUser(null);
          resolve(result);
        },
        onFailure: (err: Error) => {
          reject(err);
        },
        newPasswordRequired: (userAttributes, requiredAttributes) => {
          delete userAttributes.email_verified;
          delete userAttributes.phone_number_verified;

          setChallengeUser(cognitoUser);
          resolve({ challengeName: "NEW_PASSWORD_REQUIRED" });
        },
      });
    });
  };

  const signUp = async (
    email: string,
    password: string,
    name: string,
    birthday: string
  ): Promise<ISignUpResult> => {
    if (!isBrowser || !userPool) {
      return Promise.reject(
        new Error("Authentication not available on server")
      );
    }

    return new Promise((resolve, reject) => {
      const attributeList = [
        new CognitoUserAttribute({
          Name: "name",
          Value: name,
        }),
        new CognitoUserAttribute({
          Name: "email",
          Value: email,
        }),
        new CognitoUserAttribute({
          Name: "birthdate",
          Value: birthday,
        }),
      ];

      userPool.signUp(email, password, attributeList, [], (err, result) => {
        if (err) {
          reject(err);
          return;
        }
        if (!result) {
          reject(new Error("Registration failed with an unknown error"));
          return;
        }
        resolve(result);
      });
    });
  };

  const completeNewPasswordChallenge = async (
    newPassword: string,
    name: string
  ): Promise<CognitoUserSession> => {
    if (!isBrowser) {
      return Promise.reject(
        new Error("Authentication not available on server")
      );
    }

    return new Promise((resolve, reject) => {
      if (!challengeUser) {
        reject(new Error("No challenge user found"));
        return;
      }

      challengeUser.completeNewPasswordChallenge(
        newPassword,
        { name },
        {
          onSuccess: (result: CognitoUserSession) => {
            setUser(challengeUser);
            setChallengeUser(null);
            resolve(result);
          },
          onFailure: (err: Error) => {
            reject(err);
          },
        }
      );
    });
  };

  const signOut = () => {
    // Check if we're in browser environment
    if (!isBrowser || !userPool) {
      return;
    }

    const cognitoUser = userPool.getCurrentUser();
    if (cognitoUser) {
      cognitoUser.signOut();
      setUser(null);
      setChallengeUser(null);
    }
  };

  const getToken = async (): Promise<string> => {
    // Check if we're in browser environment
    if (!isBrowser || !userPool) {
      return Promise.reject(
        new Error("Authentication not available on server")
      );
    }

    return new Promise((resolve, reject) => {
      const cognitoUser = userPool.getCurrentUser();
      if (cognitoUser) {
        cognitoUser.getSession(
          (err: Error | null, session: CognitoUserSession | null) => {
            if (err) {
              reject(err);
            } else if (session) {
              resolve(session.getIdToken().getJwtToken());
            } else {
              reject(new Error("No valid session"));
            }
          }
        );
      } else {
        reject(new Error("No user found"));
      }
    });
  };

  const value: AuthContextType = {
    user,
    loading,
    signIn,
    signUp,
    signOut,
    getToken,
    completeNewPasswordChallenge,
    challengeUser,
    verifyStudentExists,
    getUserAttributes,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
