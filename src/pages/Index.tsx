import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  Truck, MapPin, Activity, AlertTriangle, TrendingUp,
  Users, Clock, Wrench, CheckCircle2, Plus, ArrowRight,
} from "lucide-react";

const Index = () => {
  const { data: vehiclesResponse } = useQuery({
    queryKey: ["vehicles"],
    queryFn: () => apiClient.getVehicles({ page: 1, page_size: 200 }),
    staleTime: 60_000,
  });

  const { data: driversResponse } = useQuery({
    queryKey: ["drivers"],
    queryFn: () => apiClient.getDrivers({ page_size: 200 }),
    staleTime: 60_000,
  });

  const { data: maintenanceStats } = useQuery({
    queryKey: ["maintenance-stats"],
    queryFn: () => apiClient.getMaintenanceStats(),
    staleTime: 60_000,
  });

  const { data: alertsResponse } = useQuery({
    queryKey: ["alerts-recent"],
    queryFn: () => apiClient.getAlerts({ page_size: 5 }),
    staleTime: 30_000,
  });

  const vehicles = vehiclesResponse?.items || [];
  const totalVehicles = vehiclesResponse?.total || 0;
  const totalDrivers = driversResponse?.total || 0;
  const activeDrivers = (driversResponse?.items || []).filter((d: any) => d.status === "active").length;

  const activeVehicles = vehicles.filter((v: any) => v.vehicle_status === "active" || v.status === "active").length;
  const idleVehicles = vehicles.filter((v: any) => v.vehicle_status === "idle" || v.status === "idle").length;
  const maintenanceVehicles = vehicles.filter((v: any) =>
    v.vehicle_status === "under maintenance" || v.status === "maintenance"
  ).length;
  const assignedVehicles = vehicles.filter((v: any) => v.driver_id).length;
  const utilizationRate = totalVehicles > 0 ? Math.round((activeVehicles / totalVehicles) * 100) : 0;

  const recentAlerts = alertsResponse?.items || [];
  const mStats = maintenanceStats || { total: 0, pending: 0, overdue: 0, in_progress: 0, completed: 0 };

  const SEVERITY_COLOR: Record<string, string> = {
    critical: "text-red-600 bg-red-50",
    warning: "text-orange-600 bg-orange-50",
    info: "text-blue-600 bg-blue-50",
  };

  return (
    <main className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Fleet Dashboard</h1>
          <p className="text-muted-foreground">Real-time overview of your fleet operations</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-green-600 border-green-600 gap-1">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse inline-block" />
            Live
          </Badge>
          <Button asChild size="sm">
            <Link to="/vehicles/add"><Plus className="h-4 w-4 mr-1" />Add Vehicle</Link>
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="border-l-4 border-l-blue-500">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Total Vehicles</CardTitle>
            <Truck className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalVehicles}</div>
            <p className="text-xs text-muted-foreground">{assignedVehicles} assigned to drivers</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-green-500">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Active</CardTitle>
            <Activity className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{activeVehicles}</div>
            <p className="text-xs text-muted-foreground">{idleVehicles} idle</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-purple-500">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Drivers</CardTitle>
            <Users className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalDrivers}</div>
            <p className="text-xs text-muted-foreground">{activeDrivers} active</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-red-500">
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Maintenance</CardTitle>
            <Wrench className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{mStats.pending + mStats.overdue}</div>
            <p className="text-xs text-muted-foreground">{mStats.overdue} overdue</p>
          </CardContent>
        </Card>
      </div>

      {/* Secondary row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Fleet Utilization */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />Fleet Utilization
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between text-sm">
              <span>Active rate</span>
              <span className="font-semibold">{utilizationRate}%</span>
            </div>
            <Progress value={utilizationRate} className="h-2" />
            <div className="grid grid-cols-3 gap-2 text-center text-xs">
              <div className="p-2 bg-green-50 rounded">
                <div className="font-bold text-green-700">{activeVehicles}</div>
                <div className="text-green-600">Active</div>
              </div>
              <div className="p-2 bg-yellow-50 rounded">
                <div className="font-bold text-yellow-700">{idleVehicles}</div>
                <div className="text-yellow-600">Idle</div>
              </div>
              <div className="p-2 bg-red-50 rounded">
                <div className="font-bold text-red-700">{maintenanceVehicles}</div>
                <div className="text-red-600">Maint.</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Maintenance Summary */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Wrench className="h-4 w-4" />Maintenance
              </CardTitle>
              <Button asChild variant="ghost" size="sm" className="h-6 text-xs">
                <Link to="/maintenance">View all <ArrowRight className="h-3 w-3 ml-1" /></Link>
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-2">
            {[
              { label: "Pending", value: mStats.pending, color: "text-yellow-600" },
              { label: "In Progress", value: mStats.in_progress, color: "text-blue-600" },
              { label: "Overdue", value: mStats.overdue, color: "text-red-600" },
              { label: "Completed", value: mStats.completed, color: "text-green-600" },
            ].map(({ label, value, color }) => (
              <div key={label} className="flex justify-between items-center text-sm">
                <span className="text-muted-foreground">{label}</span>
                <span className={`font-semibold ${color}`}>{value}</span>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* System Status */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Clock className="h-4 w-4" />System Status
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {[
              { label: "API Server", ok: true },
              { label: "Database", ok: true },
              { label: "WebSocket", ok: true },
              { label: "Telemetry", ok: true },
            ].map(({ label, ok }) => (
              <div key={label} className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">{label}</span>
                <div className="flex items-center gap-1">
                  {ok
                    ? <CheckCircle2 className="h-3.5 w-3.5 text-green-500" />
                    : <AlertTriangle className="h-3.5 w-3.5 text-red-500" />}
                  <span className={ok ? "text-green-600 text-xs" : "text-red-600 text-xs"}>
                    {ok ? "Operational" : "Down"}
                  </span>
                </div>
              </div>
            ))}
            <p className="text-xs text-muted-foreground pt-1">
              Updated {new Date().toLocaleTimeString()}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Alerts + Quick Links */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Recent Alerts */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <AlertTriangle className="h-4 w-4" />Recent Alerts
              </CardTitle>
              <Button asChild variant="ghost" size="sm" className="h-6 text-xs">
                <Link to="/notifications">View all <ArrowRight className="h-3 w-3 ml-1" /></Link>
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {recentAlerts.length === 0 ? (
              <div className="text-center py-6 text-muted-foreground text-sm">
                <CheckCircle2 className="h-8 w-8 mx-auto mb-2 text-green-500 opacity-50" />
                No recent alerts
              </div>
            ) : (
              <div className="space-y-2">
                {recentAlerts.map((alert: any) => (
                  <div key={alert.id} className={`p-2 rounded-lg text-sm ${SEVERITY_COLOR[alert.severity] || "text-gray-600 bg-gray-50"}`}>
                    <div className="font-medium">{alert.alert_type}</div>
                    {alert.message && <div className="text-xs opacity-80 truncate">{alert.message}</div>}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-2">
            {[
              { label: "Add Vehicle", to: "/vehicles/add", icon: Truck },
              { label: "Add Driver", to: "/drivers/add", icon: Users },
              { label: "Schedule Maintenance", to: "/maintenance", icon: Wrench },
              { label: "View Tracking", to: "/tracking", icon: MapPin },
              { label: "Generate Report", to: "/reports", icon: TrendingUp },
              { label: "View Alerts", to: "/notifications", icon: AlertTriangle },
            ].map(({ label, to, icon: Icon }) => (
              <Button key={to} asChild variant="outline" size="sm" className="justify-start h-9 text-xs">
                <Link to={to}>
                  <Icon className="h-3.5 w-3.5 mr-2" />{label}
                </Link>
              </Button>
            ))}
          </CardContent>
        </Card>
      </div>
    </main>
  );
};

export default Index;
