import { useState, useEffect } from "react";
import { useAuth } from "./auth";
import { ICognitoUserAttributeData } from "amazon-cognito-identity-js";

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
  const { user } = useAuth();
  const [userData, setUserData] = useState<UserData>(defaultUserData);

  useEffect(() => {
    const fetchUserData = () => {
      if (!user) {
        setUserData({ ...defaultUserData, isLoading: false });
        return;
      }

      user.getUserData((err, data) => {
        if (err) {
          setUserData({
            ...defaultUserData,
            isLoading: false,
            error: err,
          });
          return;
        }

        if (!data?.UserAttributes) {
          setUserData({
            ...defaultUserData,
            isLoading: false,
            error: new Error("No user attributes found"),
          });
          return;
        }

        const attributes = data.UserAttributes.reduce(
          (acc: Record<string, string>, attr: ICognitoUserAttributeData) => {
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
      });
    };

    fetchUserData();
  }, [user]);

  return userData;
};
