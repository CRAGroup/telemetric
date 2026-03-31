import { AICameraMonitor } from "@/components/AICameraMonitor";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Camera, AlertTriangle, CheckCircle2, TrendingUp, Video } from "lucide-react";

const vehicles = [
  { id: "1", registration: "KCA 456T", driver: "Kamau Mwangi", status: "active", alerts: 3 },
  { id: "2", registration: "KBZ 789M", driver: "John Omondi", status: "active", alerts: 1 },
  { id: "3", registration: "KCB 234L", driver: "Peter Wanjiru", status: "stopped", alerts: 0 },
  { id: "4", registration: "KDA 567P", driver: "Mary Njeri", status: "active", alerts: 2 },
];

const CameraMonitoring = () => {
  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">AI Camera Monitoring</h1>
          <p className="text-muted-foreground mt-1">
            Real-time driver behavior analysis and safety monitoring
          </p>
        </div>
        <Button>
          <Video className="mr-2 h-4 w-4" />
          View All Cameras
        </Button>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Active Cameras</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold">8</p>
                <p className="text-xs text-muted-foreground">of 10 vehicles</p>
              </div>
              <Camera className="h-8 w-8 text-primary" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Active Alerts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-orange-600">6</p>
                <p className="text-xs text-muted-foreground">Requires attention</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Safe Drivers</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-green-600">5</p>
                <p className="text-xs text-muted-foreground">No incidents today</p>
              </div>
              <CheckCircle2 className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Avg Safety Score</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold">82%</p>
                <p className="text-xs text-green-600 flex items-center gap-1">
                  <TrendingUp className="h-3 w-3" />
                  +5% from yesterday
                </p>
              </div>
              <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                <span className="text-lg">📊</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Camera Monitor */}
        <div className="lg:col-span-2">
          <AICameraMonitor />
        </div>

        {/* Vehicle List */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Active Vehicles</CardTitle>
                <Select defaultValue="all">
                  <SelectTrigger className="w-[120px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All</SelectItem>
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="alerts">With Alerts</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {vehicles.map((vehicle) => (
                <div
                  key={vehicle.id}
                  className="p-3 border rounded-lg hover:bg-accent/5 cursor-pointer transition-colors"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <p className="font-semibold text-sm">{vehicle.registration}</p>
                      <p className="text-xs text-muted-foreground">{vehicle.driver}</p>
                    </div>
                    <Badge variant={vehicle.status === "active" ? "default" : "secondary"}>
                      {vehicle.status === "active" ? "🎥 Live" : "Offline"}
                    </Badge>
                  </div>
                  {vehicle.alerts > 0 && (
                    <div className="flex items-center gap-2 text-xs">
                      <AlertTriangle className="h-3 w-3 text-orange-600" />
                      <span className="text-orange-600 font-medium">
                        {vehicle.alerts} active alert{vehicle.alerts > 1 ? "s" : ""}
                      </span>
                    </div>
                  )}
                  {vehicle.alerts === 0 && vehicle.status === "active" && (
                    <div className="flex items-center gap-2 text-xs">
                      <CheckCircle2 className="h-3 w-3 text-green-600" />
                      <span className="text-green-600 font-medium">All clear</span>
                    </div>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">System Info</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Hardware:</span>
                <span className="font-medium">Raspberry Pi 4</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">AI Model:</span>
                <span className="font-medium">YOLOv8 + DMS</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Processing:</span>
                <span className="font-medium">Edge + Cloud</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Frame Rate:</span>
                <span className="font-medium">30 FPS</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Resolution:</span>
                <span className="font-medium">1080p</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Storage:</span>
                <span className="font-medium">Local + S3</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default CameraMonitoring;
