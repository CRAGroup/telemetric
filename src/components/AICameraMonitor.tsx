import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { 
  Camera, 
  Eye, 
  AlertTriangle, 
  CheckCircle2, 
  Video, 
  Activity,
  Clock,
  Maximize2,
  RefreshCw,
  Settings
} from "lucide-react";

interface CameraAlert {
  id: string;
  type: "drowsiness" | "distraction" | "phone_use" | "no_seatbelt" | "smoking" | "lane_departure";
  severity: "low" | "medium" | "high" | "critical";
  timestamp: string;
  description: string;
  confidence: number;
}

interface DriverMetrics {
  attentionScore: number;
  drowsinessLevel: number;
  distractionCount: number;
  totalAlerts: number;
  drivingTime: string;
  lastIncident: string;
}

const mockAlerts: CameraAlert[] = [
  {
    id: "1",
    type: "drowsiness",
    severity: "high",
    timestamp: "2 mins ago",
    description: "Driver showing signs of drowsiness - eyes closing frequently",
    confidence: 87,
  },
  {
    id: "2",
    type: "phone_use",
    severity: "critical",
    timestamp: "15 mins ago",
    description: "Mobile phone detected in driver's hand",
    confidence: 94,
  },
  {
    id: "3",
    type: "distraction",
    severity: "medium",
    timestamp: "28 mins ago",
    description: "Driver looking away from road for extended period",
    confidence: 76,
  },
];

const mockMetrics: DriverMetrics = {
  attentionScore: 78,
  drowsinessLevel: 35,
  distractionCount: 3,
  totalAlerts: 8,
  drivingTime: "3h 45m",
  lastIncident: "2 mins ago",
};

const alertTypeConfig = {
  drowsiness: { label: "Drowsiness", icon: "😴", color: "text-orange-600" },
  distraction: { label: "Distraction", icon: "👀", color: "text-yellow-600" },
  phone_use: { label: "Phone Use", icon: "📱", color: "text-red-600" },
  no_seatbelt: { label: "No Seatbelt", icon: "🔴", color: "text-red-600" },
  smoking: { label: "Smoking", icon: "🚬", color: "text-orange-600" },
  lane_departure: { label: "Lane Departure", icon: "🛣️", color: "text-yellow-600" },
};

const severityConfig = {
  low: { variant: "secondary" as const, label: "Low" },
  medium: { variant: "default" as const, label: "Medium" },
  high: { variant: "destructive" as const, label: "High" },
  critical: { variant: "destructive" as const, label: "Critical" },
};

export function AICameraMonitor() {
  const [isLive, setIsLive] = useState(true);
  const [selectedVehicle] = useState("KCA 456T");

  return (
    <Card className="h-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Camera className="h-5 w-5 text-primary" />
            <CardTitle className="text-lg">AI Camera Monitor</CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant={isLive ? "default" : "secondary"} className="gap-1">
              {isLive ? (
                <>
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-white"></span>
                  </span>
                  Live
                </>
              ) : (
                "Offline"
              )}
            </Badge>
            <Button size="icon" variant="ghost" className="h-8 w-8">
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </div>
        <p className="text-sm text-muted-foreground">
          Vehicle: {selectedVehicle} • Driver: Kamau Mwangi
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        <Tabs defaultValue="live" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="live">Live Feed</TabsTrigger>
            <TabsTrigger value="alerts">Alerts</TabsTrigger>
            <TabsTrigger value="metrics">Metrics</TabsTrigger>
          </TabsList>

          <TabsContent value="live" className="space-y-4">
            {/* Video Feed */}
            <div className="relative aspect-video bg-muted rounded-lg overflow-hidden">
              <img
                src="https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?w=800&h=450&fit=crop"
                alt="Driver camera feed"
                className="w-full h-full object-cover"
              />
              <div className="absolute top-3 left-3 flex gap-2">
                <Badge variant="destructive" className="gap-1">
                  <Video className="h-3 w-3" />
                  Recording
                </Badge>
                <Badge variant="secondary">
                  <Clock className="h-3 w-3 mr-1" />
                  {mockMetrics.drivingTime}
                </Badge>
              </div>
              <div className="absolute top-3 right-3 flex gap-2">
                <Button size="icon" variant="secondary" className="h-8 w-8">
                  <Maximize2 className="h-4 w-4" />
                </Button>
                <Button size="icon" variant="secondary" className="h-8 w-8">
                  <RefreshCw className="h-4 w-4" />
                </Button>
              </div>
              
              {/* AI Detection Overlay */}
              <div className="absolute bottom-3 left-3 right-3 bg-black/70 backdrop-blur-sm rounded-lg p-3">
                <div className="flex items-center justify-between text-white text-sm">
                  <div className="flex items-center gap-2">
                    <Eye className="h-4 w-4 text-green-400" />
                    <span>Face Detected</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Activity className="h-4 w-4 text-blue-400" />
                    <span>Analyzing...</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-muted rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-muted-foreground">Attention Score</span>
                  <span className="text-sm font-bold">{mockMetrics.attentionScore}%</span>
                </div>
                <Progress value={mockMetrics.attentionScore} className="h-2" />
              </div>
              <div className="p-3 bg-muted rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-muted-foreground">Drowsiness Level</span>
                  <span className="text-sm font-bold text-orange-600">{mockMetrics.drowsinessLevel}%</span>
                </div>
                <Progress value={mockMetrics.drowsinessLevel} className="h-2" />
              </div>
            </div>

            {/* Recent Alert */}
            {mockAlerts[0] && (
              <div className="p-3 border border-destructive/50 bg-destructive/5 rounded-lg">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="h-5 w-5 text-destructive mt-0.5" />
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold text-sm">Latest Alert</span>
                      <Badge variant={severityConfig[mockAlerts[0].severity].variant}>
                        {severityConfig[mockAlerts[0].severity].label}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{mockAlerts[0].description}</p>
                    <p className="text-xs text-muted-foreground mt-1">{mockAlerts[0].timestamp}</p>
                  </div>
                </div>
              </div>
            )}
          </TabsContent>

          <TabsContent value="alerts" className="space-y-3">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Recent Alerts ({mockAlerts.length})</span>
              <Button variant="outline" size="sm">
                View All
              </Button>
            </div>
            
            {mockAlerts.map((alert) => (
              <div key={alert.id} className="p-3 border rounded-lg hover:bg-accent/5 transition-colors">
                <div className="flex items-start gap-3">
                  <div className="text-2xl">{alertTypeConfig[alert.type].icon}</div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold text-sm">{alertTypeConfig[alert.type].label}</span>
                      <Badge variant={severityConfig[alert.severity].variant} className="text-xs">
                        {severityConfig[alert.severity].label}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">{alert.description}</p>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">{alert.timestamp}</span>
                      <span className="text-muted-foreground">Confidence: {alert.confidence}%</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </TabsContent>

          <TabsContent value="metrics" className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div className="p-4 border rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  <span className="text-xs text-muted-foreground">Attention Score</span>
                </div>
                <p className="text-2xl font-bold">{mockMetrics.attentionScore}%</p>
                <Progress value={mockMetrics.attentionScore} className="h-2 mt-2" />
              </div>

              <div className="p-4 border rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="h-4 w-4 text-orange-600" />
                  <span className="text-xs text-muted-foreground">Drowsiness</span>
                </div>
                <p className="text-2xl font-bold text-orange-600">{mockMetrics.drowsinessLevel}%</p>
                <Progress value={mockMetrics.drowsinessLevel} className="h-2 mt-2" />
              </div>

              <div className="p-4 border rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Eye className="h-4 w-4 text-blue-600" />
                  <span className="text-xs text-muted-foreground">Distractions</span>
                </div>
                <p className="text-2xl font-bold">{mockMetrics.distractionCount}</p>
                <p className="text-xs text-muted-foreground mt-1">Today</p>
              </div>

              <div className="p-4 border rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Activity className="h-4 w-4 text-primary" />
                  <span className="text-xs text-muted-foreground">Total Alerts</span>
                </div>
                <p className="text-2xl font-bold">{mockMetrics.totalAlerts}</p>
                <p className="text-xs text-muted-foreground mt-1">Today</p>
              </div>
            </div>

            <div className="p-4 border rounded-lg">
              <h4 className="font-semibold text-sm mb-3">Driving Session</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Duration:</span>
                  <span className="font-medium">{mockMetrics.drivingTime}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Last Incident:</span>
                  <span className="font-medium">{mockMetrics.lastIncident}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Camera Status:</span>
                  <Badge variant="default" className="text-xs">Active</Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">AI Model:</span>
                  <span className="font-medium">v2.1.0</span>
                </div>
              </div>
            </div>

            <div className="p-4 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg">
              <div className="flex items-start gap-3">
                <Camera className="h-5 w-5 text-blue-600 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-blue-900 dark:text-blue-100">
                    Raspberry Pi Camera System
                  </p>
                  <p className="text-xs text-blue-700 dark:text-blue-300 mt-1">
                    Real-time AI analysis powered by edge computing. Data is processed locally and synced to cloud.
                  </p>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
