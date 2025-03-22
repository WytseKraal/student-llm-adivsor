//#############################################
// File: userDataHook.tsx
// returns Cogito user information
//#############################################
import { useState, useEffect } from "react";
import { useAuth } from "./auth";
import { ICognitoUserAttributeData } from "amazon-cognito-identity-js";
import Cookies from "js-cookie";

interface UserData {
  userEmail: string;
  userName: string;
  phoneNumber: string;
  emailVerified: boolean;
  phoneVerified: boolean;
  sub: string;
  isLoading: boolean;
  error: Error | null;
}

const defaultUserData: UserData = {
  userEmail: "",
  userName: "",
  phoneNumber: "",
  emailVerified: false,
  phoneVerified: false,
  sub: "",
  isLoading: true,
  error: null,
};

export const useUserData = (): UserData => {
  const { user, isAuthenticated } = useAuth();
  const [userData, setUserData] = useState<UserData>(defaultUserData);

  useEffect(() => {
    const fetchUserData = async () => {
      console.log(
        "Fetching user data, authenticated:",
        isAuthenticated,
        "user:",
        !!user
      );

      // If not authenticated, return default data
      if (!isAuthenticated) {
        setUserData({ ...defaultUserData, isLoading: false });
        return;
      }

      try {
        // Method 1: Try to get data using Cognito user object (for regular Cognito users)
        if (user) {
          user.getUserData((err, data) => {
            if (err) {
              console.error("Error getting user data from Cognito:", err);
              // Don't set error state here - try the token method next
              tryTokenMethod();
              return;
            }

            if (!data?.UserAttributes) {
              console.warn("No user attributes found in Cognito user data");
              tryTokenMethod();
              return;
            }

            const attributes = data.UserAttributes.reduce(
              (
                acc: Record<string, string>,
                attr: ICognitoUserAttributeData
              ) => {
                acc[attr.Name] = attr.Value;
                return acc;
              },
              {}
            );

            setUserData({
              userEmail: attributes["email"] || "",
              userName: attributes["name"] || "",
              phoneNumber: attributes["phone_number"] || "",
              emailVerified: attributes["email_verified"] === "true",
              phoneVerified: attributes["phone_number_verified"] === "true",
              sub: attributes["sub"] || "",
              isLoading: false,
              error: null,
            });

            console.log("Successfully retrieved user data from Cognito");
          });
        } else {
          // No Cognito user object, try token method
          tryTokenMethod();
        }
      } catch (error) {
        console.error("Exception in fetchUserData:", error);
        tryTokenMethod();
      }
    };

    // Method 2: Try to get data from ID token (for Google SSO users)
    const tryTokenMethod = () => {
      try {
        console.log("Trying to get user data from auth token");
        const idToken = Cookies.get("auth-token");

        if (!idToken) {
          console.error("No auth token found in cookies");
          setUserData({
            ...defaultUserData,
            isLoading: false,
            error: new Error("No authentication token found"),
          });
          return;
        }

        // Parse the JWT token
        const tokenData = parseJwt(idToken);
        console.log("Parsed token data:", tokenData);

        setUserData({
          userEmail: tokenData.email || "",
          userName: tokenData.name || "",
          phoneNumber: tokenData.phone_number || "",
          emailVerified: tokenData.email_verified === true,
          phoneVerified: tokenData.phone_number_verified === true,
          sub: tokenData.sub || "",
          isLoading: false,
          error: null,
        });

        console.log("Successfully retrieved user data from token");
      } catch (error) {
        console.error("Error getting user data from token:", error);
        setUserData({
          ...defaultUserData,
          isLoading: false,
          error:
            error instanceof Error
              ? error
              : new Error("Unknown error getting user data"),
        });
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
        throw new Error("Invalid token format");
      }
    };

    fetchUserData();
  }, [user, isAuthenticated]);

  return userData;
};
