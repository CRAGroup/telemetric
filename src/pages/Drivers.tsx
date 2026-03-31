import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { apiClient } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Users,
  Plus,
  Search,
  Filter,
  Phone,
  Mail,
  MapPin,
  Calendar,
  Star,
  Clock,
  Truck,
  AlertTriangle,
  CheckCircle2,
  Pencil,
} from "lucide-react";

interface Driver {
  id: string;
  name: string;
  email: string;
  phone: string;
  licenseNumber: string;
  licenseExpiry?: string;
  status: "active" | "inactive" | "on_leave" | "suspended";
  rating?: number;
  totalTrips?: number;
  currentVehicle?: string;
  location?: string;
  joinDate: string;
  avatar?: string;
  experience?: number;
  lastTrip?: string;
}

const Drivers = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTab, setActiveTab] = useState("all");

  const { data: drivers = [], isLoading, error } = useQuery<Driver[], Error>({
    queryKey: ["drivers"],
    queryFn: async () => {
      const response = await apiClient.getDrivers();
      return (response.items || []).map((driver: any) => ({
        id: String(driver.id),
        name: driver.name || `Driver ${driver.id}`,
        email: driver.email || "",
        phone: driver.phone || "N/A",
        licenseNumber: driver.license_number || "N/A",
        licenseExpiry: driver.license_expiry,
        status: (driver.status as Driver["status"]) || "active",
        rating: driver.rating || 4.5,
        totalTrips: driver.total_trips || 0,
        currentVehicle: driver.current_vehicle_id ? String(driver.current_vehicle_id) : undefined,
        location: driver.location,
        joinDate: driver.created_at,
        avatar: driver.avatar_url,
        experience: driver.years_experience || 0,
        lastTrip: driver.last_trip,
      }));
    },
    staleTime: 5 * 60 * 1000,
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "bg-green-100 text-green-800";
      case "inactive": return "bg-gray-100 text-gray-800";
      case "on_leave": return "bg-yellow-100 text-yellow-800";
      case "suspended": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "active": return <CheckCircle2 className="w-3 h-3" />;
      case "suspended": return <AlertTriangle className="w-3 h-3" />;
      default: return <Clock className="w-3 h-3" />;
    }
  };

  const isLicenseExpiringSoon = (expiryDate?: string) => {
    if (!expiryDate) return false;
    const diff = new Date(expiryDate).getTime() - Date.now();
    const days = Math.ceil(diff / (1000 * 60 * 60 * 24));
    return days <= 30 && days > 0;
  };

  const isLicenseExpired = (expiryDate?: string) => {
    if (!expiryDate) return false;
    return new Date(expiryDate) < new Date();
  };

  const filteredDrivers = drivers.filter((driver) => {
    const matchesSearch =
      driver.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      driver.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      driver.phone.includes(searchQuery);
    const matchesTab = activeTab === "all" || driver.status === activeTab;
    return matchesSearch && matchesTab;
  });

  const stats = {
    total: drivers.length,
    active: drivers.filter((d) => d.status === "active").length,
    onLeave: drivers.filter((d) => d.status === "on_leave").length,
    suspended: drivers.filter((d) => d.status === "suspended").length,
    avgRating:
      drivers.length > 0
        ? (drivers.reduce((sum, d) => sum + (d.rating || 0), 0) / drivers.length).toFixed(1)
        : "0.0",
  };

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto" />
          <p className="mt-2 text-muted-foreground">Loading drivers...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 flex items-center justify-center h-64">
        <p className="text-destructive">Error loading drivers: {error.message}</p>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Driver Management</h1>
          <p className="text-muted-foreground">Manage your fleet drivers and their performance</p>
        </div>
        <Button onClick={() => navigate("/drivers/add")}>
          <Plus className="w-4 h-4 mr-2" />
          Add New Driver
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {[
          { label: "Total Drivers", value: stats.total, icon: Users, color: "text-blue-500" },
          { label: "Active", value: stats.active, icon: CheckCircle2, color: "text-green-500" },
          { label: "On Leave", value: stats.onLeave, icon: Clock, color: "text-yellow-500" },
          { label: "Suspended", value: stats.suspended, icon: AlertTriangle, color: "text-red-500" },
          { label: "Avg Rating", value: stats.avgRating, icon: Star, color: "text-orange-500" },
        ].map(({ label, value, icon: Icon, color }) => (
          <Card key={label}>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Icon className={`h-4 w-4 ${color}`} />
                <div>
                  <p className="text-sm font-medium">{label}</p>
                  <p className="text-2xl font-bold">{value}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Search */}
      <div className="flex items-center space-x-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search drivers..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        <Button variant="outline">
          <Filter className="w-4 h-4 mr-2" />
          Filter
        </Button>
      </div>

      {/* Drivers List */}
      <Card>
        <CardHeader>
          <CardTitle>All Drivers</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList>
              <TabsTrigger value="all">All ({stats.total})</TabsTrigger>
              <TabsTrigger value="active">Active ({stats.active})</TabsTrigger>
              <TabsTrigger value="on_leave">On Leave ({stats.onLeave})</TabsTrigger>
              <TabsTrigger value="suspended">Suspended ({stats.suspended})</TabsTrigger>
            </TabsList>

            <TabsContent value={activeTab} className="mt-4">
              <div className="space-y-4">
                {filteredDrivers.map((driver) => (
                  <div key={driver.id} className="border rounded-lg p-4 hover:bg-accent/5 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-4">
                        <Avatar className="w-12 h-12">
                          <AvatarImage src={driver.avatar} />
                          <AvatarFallback>
                            {driver.name.split(" ").map((n) => n[0]).join("")}
                          </AvatarFallback>
                        </Avatar>

                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <h3 className="font-semibold text-lg">{driver.name}</h3>
                            <Badge className={getStatusColor(driver.status)}>
                              <div className="flex items-center space-x-1">
                                {getStatusIcon(driver.status)}
                                <span>{driver.status.replace("_", " ")}</span>
                              </div>
                            </Badge>
                            {isLicenseExpired(driver.licenseExpiry) && (
                              <Badge variant="destructive">License Expired</Badge>
                            )}
                            {!isLicenseExpired(driver.licenseExpiry) && isLicenseExpiringSoon(driver.licenseExpiry) && (
                              <Badge variant="destructive">License Expiring Soon</Badge>
                            )}
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm text-muted-foreground">
                            <div className="flex items-center space-x-2">
                              <Mail className="w-4 h-4" />
                              <span>{driver.email || "—"}</span>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Phone className="w-4 h-4" />
                              <span>{driver.phone}</span>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Calendar className="w-4 h-4" />
                              <span>License: {driver.licenseExpiry || "Not specified"}</span>
                            </div>
                            <div className="flex items-center space-x-2">
                              <Star className="w-4 h-4" />
                              <span>{driver.rating?.toFixed(1) || "N/A"}/5.0 ({driver.totalTrips || 0} trips)</span>
                            </div>
                          </div>

                          {(driver.currentVehicle || driver.location) && (
                            <div className="mt-2 flex items-center space-x-4 text-sm">
                              {driver.currentVehicle && (
                                <div className="flex items-center space-x-2 text-blue-600">
                                  <Truck className="w-4 h-4" />
                                  <span>Vehicle: {driver.currentVehicle}</span>
                                </div>
                              )}
                              {driver.location && (
                                <div className="flex items-center space-x-2 text-green-600">
                                  <MapPin className="w-4 h-4" />
                                  <span>{driver.location}</span>
                                </div>
                              )}
                            </div>
                          )}

                          <div className="mt-2 text-xs text-muted-foreground">
                            {driver.experience || 0} years experience • Joined{" "}
                            {driver.joinDate ? new Date(driver.joinDate).toLocaleDateString() : "—"}
                          </div>
                        </div>
                      </div>

                      <div className="flex space-x-2 ml-4">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => navigate(`/driver-profile/${driver.id}`)}
                        >
                          View Profile
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => navigate(`/drivers/edit/${driver.id}`)}
                        >
                          <Pencil className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}

                {filteredDrivers.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    <Users className="w-12 h-12 mx-auto mb-4 opacity-30" />
                    <p>No drivers found matching your criteria</p>
                  </div>
                )}
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export default Drivers;
