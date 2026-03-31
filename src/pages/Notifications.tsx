import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/components/ui/use-toast";
import {
  Bell, AlertTriangle, CheckCircle2, Clock, Search,
  Settings, Trash2, Check, Filter, Info, Zap, RefreshCw,
} from "lucide-react";

const SEVERITY_ICON: Record<string, JSX.Element> = {
  critical: <AlertTriangle className="w-4 h-4 text-red-500" />,
  warning: <AlertTriangle className="w-4 h-4 text-orange-500" />,
  info: <Info className="w-4 h-4 text-blue-500" />,
};

const SEVERITY_COLOR: Record<string, string> = {
  critical: "bg-red-100 text-red-800 border-red-200",
  warning: "bg-orange-100 text-orange-800 border-orange-200",
  info: "bg-blue-100 text-blue-800 border-blue-200",
};

const Notifications = () => {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [activeTab, setActiveTab] = useState("all");
  const [notifSettings, setNotifSettings] = useState({
    emailNotifications: true,
    smsNotifications: false,
    pushNotifications: true,
    maintenanceAlerts: true,
    emergencyAlerts: true,
    routeUpdates: false,
    systemUpdates: true,
  });

  const { data: alertsData, isLoading, refetch } = useQuery({
    queryKey: ["alerts-all"],
    queryFn: () => apiClient.getAlerts({ page_size: 100 }),
    staleTime: 30_000,
    refetchInterval: 60_000,
  });

  const ackMutation = useMutation({
    mutationFn: (id: number) => apiClient.acknowledgeAlert(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts-all"] });
      queryClient.invalidateQueries({ queryKey: ["alerts-recent"] });
      toast({ title: "Alert acknowledged" });
    },
  });

  const alerts: any[] = alertsData?.items || [];

  const filtered = alerts.filter((a) => {
    const matchSearch =
      !search.trim() ||
      a.alert_type?.toLowerCase().includes(search.toLowerCase()) ||
      a.message?.toLowerCase().includes(search.toLowerCase());
    const matchTab =
      activeTab === "all" ||
      (activeTab === "unread" && !a.acknowledged) ||
      (activeTab === "critical" && a.severity === "critical") ||
      (activeTab === "warning" && a.severity === "warning");
    return matchSearch && matchTab;
  });

  const unreadCount = alerts.filter((a) => !a.acknowledged).length;
  const criticalCount = alerts.filter((a) => a.severity === "critical" && !a.acknowledged).length;

  const fmtDate = (val: string) => {
    try { return new Date(val).toLocaleString(); } catch { return val; }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Notifications</h1>
          <p className="text-muted-foreground">Fleet alerts and system notifications</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            <RefreshCw className="w-4 h-4 mr-2" />Refresh
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Total", value: alerts.length, icon: Bell, color: "text-blue-500" },
          { label: "Unread", value: unreadCount, icon: Clock, color: "text-orange-500" },
          { label: "Critical", value: criticalCount, icon: AlertTriangle, color: "text-red-500" },
          { label: "Acknowledged", value: alerts.filter((a) => a.acknowledged).length, icon: CheckCircle2, color: "text-green-500" },
        ].map(({ label, value, icon: Icon, color }) => (
          <Card key={label}>
            <CardContent className="p-4 flex items-center gap-3">
              <Icon className={`h-5 w-5 ${color}`} />
              <div>
                <p className="text-sm font-medium">{label}</p>
                <p className="text-2xl font-bold">{value}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Alerts list */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center gap-3">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search alerts..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9"
              />
            </div>
          </div>

          <Card>
            <CardHeader><CardTitle>Alerts</CardTitle></CardHeader>
            <CardContent>
              <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList>
                  <TabsTrigger value="all">All ({alerts.length})</TabsTrigger>
                  <TabsTrigger value="unread">Unread ({unreadCount})</TabsTrigger>
                  <TabsTrigger value="critical">Critical ({criticalCount})</TabsTrigger>
                  <TabsTrigger value="warning">Warning</TabsTrigger>
                </TabsList>

                <TabsContent value={activeTab} className="mt-4">
                  {isLoading ? (
                    <div className="space-y-3">
                      {[1, 2, 3].map((i) => <div key={i} className="h-16 bg-muted animate-pulse rounded-lg" />)}
                    </div>
                  ) : filtered.length === 0 ? (
                    <div className="text-center py-10 text-muted-foreground">
                      <Bell className="w-10 h-10 mx-auto mb-3 opacity-30" />
                      <p>No alerts found</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {filtered.map((alert) => (
                        <div
                          key={alert.id}
                          className={`border rounded-lg p-4 transition-colors ${
                            !alert.acknowledged ? "bg-blue-50/50 border-blue-200" : "hover:bg-accent/5"
                          }`}
                        >
                          <div className="flex items-start justify-between gap-3">
                            <div className="flex items-start gap-3 flex-1">
                              {SEVERITY_ICON[alert.severity] || <Zap className="w-4 h-4 text-gray-500" />}
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 flex-wrap mb-1">
                                  <span className="font-semibold text-sm">{alert.alert_type}</span>
                                  <Badge className={`text-xs ${SEVERITY_COLOR[alert.severity] || "bg-gray-100 text-gray-800"}`}>
                                    {alert.severity}
                                  </Badge>
                                  {alert.acknowledged && (
                                    <Badge variant="outline" className="text-xs text-green-700">Acknowledged</Badge>
                                  )}
                                </div>
                                {alert.message && (
                                  <p className="text-sm text-muted-foreground mb-1">{alert.message}</p>
                                )}
                                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                                  <span>{fmtDate(alert.created_at)}</span>
                                  {alert.vehicle_id && <span>Vehicle #{alert.vehicle_id}</span>}
                                </div>
                              </div>
                            </div>
                            {!alert.acknowledged && (
                              <Button
                                variant="outline"
                                size="sm"
                                className="h-7 shrink-0"
                                onClick={() => ackMutation.mutate(alert.id)}
                                disabled={ackMutation.isPending}
                              >
                                <Check className="w-3 h-3 mr-1" />Ack
                              </Button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>

        {/* Settings panel */}
        <Card className="h-fit">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-4 w-4" />Notification Settings
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Channels</p>
              {[
                { key: "emailNotifications", label: "Email" },
                { key: "smsNotifications", label: "SMS" },
                { key: "pushNotifications", label: "Push" },
              ].map(({ key, label }) => (
                <div key={key} className="flex items-center justify-between">
                  <span className="text-sm">{label}</span>
                  <Switch
                    checked={notifSettings[key as keyof typeof notifSettings] as boolean}
                    onCheckedChange={(v) => setNotifSettings((p) => ({ ...p, [key]: v }))}
                  />
                </div>
              ))}
            </div>

            <hr />

            <div className="space-y-3">
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Alert Types</p>
              {[
                { key: "maintenanceAlerts", label: "Maintenance" },
                { key: "emergencyAlerts", label: "Emergency" },
                { key: "routeUpdates", label: "Route Updates" },
                { key: "systemUpdates", label: "System Updates" },
              ].map(({ key, label }) => (
                <div key={key} className="flex items-center justify-between">
                  <span className="text-sm">{label}</span>
                  <Switch
                    checked={notifSettings[key as keyof typeof notifSettings] as boolean}
                    onCheckedChange={(v) => setNotifSettings((p) => ({ ...p, [key]: v }))}
                  />
                </div>
              ))}
            </div>

            <Button className="w-full" size="sm" onClick={() => toast({ title: "Settings saved" })}>
              Save Settings
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Notifications;
