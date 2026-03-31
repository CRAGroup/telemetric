import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { apiClient } from "@/lib/api-client";
import { Loader2 } from "lucide-react";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  console.log('🛡️ ProtectedRoute: Component rendering', { isLoading, isAuthenticated });

  useEffect(() => {
    let mounted = true;

    const checkAuth = async () => {
      console.log('🔍 ProtectedRoute: Initial auth check...');
      try {
        const token = apiClient.getToken();
        
        if (!token) {
          console.log('🚫 ProtectedRoute: No token found');
          if (mounted) {
            setIsAuthenticated(false);
            setIsLoading(false);
          }
          return;
        }

        // Verify token is valid by calling /me endpoint
        const user = await apiClient.getMe();
        console.log('✅ ProtectedRoute: Token valid', { userId: user.user_id, role: user.role });
        
        if (mounted) {
          setIsAuthenticated(true);
          setIsLoading(false);
        }
      } catch (error) {
        console.error("❌ ProtectedRoute: Auth check error:", error);
        // Token is invalid, clear it
        apiClient.setToken(null);
        if (mounted) {
          setIsAuthenticated(false);
          setIsLoading(false);
        }
      }
    };

    checkAuth();

    return () => {
      console.log('🧹 ProtectedRoute: Cleaning up');
      mounted = false;
    };
  }, []);

  if (isLoading) {
    console.log('⏳ ProtectedRoute: Showing loading state');
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!isAuthenticated) {
    console.log('🚫 ProtectedRoute: Not authenticated, redirecting to login');
    return <Navigate to="/login" replace />;
  }

  console.log('✅ ProtectedRoute: Authenticated, rendering children');
  return <>{children}</>;
}
