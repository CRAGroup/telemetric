import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/use-toast";
import { Bell, Mail, MessageSquare, Truck, AlertTriangle } from "lucide-react";

export function NotificationSettings() {
  const { toast } = useToast();
  const [notifications, setNotifications] = useState({
    emailNotifications: true,
    pushNotifications: true,
    smsNotifications: false,
    vehicleAlerts: true,
    maintenanceReminders: true,
    deliveryUpdates: true,
    driverMessages: true,
    systemAlerts: true,
    weeklyReports: false,
    monthlyReports: true,
  });

  const handleToggle = (key: keyof typeof notifications) => {
    setNotifications(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const handleSave = () => {
    // Save to backend
    toast({
      title: "Notifications updated",
      description: "Your notification preferences have been saved.",
    });
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Notification Channels</CardTitle>
          <CardDescription>
            Choose how you want to receive notifications
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Mail className="h-5 w-5 text-muted-foreground" />
              <div>
                <Label htmlFor="email-notifications">Email Notifications</Label>
                <p className="text-sm text-muted-foreground">
                  Receive notifications via email
                </p>
              </div>
            </div>
            <Switch
              id="email-notifications"
              checked={notifications.emailNotifications}
              onCheckedChange={() => handleToggle("emailNotifications")}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Bell className="h-5 w-5 text-muted-foreground" />
              <div>
                <Label htmlFor="push-notifications">Push Notifications</Label>
                <p className="text-sm text-muted-foreground">
                  Receive push notifications in browser
                </p>
              </div>
            </div>
            <Switch
              id="push-notifications"
              checked={notifications.pushNotifications}
              onCheckedChange={() => handleToggle("pushNotifications")}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <MessageSquare className="h-5 w-5 text-muted-foreground" />
              <div>
                <Label htmlFor="sms-notifications">SMS Notifications</Label>
                <p className="text-sm text-muted-foreground">
                  Receive notifications via SMS
                </p>
              </div>
            </div>
            <Switch
              id="sms-notifications"
              checked={notifications.smsNotifications}
              onCheckedChange={() => handleToggle("smsNotifications")}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Alert Preferences</CardTitle>
          <CardDescription>
            Manage what alerts you want to receive
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Truck className="h-5 w-5 text-muted-foreground" />
              <div>
                <Label htmlFor="vehicle-alerts">Vehicle Alerts</Label>
                <p className="text-sm text-muted-foreground">
                  Alerts about vehicle status changes
                </p>
              </div>
            </div>
            <Switch
              id="vehicle-alerts"
              checked={notifications.vehicleAlerts}
              onCheckedChange={() => handleToggle("vehicleAlerts")}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <AlertTriangle className="h-5 w-5 text-muted-foreground" />
              <div>
                <Label htmlFor="maintenance-reminders">Maintenance Reminders</Label>
                <p className="text-sm text-muted-foreground">
                  Reminders for scheduled maintenance
                </p>
              </div>
            </div>
            <Switch
              id="maintenance-reminders"
              checked={notifications.maintenanceReminders}
              onCheckedChange={() => handleToggle("maintenanceReminders")}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Bell className="h-5 w-5 text-muted-foreground" />
              <div>
                <Label htmlFor="delivery-updates">Delivery Updates</Label>
                <p className="text-sm text-muted-foreground">
                  Updates on delivery status
                </p>
              </div>
            </div>
            <Switch
              id="delivery-updates"
              checked={notifications.deliveryUpdates}
              onCheckedChange={() => handleToggle("deliveryUpdates")}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <MessageSquare className="h-5 w-5 text-muted-foreground" />
              <div>
                <Label htmlFor="driver-messages">Driver Messages</Label>
                <p className="text-sm text-muted-foreground">
                  Messages from drivers
                </p>
              </div>
            </div>
            <Switch
              id="driver-messages"
              checked={notifications.driverMessages}
              onCheckedChange={() => handleToggle("driverMessages")}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <AlertTriangle className="h-5 w-5 text-muted-foreground" />
              <div>
                <Label htmlFor="system-alerts">System Alerts</Label>
                <p className="text-sm text-muted-foreground">
                  Important system notifications
                </p>
              </div>
            </div>
            <Switch
              id="system-alerts"
              checked={notifications.systemAlerts}
              onCheckedChange={() => handleToggle("systemAlerts")}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Reports</CardTitle>
          <CardDescription>
            Schedule automated reports
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="weekly-reports">Weekly Reports</Label>
              <p className="text-sm text-muted-foreground">
                Receive weekly fleet summary
              </p>
            </div>
            <Switch
              id="weekly-reports"
              checked={notifications.weeklyReports}
              onCheckedChange={() => handleToggle("weeklyReports")}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="monthly-reports">Monthly Reports</Label>
              <p className="text-sm text-muted-foreground">
                Receive monthly performance reports
              </p>
            </div>
            <Switch
              id="monthly-reports"
              checked={notifications.monthlyReports}
              onCheckedChange={() => handleToggle("monthlyReports")}
            />
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end">
        <Button onClick={handleSave}>Save Preferences</Button>
      </div>
    </div>
  );
}
