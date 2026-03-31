import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Outlet, useLocation } from "react-router-dom";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import Tracking from "./pages/Tracking";
import Vehicles from "./pages/Vehicles";
import VehicleTypes from "./pages/VehicleTypes";
import AddVehicle from "./pages/AddVehicle";
import EditVehicle from "./pages/EditVehicle";
import Drivers from "./pages/Drivers";
import AddDriver from "./pages/AddDriver";
import DriverProfile from "./pages/DriverProfile";
import DriverPerformance from "./pages/DriverPerformance";
import DriverSchedules from "./pages/DriverSchedules";
import EditDriver from "./pages/EditDriver";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Settings from "./pages/Settings";
import CameraMonitoring from "./pages/CameraMonitoring";
import Maintenance from "./pages/Maintenance";
import Reports from "./pages/Reports";
import Notifications from "./pages/Notifications";
import Profile from "./pages/Profile";
import { NavigationSidebar } from "@/components/NavigationSidebar";
import { Header } from "@/components/Header";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { ResizablePanel, ResizablePanelGroup, ResizableHandle } from "@/components/ui/resizable";
import { SecondarySidebar } from "@/components/SecondarySidebar";
import { useEffect, useState } from "react";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (replaces cacheTime in newer versions)
    },
  },
});

const AppLayout = () => {
  const location = useLocation();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const showSecondarySidebar = 
  location.pathname === "/tracking";

  const toggleSidebarCollapse = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <Header />
      
      {/* Main Content Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className={`${isSidebarCollapsed ? 'w-16' : 'w-64'} flex flex-col py-2 space-y-4 bg-sidebar border-r transition-all duration-300`}>
          <div className="flex-1">
            <NavigationSidebar 
              isCollapsed={isSidebarCollapsed} 
              onToggleCollapse={toggleSidebarCollapse}
            />
          </div>
        </aside>

        {/* Content Area */}
        <ResizablePanelGroup direction="horizontal" className="flex-1">
          {showSecondarySidebar && (
            <>
              <ResizablePanel defaultSize={20} minSize={15} maxSize={30}>
                <SecondarySidebar />
              </ResizablePanel>
              <ResizableHandle withHandle />
            </>
          )}
          <ResizablePanel>
            <main className="flex-1 overflow-y-auto h-full bg-background">
              <Outlet />
            </main>
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>
    </div>
  );
};

const App = () => {
  // Note: Auth state management removed - handled by API client
  // Admin settings prefetch removed - handled by useAdminSettings hook

  return (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          
          {/* Protected routes */}
          <Route element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }>
            <Route path="/" element={<Index />} />
            <Route path="/tracking" element={<Tracking />} />
            <Route path="/vehicles" element={<Vehicles />} />
            <Route path="/vehicles/add" element={<AddVehicle />} />
            <Route path="/vehicles/edit/:id" element={<EditVehicle />} />
            <Route path="/vehicle-types" element={<VehicleTypes />} />
            <Route path="/drivers" element={<Drivers />} />
            <Route path="/drivers/add" element={<AddDriver />} />
            <Route path="/drivers/edit/:id" element={<EditDriver />} />
            <Route path="/driver-profile/:id" element={<DriverProfile />} />
            <Route path="/drivers/performance" element={<DriverPerformance />} />
            <Route path="/drivers/schedules" element={<DriverSchedules />} />
            <Route path="/camera-monitoring" element={<CameraMonitoring />} />
            <Route path="/maintenance" element={<Maintenance />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/notifications" element={<Notifications />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
          
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
)};

export default App;