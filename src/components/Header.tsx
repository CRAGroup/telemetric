import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { 
  Bell, 
  AlertTriangle, 
  Search, 
  ChevronDown, 
  MoreVertical,
  User,
  LogOut,
  Settings,
  Circle,
  MapPin,
  Clock,
  Truck
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/components/ui/use-toast";
import { CompanyLogo } from "./CompanyLogo";

interface OnlineDriver {
  id: string;
  name: string;
  vehicle: string;
  status: "driving" | "break" | "loading" | "idle";
  location: string;
  lastSeen: string;
  avatar?: string;
}

// Mock online drivers data
const mockOnlineDrivers: OnlineDriver[] = [
  {
    id: "1",
    name: "John Kamau",
    vehicle: "KCA 456T",
    status: "driving",
    location: "Machakos - Mombasa Highway",
    lastSeen: "Active now",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=john"
  },
  {
    id: "2", 
    name: "Peter Kiprotich",
    vehicle: "KBZ 789M",
    status: "break",
    location: "Mtito Andei Rest Stop",
    lastSeen: "2 min ago",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=peter"
  },
  {
    id: "3",
    name: "Mary Wanjiku",
    vehicle: "KCB 234L", 
    status: "loading",
    location: "Mombasa Port",
    lastSeen: "5 min ago",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=mary"
  },
  {
    id: "4",
    name: "David Ochieng",
    vehicle: "KDA 567P",
    status: "idle",
    location: "Nairobi Depot",
    lastSeen: "10 min ago",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=david"
  },
  {
    id: "5",
    name: "Grace Mutua",
    vehicle: "KAA 890R",
    status: "driving", 
    location: "Nakuru - Eldoret Road",
    lastSeen: "Active now",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=grace"
  }
];

export function Header() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState("");

  const { data: user } = useQuery({
    queryKey: ["current-user"],
    queryFn: async () => {
      const userData = await apiClient.getMe();
      return {
        user_metadata: { full_name: userData.full_name },
        email: userData.email,
        last_sign_in_at: new Date().toISOString()
      };
    },
  });

  const handleLogout = async () => {
    try {
      await apiClient.logout();
      navigate("/login");
      toast({
        title: "Logged Out",
        description: "You have been successfully logged out.",
      });
    } catch (error) {
      toast({
        title: "Logout Failed",
        description: "Failed to log out. Please try again.",
        variant: "destructive",
      });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "driving": return "text-green-500";
      case "break": return "text-yellow-500";
      case "loading": return "text-blue-500";
      case "idle": return "text-gray-500";
      default: return "text-gray-500";
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "driving": return "On Route";
      case "break": return "On Break";
      case "loading": return "Loading";
      case "idle": return "Idle";
      default: return "Unknown";
    }
  };

  const activeDrivers = mockOnlineDrivers.filter(d => d.status === "driving").length;
  const totalNotifications = 23; // Mock notification count
  const criticalAlerts = 5; // Mock critical alerts

  const currentTime = new Date().toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit',
    second: '2-digit'
  });
  
  const currentDate = new Date().toLocaleDateString('en-US', {
    weekday: 'short',
    year: 'numeric',
    month: 'long', 
    day: 'numeric'
  });

  const userName = user?.user_metadata?.full_name || user?.email?.split('@')[0] || "User";
  const lastSignIn = user?.last_sign_in_at ? 
    new Date(user.last_sign_in_at).toLocaleDateString('en-US', {
      weekday: 'short',
      hour: '2-digit',
      minute: '2-digit'
    }) : "Today";

  return (
    <header className="bg-slate-800 text-white px-6 py-3">
      <div className="flex items-center justify-between">
        {/* Far Left - Logo */}
        <div className="flex items-center space-x-4">
          <CompanyLogo size="md" showText={true} />
        </div>

        {/* Left Section - Notifications and Status */}
        <div className="flex items-center space-x-4">
          {/* Notification Bell */}
          <div className="relative">
            <Button variant="ghost" size="sm" className="text-white hover:bg-slate-700 relative">
              <Bell className="w-5 h-5" />
            </Button>
            <Badge className="absolute -top-1 -right-1 bg-red-500 text-white text-xs min-w-[20px] h-5 flex items-center justify-center rounded-full">
              {totalNotifications}
            </Badge>
          </div>

          {/* Critical Alerts */}
          <div className="relative">
            <Button variant="ghost" size="sm" className="text-white hover:bg-slate-700">
              <AlertTriangle className="w-5 h-5" />
            </Button>
            <Badge className="absolute -top-1 -right-1 bg-orange-500 text-white text-xs min-w-[20px] h-5 flex items-center justify-center rounded-full">
              {criticalAlerts}
            </Badge>
          </div>

          {/* Date and Time */}
          <div className="hidden md:flex items-center space-x-4 text-sm">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-slate-600 rounded flex items-center justify-center">
                <Clock className="w-3 h-3" />
              </div>
              <span>{currentDate}</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-slate-600 rounded flex items-center justify-center">
                <Circle className="w-2 h-2 fill-current" />
              </div>
              <span>{currentTime}</span>
            </div>
            <div className="flex items-center space-x-2">
              <MapPin className="w-4 h-4" />
              <span>Nairobi, Kenya 24°C, Clear</span>
            </div>
          </div>
        </div>

    
        {/* Right Section - Search, Profile, and Online Drivers */}
        <div className="flex items-center space-x-4">
          {/* Search - Reduced Width */}
          <div className="relative hidden md:block">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <Input
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 w-48 bg-slate-700 border-slate-600 text-white placeholder:text-slate-400 focus:border-blue-500"
            />
          </div>

          {/* Profile Dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="text-white hover:bg-slate-700 flex items-center space-x-2">
                <span className="hidden md:block">Hi, {userName}</span>
                <ChevronDown className="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>My Account</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => navigate("/profile")}>
                <User className="w-4 h-4 mr-2" />
                Profile
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => navigate("/settings")}>
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout} className="text-red-600">
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Online Drivers */}
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="ghost" className="text-white hover:bg-slate-700 relative">
                <MoreVertical className="w-5 h-5" />
                <Badge className="absolute -top-1 -right-1 bg-green-500 text-white text-xs min-w-[20px] h-5 flex items-center justify-center rounded-full">
                  {activeDrivers}
                </Badge>
              </Button>
            </PopoverTrigger>
            <PopoverContent align="end" className="w-80">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold">Online Drivers</h3>
                  <Badge variant="outline">
                    {mockOnlineDrivers.length} online
                  </Badge>
                </div>
                
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {mockOnlineDrivers.map((driver) => (
                    <div key={driver.id} className="flex items-center space-x-3 p-2 rounded-lg hover:bg-accent">
                      <div className="relative">
                        <Avatar className="w-8 h-8">
                          <AvatarImage src={driver.avatar} />
                          <AvatarFallback>{driver.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                        </Avatar>
                        <div className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-white ${getStatusColor(driver.status)} bg-current`} />
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium truncate">{driver.name}</p>
                          <Badge variant="outline" className="text-xs">
                            {getStatusLabel(driver.status)}
                          </Badge>
                        </div>
                        <p className="text-xs text-muted-foreground truncate">{driver.vehicle}</p>
                        <p className="text-xs text-muted-foreground truncate">{driver.location}</p>
                        <p className="text-xs text-muted-foreground">{driver.lastSeen}</p>
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="pt-2 border-t">
                  <Button variant="outline" size="sm" className="w-full">
                    View All Drivers
                  </Button>
                </div>
              </div>
            </PopoverContent>
          </Popover>
        </div>
      </div>
    </header>
  );
}