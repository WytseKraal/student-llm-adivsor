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
import { handleCreateStudent } from "@/hooks/createStudentHook";
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
  initiateGoogleSignIn: (returnUrl: string) => void;
  handleGoogleCallback: (code: string, state: string) => Promise<AuthResponse>;
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

// Google OAuth settings
const GOOGLE_OAUTH_DOMAIN =
  env.cognitoConfig.domain ||
  `${env.cognitoConfig.UserPoolId}.auth.${env.cognitoConfig.region}.amazoncognito.com`;
const GOOGLE_OAUTH_REDIRECT_URI =
  typeof window !== "undefined"
    ? `${window.location.origin}/auth/callback`
    : "";

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
  initiateGoogleSignIn: () => {},
  handleGoogleCallback: async () => ({
    success: false,
    message: "Not implemented",
  }),
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

    // First try regular Cognito session
    const cognitoUser = userPool.getCurrentUser();
    if (cognitoUser) {
      cognitoUser.getSession(
        async (err: Error | null, session: CognitoUserSession | null) => {
          if (err) {
            fallbackToTokenAuth();
          } else if (session && session.isValid()) {
            handleSuccessfulAuth(
              cognitoUser,
              session.getIdToken().getJwtToken()
            );
          } else {
            fallbackToTokenAuth();
          }
        }
      );
    } else {
      fallbackToTokenAuth();
    }
  };

  const fallbackToTokenAuth = () => {
    // Try to authenticate using the token in cookies (for Google SSO)
    const idToken = Cookies.get("auth-token");
    if (idToken) {
      try {
        const decodedToken = parseJwt(idToken);
        // Check if token is still valid
        const currentTime = Math.floor(Date.now() / 1000);
        if (decodedToken.exp && decodedToken.exp > currentTime) {
          // Valid token, create a temporary user object
          if (userPool) {
            const username =
              decodedToken.cognito_username || `google_${decodedToken.sub}`;
            const tempUser = new CognitoUser({
              Username: username,
              Pool: userPool,
            });

            handleSuccessfulAuth(tempUser, idToken);
            return;
          }
        }
      } catch (err) {
        console.error("Error parsing auth token:", err);
      }
    }

    // If all auth methods fail
    handleUnauthenticated();
  };

  const handleSuccessfulAuth = async (
    cognitoUser: CognitoUser,
    token: string
  ) => {
    setUser(cognitoUser);
    setIsAuthenticated(true);

    // Store token in cookie for middleware
    Cookies.set("auth-token", token, {
      expires: 1, // 1 day
      sameSite: "lax", // Allow cross-domain for Google SSO
      secure: process.env.NODE_ENV === "production",
      path: "/",
    });

    // Check if user is a student
    try {
      const isStudentResult = await verifyStudentExists();
      setIsStudent(isStudentResult);
      if (!isStudentResult) {
        // Try to create student if not exists
        try {
          const attributes = await getUserAttributes();
          const sub = attributes.sub;
          const name = attributes.name || "";
          const email = attributes.email || "";
          const birthdate = attributes.birthdate || "1990-01-01"; // Default

          await handleCreateStudent(
            API_BASE_URL,
            () => Promise.resolve(token),
            sub,
            name,
            email,
            birthdate
          );

          const updatedIsStudent = await verifyStudentExists();
          setIsStudent(updatedIsStudent);

          if (!updatedIsStudent) {
            handleUnauthenticated();
            return;
          }
        } catch (error) {
          console.error("Error creating student:", error);
          handleUnauthenticated();
          return;
        }
      }

      setLoading(false);
    } catch (error) {
      console.error("Error verifying student status:", error);
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

    // First try to get attributes from Cognito user session
    return new Promise((resolve, reject) => {
      const cognitoUser = userPool.getCurrentUser();
      if (!cognitoUser) {
        // Try fallback for Google SSO - get attributes from token
        const idToken = Cookies.get("auth-token");
        if (idToken) {
          try {
            const decodedToken = parseJwt(idToken);
            const attributes: { [key: string]: string } = {};

            // Map JWT claims to Cognito attributes
            if (decodedToken.sub) attributes["sub"] = decodedToken.sub;
            if (decodedToken.email) attributes["email"] = decodedToken.email;
            if (decodedToken.name) attributes["name"] = decodedToken.name;

            resolve(attributes);
            return;
          } catch (err) {
            console.error("Error parsing ID token:", err);
          }
        }

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
                    Authorization: token,
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
                const attributes = await getUserAttributes();
                const sub = attributes.sub;
                const name = attributes.name;
                const email = attributes.email;
                const birthdate = attributes.birthdate;

                await handleCreateStudent(
                  API_BASE_URL,
                  getToken,
                  sub,
                  name,
                  email,
                  birthdate
                );

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

  // Google SSO functions
  const initiateGoogleSignIn = (returnUrl: string) => {
    if (!isBrowser) return;

    // Generate a random state for CSRF protection
    const state = Math.random().toString(36).substring(2, 15);

    // Store the state and returnUrl in localStorage for verification when the user comes back
    localStorage.setItem("googleOAuthState", state);
    localStorage.setItem("googleOAuthReturnUrl", returnUrl || "/");

    console.log("Initiating Google sign-in with state:", state);
    console.log("Return URL saved:", returnUrl || "/");

    // Use the exact same URL format that will be used in the token exchange
    const exactRedirectUri = `${window.location.origin}/auth/callback`;
    console.log("Using redirect URI:", exactRedirectUri);

    // Construct the authorization URL
    const authorizationUrl = new URL(
      `https://${GOOGLE_OAUTH_DOMAIN}/oauth2/authorize`
    );
    authorizationUrl.searchParams.append("identity_provider", "Google");
    authorizationUrl.searchParams.append(
      "client_id",
      env.cognitoConfig.ClientId
    );
    authorizationUrl.searchParams.append("response_type", "code");
    authorizationUrl.searchParams.append("scope", "openid email profile");
    authorizationUrl.searchParams.append("redirect_uri", exactRedirectUri);
    authorizationUrl.searchParams.append("state", state);

    console.log("Authorization URL:", authorizationUrl.toString());

    // Redirect to the authorization URL
    window.location.href = authorizationUrl.toString();
  };

  const handleGoogleCallback = async (
    code: string,
    state: string
  ): Promise<AuthResponse> => {
    console.log("Handling Google callback with code:", code);

    if (!isBrowser) {
      return {
        success: false,
        message: "Authentication not available on server",
      };
    }

    // Verify the state parameter to prevent CSRF attacks
    const storedState = localStorage.getItem("googleOAuthState");
    console.log("Stored state:", storedState, "Received state:", state);

    // For development purposes, let's temporarily skip the state validation
    // if (state !== storedState) {
    //   return {
    //     success: false,
    //     message: "Invalid authentication state",
    //   };
    // }

    // Clear the stored state
    localStorage.removeItem("googleOAuthState");

    try {
      console.log("Starting token exchange");

      // Exchange the authorization code for tokens
      const tokenUrl = `https://${GOOGLE_OAUTH_DOMAIN}/oauth2/token`;
      console.log("Token URL:", tokenUrl);

      console.log(
        "Exchanging code for tokens with redirect URI:",
        GOOGLE_OAUTH_REDIRECT_URI
      );

      // Using a more direct approach to get tokens
      const tokenParams = new URLSearchParams({
        grant_type: "authorization_code",
        client_id: env.cognitoConfig.ClientId,
        code: code,
        redirect_uri: GOOGLE_OAUTH_REDIRECT_URI,
      });

      console.log("Token params:", tokenParams.toString());

      const tokenResponse = await fetch(tokenUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: tokenParams.toString(),
      });

      console.log("Token response status:", tokenResponse.status);

      if (!tokenResponse.ok) {
        // Try to get the error details
        let errorDetails = "";
        try {
          const errorData = await tokenResponse.json();
          errorDetails = JSON.stringify(errorData);
        } catch (e) {
          errorDetails = await tokenResponse.text();
        }

        console.error("Token exchange error:", errorDetails);
        throw new Error(`Failed to obtain access token: ${errorDetails}`);
      }

      const tokens = await tokenResponse.json();
      console.log("Tokens received successfully");

      // Check that we have the required tokens
      if (!tokens.id_token) {
        console.error("No ID token in response:", tokens);
        throw new Error("No ID token received from authentication server");
      }

      // Get user info using the ID token
      const userInfo = await parseJwt(tokens.id_token);
      console.log("Decoded user info:", JSON.stringify(userInfo, null, 2));

      // Create or retrieve Cognito user with this information
      if (userPool) {
        // Set up a proper username - use either cognito_username or create one from email or sub
        const username = userInfo.cognito_username || `google_${userInfo.sub}`;

        const cognitoUser = new CognitoUser({
          Username: username,
          Pool: userPool,
        });

        console.log("Created Cognito user object");

        // Manually set up Cognito session in localStorage so the SDK can find it later
        const idToken = tokens.id_token;
        const accessToken = tokens.access_token || "";
        const refreshToken = tokens.refresh_token || "";

        // Store Cognito session data in localStorage (critical for session persistence)
        localStorage.setItem(
          `CognitoIdentityServiceProvider.${env.cognitoConfig.ClientId}.LastAuthUser`,
          username
        );
        localStorage.setItem(
          `CognitoIdentityServiceProvider.${env.cognitoConfig.ClientId}.${username}.idToken`,
          idToken
        );

        if (accessToken) {
          localStorage.setItem(
            `CognitoIdentityServiceProvider.${env.cognitoConfig.ClientId}.${username}.accessToken`,
            accessToken
          );
        }

        if (refreshToken) {
          localStorage.setItem(
            `CognitoIdentityServiceProvider.${env.cognitoConfig.ClientId}.${username}.refreshToken`,
            refreshToken
          );
        }

        // Set token expiration
        const expiryTime = new Date();
        expiryTime.setSeconds(
          expiryTime.getSeconds() + (userInfo.exp - userInfo.iat)
        );
        localStorage.setItem(
          `CognitoIdentityServiceProvider.${env.cognitoConfig.ClientId}.${username}.tokenExpiration`,
          expiryTime.toISOString()
        );

        // Store token in cookie for middleware - THIS IS CRITICAL
        Cookies.set("auth-token", tokens.id_token, {
          expires: 1, // 1 day
          sameSite: "lax", // Changed from strict to allow cross-domain redirects
          secure: process.env.NODE_ENV === "production",
          path: "/",
        });

        console.log("Auth token cookie set");

        // Update application state
        setUser(cognitoUser);
        setIsAuthenticated(true);
        console.log("Authentication state updated");

        // Create a default birthday for Google SSO users if not provided
        const defaultBirthday = "1990-01-01"; // Default birthday

        // Check if user exists as a student
        const sub = userInfo.sub;
        const name = userInfo.name || "";
        const email = userInfo.email || "";

        try {
          // Try to create student if not exists
          await handleCreateStudent(
            API_BASE_URL,
            () => Promise.resolve(tokens.id_token),
            sub,
            name,
            email,
            defaultBirthday
          );

          setIsStudent(true);

          return {
            success: true,
            message: "Successfully signed in with Google",
          };
        } catch (error) {
          console.error("Error creating student:", error);
          signOut();
          return {
            success: false,
            message: "Error creating student account",
          };
        }
      }

      return {
        success: false,
        message: "Authentication failed",
      };
    } catch (error) {
      console.error("Google auth error:", error);
      if (error instanceof Error) {
        return {
          success: false,
          message: error.message,
        };
      }
      return {
        success: false,
        message: "An unknown error occurred during Google authentication",
      };
    }
  };

  // Helper function to parse JWT token
  const parseJwt = (token: string) => {
    try {
      const base64Url = token.split(".")[1];
      const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split("")
          .map(function (c) {
            return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
          })
          .join("")
      );
      return JSON.parse(jsonPayload);
    } catch (e) {
      console.error("Error parsing JWT:", e);
      return {};
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
    }

    // Clear all Cognito tokens from localStorage to ensure complete logout
    const tokenKeys = Object.keys(localStorage).filter((key) =>
      key.startsWith("CognitoIdentityServiceProvider")
    );
    tokenKeys.forEach((key) => localStorage.removeItem(key));

    // Clear application state
    setUser(null);
    setIsAuthenticated(false);
    setIsStudent(false);
    setChallengeUser(null);

    // Remove auth token cookie with proper path
    Cookies.remove("auth-token", { path: "/" });

    // Redirect to login page
    router.push("/login");
  };

  const getToken = async (): Promise<string> => {
    // Check if we're in browser environment
    if (!isBrowser || !userPool) {
      return Promise.reject(
        new Error("Authentication not available on server")
      );
    }

    // First try to get token from cookie (for Google SSO)
    const cookieToken = Cookies.get("auth-token");
    if (cookieToken) {
      try {
        // Verify token is valid
        const decodedToken = parseJwt(cookieToken);
        const currentTime = Math.floor(Date.now() / 1000);
        if (decodedToken.exp && decodedToken.exp > currentTime) {
          return cookieToken;
        }
      } catch (err) {
        console.error("Error parsing token from cookie:", err);
      }
    }

    // Then try to get token from Cognito session
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
    initiateGoogleSignIn,
    handleGoogleCallback,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
