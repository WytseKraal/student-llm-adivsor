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
import { useRouter, usePathname } from "next/navigation";
import Cookies from "js-cookie";

// Type definitions
interface PoolData {
  UserPoolId: string;
  ClientId: string;
}

interface AuthContextType {
  user: CognitoUser | null;
  loading: boolean;
  isAuthenticated: boolean;
  isStudent: boolean;
  signIn: (email: string, password: string) => Promise<AuthResponse>;
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
  getUserAttributes: () => Promise<{ [key: string]: string }>;
}

interface AuthResponse {
  success: boolean;
  message: string;
  requiresNewPassword?: boolean;
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
  isAuthenticated: false,
  isStudent: false,
  signIn: async () => ({ success: false, message: "Not implemented" }),
  signUp: async () => {
    throw new Error("signUp not implemented");
  },
  signOut: () => {},
  getToken: async () => {
    throw new Error("getToken not implemented");
  },
  completeNewPasswordChallenge: async () => {
    throw new Error("completeNewPasswordChallenge not implemented");
  },
  getUserAttributes: async () => ({}),
});

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<CognitoUser | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isStudent, setIsStudent] = useState(false);
  const [loading, setLoading] = useState(true);
  const [challengeUser, setChallengeUser] = useState<CognitoUser | null>(null);

  const router = useRouter();
  const pathname = usePathname();

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
        async (err: Error | null, session: CognitoUserSession | null) => {
          if (err) {
            handleUnauthenticated();
          } else if (session && session.isValid()) {
            setUser(cognitoUser);
            setIsAuthenticated(true);

            // Store token in cookie for middleware
            const token = session.getIdToken().getJwtToken();
            Cookies.set("auth-token", token, {
              expires: 1, // 1 day
              sameSite: "strict",
              secure: process.env.NODE_ENV === "production",
            });

            // Check if user is a student
            try {
              const isStudentResult = await verifyStudentExists();
              setIsStudent(isStudentResult);
              if (!isStudentResult) {
                // If not a student, log them out
                signOut();
                return;
              }
            } catch (error) {
              console.error("Error verifying student status:", error);
              signOut();
              return;
            }

            setLoading(false);
          } else {
            handleUnauthenticated();
          }
        }
      );
    } else {
      handleUnauthenticated();
    }
  };

  const handleUnauthenticated = () => {
    setUser(null);
    setIsAuthenticated(false);
    setIsStudent(false);
    Cookies.remove("auth-token");
    setLoading(false);
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
      const cognitoUser = userPool?.getCurrentUser();
      if (!cognitoUser) {
        return false;
      }

      return new Promise((resolve, reject) => {
        cognitoUser.getSession(
          async (err: Error | null, session: CognitoUserSession | null) => {
            if (err || !session) {
              resolve(false);
              return;
            }

            const token = session.getIdToken().getJwtToken();

            try {
              const attributes = await getUserAttributes();
              const sub = attributes.sub;

              if (!sub) {
                console.error("No sub found in user attributes");
                resolve(false);
                return;
              }

              const response = await fetch(
                `${API_BASE_URL}/student/check?student_id=${encodeURIComponent(
                  sub
                )}`,
                {
                  method: "GET",
                  headers: {
                    Authorization: `Bearer ${token}`,
                  },
                }
              );

              if (!response.ok) {
                throw new Error(
                  `Error checking student: ${response.statusText}`
                );
              }

              const data = await response.json();
              resolve(data.exists);
            } catch (error) {
              console.error("Error verifying student:", error);
              resolve(false);
            }
          }
        );
      });
    } catch (error) {
      console.error("Error verifying student:", error);
      return false;
    }
  };

  const signIn = async (
    email: string,
    password: string
  ): Promise<AuthResponse> => {
    if (!isBrowser || !userPool) {
      return {
        success: false,
        message: "Authentication not available on server",
      };
    }

    try {
      const authenticationDetails = new AuthenticationDetails({
        Username: email,
        Password: password,
      });

      const cognitoUser = new CognitoUser({
        Username: email,
        Pool: userPool,
      });

      return new Promise((resolve) => {
        cognitoUser.authenticateUser(authenticationDetails, {
          onSuccess: async (result: CognitoUserSession) => {
            setUser(cognitoUser);
            setChallengeUser(null);
            setIsAuthenticated(true);

            // Store token in cookie for middleware
            const token = result.getIdToken().getJwtToken();
            Cookies.set("auth-token", token, {
              expires: 1, // 1 day
              sameSite: "strict",
              secure: process.env.NODE_ENV === "production",
            });

            // Verify if user is a student
            try {
              const isStudentResult = await verifyStudentExists();
              setIsStudent(isStudentResult);

              if (!isStudentResult) {
                signOut();
                resolve({
                  success: false,
                  message: "Your account is not registered as a student",
                });
                return;
              }

              resolve({
                success: true,
                message: "Successfully signed in",
              });
            } catch (error) {
              console.error("Error verifying student status:", error);
              signOut();
              resolve({
                success: false,
                message: "Error verifying student status",
              });
            }
          },
          onFailure: (err: Error) => {
            resolve({
              success: false,
              message: err.message,
            });
          },
          newPasswordRequired: () => {
            setChallengeUser(cognitoUser);
            resolve({
              success: false,
              message: "Please set a new password",
              requiresNewPassword: true,
            });
          },
        });
      });
    } catch (error) {
      if (error instanceof Error) {
        return {
          success: false,
          message: error.message,
        };
      }
      return {
        success: false,
        message: "An unknown error occurred",
      };
    }
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
          onSuccess: async (result: CognitoUserSession) => {
            setUser(challengeUser);
            setChallengeUser(null);
            setIsAuthenticated(true);

            // Store token in cookie for middleware
            const token = result.getIdToken().getJwtToken();
            Cookies.set("auth-token", token, {
              expires: 1, // 1 day
              sameSite: "strict",
              secure: process.env.NODE_ENV === "production",
            });

            // Verify if user is a student
            try {
              const isStudentResult = await verifyStudentExists();
              setIsStudent(isStudentResult);

              if (!isStudentResult) {
                signOut();
                reject(
                  new Error("Your account is not registered as a student")
                );
                return;
              }

              resolve(result);
            } catch (error) {
              console.error("Error verifying student status:", error);
              signOut();
              reject(new Error("Error verifying student status"));
            }
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
      setIsAuthenticated(false);
      setIsStudent(false);
      setChallengeUser(null);

      // Remove auth token cookie
      Cookies.remove("auth-token");

      // Redirect to login page
      router.push("/login");
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
    isAuthenticated,
    isStudent,
    signIn,
    signUp,
    signOut,
    getToken,
    completeNewPasswordChallenge,
    getUserAttributes,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
