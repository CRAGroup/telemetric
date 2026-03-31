import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Truck, Package, Weight, AlertTriangle } from "lucide-react";

export function TruckCapacity() {
  const { data: vehicles, isLoading } = useQuery({
    queryKey: ["vehicles-capacity"],
    queryFn: async () => {
      const response = await apiClient.getVehicles();
      return response.items;
    },
  });

  // Get the first in-transit vehicle for display, or fallback to first vehicle
  const selectedVehicle = vehicles?.find(v => v.status === 'in_transit') || vehicles?.[0];

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Current Truck Capacity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            <div className="h-32 bg-gray-200 rounded"></div>
            <div className="space-y-2">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!selectedVehicle) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Current Truck Capacity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <Truck className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No vehicles available</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const currentLoad = selectedVehicle.current_load_weight || 0;
  const maxLoad = selectedVehicle.max_load_weight || 1;
  const loadPercentage = Math.round((currentLoad / maxLoad) * 100);
  
  const getLoadStatus = (percentage: number) => {
    if (percentage >= 90) return { color: "text-red-600", bg: "bg-red-100", label: "Overloaded", icon: AlertTriangle };
    if (percentage >= 75) return { color: "text-orange-600", bg: "bg-orange-100", label: "Near Capacity", icon: Package };
    if (percentage >= 50) return { color: "text-blue-600", bg: "bg-blue-100", label: "Good Load", icon: Package };
    return { color: "text-green-600", bg: "bg-green-100", label: "Light Load", icon: Package };
  };

  const status = getLoadStatus(loadPercentage);
  const StatusIcon = status.icon;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Current Truck Capacity</CardTitle>
          <Button variant="link" className="text-xs p-0 h-auto text-primary">
            View Details
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Vehicle Info */}
        <div className="flex items-center space-x-3 p-3 bg-muted/50 rounded-lg">
          <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
            <Truck className="w-5 h-5 text-primary" />
          </div>
          <div className="flex-1">
            <p className="font-semibold text-sm">{selectedVehicle.registration_number}</p>
            <p className="text-xs text-muted-foreground">{selectedVehicle.model_name}</p>
          </div>
          <Badge variant={selectedVehicle.status === 'in_transit' ? 'default' : 'secondary'}>
            {selectedVehicle.status.replace('_', ' ')}
          </Badge>
        </div>

        {/* Capacity Visualization */}
        <div className="relative">
          <div className="w-full h-32 bg-gray-100 rounded-lg border-2 border-gray-200 relative overflow-hidden">
            {/* Truck outline */}
            <div className="absolute inset-2 border-2 border-gray-300 rounded bg-white">
              {/* Load visualization */}
              <div 
                className={`absolute bottom-0 left-0 right-0 ${status.bg} transition-all duration-500 rounded-b`}
                style={{ height: `${Math.min(loadPercentage, 100)}%` }}
              >
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className={`text-2xl font-bold ${status.color}`}>
                    {loadPercentage}%
                  </span>
                </div>
              </div>
            </div>
            
            {/* Status indicator */}
            <div className="absolute top-2 right-2">
              <div className={`flex items-center space-x-1 px-2 py-1 rounded-full ${status.bg}`}>
                <StatusIcon className={`w-3 h-3 ${status.color}`} />
                <span className={`text-xs font-medium ${status.color}`}>
                  {status.label}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Load Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Load Progress</span>
            <span className="font-medium">{loadPercentage}%</span>
          </div>
          <Progress value={loadPercentage} className="h-2" />
        </div>

        {/* Load Details */}
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <Weight className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">Current Load</span>
            </div>
            <span className="text-sm font-semibold text-foreground">
              {currentLoad.toLocaleString()} kg
            </span>
          </div>
          
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <Package className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">Max Capacity</span>
            </div>
            <span className="text-sm font-semibold text-foreground">
              {maxLoad.toLocaleString()} kg
            </span>
          </div>
          
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Available Space</span>
            <span className="text-sm font-semibold text-foreground">
              {(maxLoad - currentLoad).toLocaleString()} kg
            </span>
          </div>
          
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Load Category</span>
            <span className="text-sm font-semibold text-foreground">
              {selectedVehicle.load_category || "General Cargo"}
            </span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-2">
          <Button variant="outline" size="sm" className="flex-1">
            Update Load
          </Button>
          <Button variant="outline" size="sm" className="flex-1">
            View Route
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
