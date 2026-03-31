import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { 
  Star, 
  TrendingUp, 
  TrendingDown,
  Award,
  AlertTriangle,
  Clock,
  MapPin,
  Fuel,
  Shield
} from "lucide-react";

interface Driver {
  id: string;
  name: string;
  avatar?: string;
  rating: number;
  totalTrips: number;
  safetyScore: number;
  fuelEfficiency: number;
  onTimeDelivery: number;
  totalDistance: number;
  violations: number;
  status: "active" | "inactive" | "on-trip";
}

interface PerformanceMetric {
  label: string;
  value: number;
  unit: string;
  trend: "up" | "down" | "stable";
  trendValue: number;
}

// Fetch drivers from API
const fetchDriversForPerformance = async (): Promise<Driver[]> => {
  const response = await apiClient.getDrivers();
  
  const drivers: Driver[] = (response.items || []).map((driver: any) => {
    return {
      id: String(driver.id),
      name: driver.name || 'Unknown Driver',
      avatar: driver.avatar_url,
      rating: driver.rating || Math.random() * 1 + 4,
      totalTrips: driver.total_trips || 0,
      safetyScore: driver.safety_score || Math.floor(Math.random() * 10) + 90,
      fuelEfficiency: driver.fuel_efficiency || Math.floor(Math.random() * 15) + 80,
      onTimeDelivery: driver.on_time_delivery || Math.floor(Math.random() * 15) + 85,
      totalDistance: Math.floor(driver.total_distance || 0),
      violations: driver.violations_count || 0,
      status: driver.status === 'active' ? "active" : "inactive"
    };
  });

  return drivers;
};

export default function DriverPerformance() {
  const [selectedDriver, setSelectedDriver] = useState<string>("");
  const [timeRange, setTimeRange] = useState<string>("30d");

  // Fetch drivers from database
  const { data: drivers = [], isLoading, error } = useQuery({
    queryKey: ['drivers-performance'],
    queryFn: fetchDriversForPerformance,
  });

  // Set default selected driver when data loads
  const currentDriver = drivers.find(d => d.id === selectedDriver) || drivers[0];

  if (isLoading) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
            <p className="mt-2 text-gray-600">Loading driver performance data...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <p className="text-red-600">Error loading driver performance: {error.message}</p>
          </div>
        </div>
      </div>
    );
  }

  if (drivers.length === 0) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <p className="text-gray-600">No drivers found in the system.</p>
          </div>
        </div>
      </div>
    );
  }

  // Set default driver if none selected
  if (!selectedDriver && drivers.length > 0) {
    setSelectedDriver(drivers[0].id);
  }

  if (!currentDriver) {
    return null;
  }

  const performanceMetrics: PerformanceMetric[] = [
    {
      label: "Safety Score",
      value: currentDriver.safetyScore,
      unit: "%",
      trend: "up",
      trendValue: 2.3
    },
    {
      label: "Fuel Efficiency", 
      value: currentDriver.fuelEfficiency,
      unit: "%",
      trend: "up",
      trendValue: 1.8
    },
    {
      label: "On-Time Delivery",
      value: currentDriver.onTimeDelivery,
      unit: "%", 
      trend: "down",
      trendValue: -0.5
    },
    {
      label: "Total Distance",
      value: currentDriver.totalDistance,
      unit: "km",
      trend: "up",
      trendValue: 12.4
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "bg-green-100 text-green-800";
      case "on-trip": return "bg-blue-100 text-blue-800";
      case "inactive": return "bg-gray-100 text-gray-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "up": return <TrendingUp className="h-4 w-4 text-green-600" />;
      case "down": return <TrendingDown className="h-4 w-4 text-red-600" />;
      default: return null;
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Driver Performance</h1>
        <div className="flex gap-4">
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
              <SelectItem value="90d">Last 90 days</SelectItem>
              <SelectItem value="1y">Last year</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Driver Selection */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="h-5 w-5" />
              Select Driver
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {drivers.map((driver) => (
              <div
                key={driver.id}
                className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                  selectedDriver === driver.id 
                    ? "border-blue-500 bg-blue-50" 
                    : "border-gray-200 hover:border-gray-300"
                }`}
                onClick={() => setSelectedDriver(driver.id)}
              >
                <div className="flex items-center gap-3">
                  <Avatar className="h-10 w-10">
                    <AvatarImage src={driver.avatar} />
                    <AvatarFallback>{driver.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <p className="font-medium text-sm">{driver.name}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <div className="flex items-center gap-1">
                        <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                        <span className="text-xs text-gray-600">{driver.rating}</span>
                      </div>
                      <Badge className={`text-xs ${getStatusColor(driver.status)}`}>
                        {driver.status}
                      </Badge>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Performance Overview */}
        <div className="lg:col-span-3 space-y-6">
          {/* Driver Header */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <Avatar className="h-16 w-16">
                    <AvatarImage src={currentDriver.avatar} />
                    <AvatarFallback className="text-lg">
                      {currentDriver.name.split(' ').map(n => n[0]).join('')}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <h2 className="text-2xl font-bold">{currentDriver.name}</h2>
                    <div className="flex items-center gap-4 mt-2">
                      <div className="flex items-center gap-1">
                        <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                        <span className="font-medium">{currentDriver.rating}</span>
                        <span className="text-gray-500">rating</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <MapPin className="h-4 w-4 text-gray-500" />
                        <span className="text-gray-600">{currentDriver.totalTrips} trips</span>
                      </div>
                      <Badge className={getStatusColor(currentDriver.status)}>
                        {currentDriver.status}
                      </Badge>
                    </div>
                  </div>
                </div>
                <Button>View Details</Button>
              </div>
            </CardContent>
          </Card>

          {/* Performance Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {performanceMetrics.map((metric, index) => (
              <Card key={index}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-600">{metric.label}</span>
                    {getTrendIcon(metric.trend)}
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-2xl font-bold">
                      {metric.unit === "km" ? metric.value.toLocaleString() : metric.value}
                    </span>
                    <span className="text-sm text-gray-500">{metric.unit}</span>
                  </div>
                  <div className="flex items-center gap-1 mt-1">
                    <span className={`text-xs ${
                      metric.trend === "up" ? "text-green-600" : 
                      metric.trend === "down" ? "text-red-600" : "text-gray-600"
                    }`}>
                      {metric.trend === "up" ? "+" : metric.trend === "down" ? "" : ""}
                      {metric.trendValue}%
                    </span>
                    <span className="text-xs text-gray-500">vs last period</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Detailed Performance */}
          <Tabs defaultValue="overview" className="space-y-4">
            <TabsList>
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="safety">Safety</TabsTrigger>
              <TabsTrigger value="efficiency">Efficiency</TabsTrigger>
              <TabsTrigger value="violations">Violations</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Shield className="h-5 w-5" />
                      Safety Performance
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm">Overall Safety Score</span>
                        <span className="font-medium">{currentDriver.safetyScore}%</span>
                      </div>
                      <Progress value={currentDriver.safetyScore} className="h-2" />
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">Violations</span>
                        <p className="font-medium">{currentDriver.violations}</p>
                      </div>
                      <div>
                        <span className="text-gray-600">Clean Days</span>
                        <p className="font-medium">28</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Fuel className="h-5 w-5" />
                      Efficiency Metrics
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm">Fuel Efficiency</span>
                        <span className="font-medium">{currentDriver.fuelEfficiency}%</span>
                      </div>
                      <Progress value={currentDriver.fuelEfficiency} className="h-2" />
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">Avg. Consumption</span>
                        <p className="font-medium">12.5 L/100km</p>
                      </div>
                      <div>
                        <span className="text-gray-600">Cost Savings</span>
                        <p className="font-medium">KSh 15,000</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="safety" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Safety Breakdown</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm">Speed Compliance</span>
                        <span className="text-sm font-medium">96%</span>
                      </div>
                      <Progress value={96} className="h-2" />
                    </div>
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm">Harsh Braking Events</span>
                        <span className="text-sm font-medium">92%</span>
                      </div>
                      <Progress value={92} className="h-2" />
                    </div>
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm">Smooth Acceleration</span>
                        <span className="text-sm font-medium">94%</span>
                      </div>
                      <Progress value={94} className="h-2" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="efficiency" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Efficiency Analysis</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center p-4 bg-blue-50 rounded-lg">
                      <Clock className="h-8 w-8 mx-auto mb-2 text-blue-600" />
                      <p className="text-2xl font-bold text-blue-600">{currentDriver.onTimeDelivery}%</p>
                      <p className="text-sm text-gray-600">On-Time Delivery</p>
                    </div>
                    <div className="text-center p-4 bg-green-50 rounded-lg">
                      <Fuel className="h-8 w-8 mx-auto mb-2 text-green-600" />
                      <p className="text-2xl font-bold text-green-600">{currentDriver.fuelEfficiency}%</p>
                      <p className="text-sm text-gray-600">Fuel Efficiency</p>
                    </div>
                    <div className="text-center p-4 bg-purple-50 rounded-lg">
                      <MapPin className="h-8 w-8 mx-auto mb-2 text-purple-600" />
                      <p className="text-2xl font-bold text-purple-600">{currentDriver.totalDistance.toLocaleString()}</p>
                      <p className="text-sm text-gray-600">Total Distance (km)</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="violations" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5" />
                    Violation History
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {currentDriver.violations === 0 ? (
                    <div className="text-center py-8">
                      <Award className="h-12 w-12 mx-auto mb-4 text-green-600" />
                      <p className="text-lg font-medium text-green-600">Excellent Record!</p>
                      <p className="text-gray-600">No violations in the selected period</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                        <div>
                          <p className="font-medium text-red-800">Speed Violation</p>
                          <p className="text-sm text-red-600">Exceeded speed limit by 15 km/h</p>
                        </div>
                        <Badge variant="destructive">Minor</Badge>
                      </div>
                      {currentDriver.violations > 1 && (
                        <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                          <div>
                            <p className="font-medium text-yellow-800">Late Delivery</p>
                            <p className="text-sm text-yellow-600">Delivery delayed by 2 hours</p>
                          </div>
                          <Badge variant="secondary">Warning</Badge>
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}