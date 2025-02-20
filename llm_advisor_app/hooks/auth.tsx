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
  signOut: () => void;
  getToken: () => Promise<string>;
  completeNewPasswordChallenge: (
    newPassword: string,
    name: string
  ) => Promise<CognitoUserSession>;
  challengeUser: CognitoUser | null;
}

interface AuthProviderProps {
  children: ReactNode;
}

// Pool configuration
const poolData: PoolData = {
  UserPoolId: env.cognitoConfig.UserPoolId,
  ClientId: env.cognitoConfig.ClientId,
};

const userPool = new CognitoUserPool(poolData);

// Create context with default values
const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  challengeUser: null,
  signIn: async () => {
    throw new Error("signIn not implemented");
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
});

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<CognitoUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [challengeUser, setChallengeUser] = useState<CognitoUser | null>(null);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = () => {
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

  const signIn = async (
    email: string,
    password: string
  ): Promise<CognitoUserSession | { challengeName: string }> => {
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
          // Delete sensitive attributes before passing to completeNewPasswordChallenge
          delete userAttributes.email_verified;
          delete userAttributes.phone_number_verified;

          setChallengeUser(cognitoUser);
          resolve({ challengeName: "NEW_PASSWORD_REQUIRED" });
        },
      });
    });
  };

  const completeNewPasswordChallenge = async (
    newPassword: string,
    name: string
  ): Promise<CognitoUserSession> => {
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
    const cognitoUser = userPool.getCurrentUser();
    if (cognitoUser) {
      cognitoUser.signOut();
      setUser(null);
      setChallengeUser(null);
    }
  };

  const getToken = async (): Promise<string> => {
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
    signOut,
    getToken,
    completeNewPasswordChallenge,
    challengeUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
