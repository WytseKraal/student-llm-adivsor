import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";

// Define public routes that don't require authentication
const publicRoutes = [
  "/",
  "/login",
  "/register",
  "/forgot-password", // NOT YET IMPLEMENTED
  "/reset-password", // NOT YET IMPLEMENTED
  "/auth/callback", // Add the OAuth callback route here
];

export default async function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname;
  const isPublicRoute = publicRoutes.some(
    (route) => path === route || path.startsWith(`${route}/`)
  );

  const token = request.cookies.get("auth-token")?.value;
  const isAuthenticated = !!token;

  // Special handling for OAuth callback - always allow this route
  if (path === "/auth/callback") {
    return NextResponse.next();
  }

  if (!isPublicRoute && !isAuthenticated) {
    const url = new URL("/login", request.url);
    url.searchParams.set("returnUrl", path);
    return NextResponse.redirect(url);
  }

  if (isAuthenticated && (path === "/login" || path === "/register")) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  return NextResponse.next();
}

// Configure middleware to run on specific paths
export const config = {
  matcher: [
    /**
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     * - api routes that handle their own authentication
     */
    "/((?!_next/static|_next/image|favicon.ico|public|api/auth).*)",
  ],
};
