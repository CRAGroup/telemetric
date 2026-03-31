import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { useToast } from "@/components/ui/use-toast";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Calendar, Clock, Plus, User, ChevronLeft, ChevronRight } from "lucide-react";

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

const SHIFTS = [
  { value: "morning", label: "Morning (06-14)", color: "bg-blue-100 text-blue-800" },
  { value: "afternoon", label: "Afternoon (14-22)", color: "bg-orange-100 text-orange-800" },
  { value: "night", label: "Night (22-06)", color: "bg-purple-100 text-purple-800" },
  { value: "off", label: "Day Off", color: "bg-gray-100 text-gray-500" },
];

type Schedule = Record<string, Record<string, string>>;

const getWeekDates = (offset: number) => {
  const now = new Date();
  const day = now.getDay();
  const monday = new Date(now);
  monday.setDate(now.getDate() - (day === 0 ? 6 : day - 1) + offset * 7);
  return DAYS.map((_, i) => {
    const d = new Date(monday);
    d.setDate(monday.getDate() + i);
    return d;
  });
};

export default function DriverSchedules() {
  const { toast } = useToast();
  const [weekOffset, setWeekOffset] = useState(0);
  const [schedules, setSchedules] = useState<Schedule>({});
  const [dialogOpen, setDialogOpen] = useState(false);
  const [form, setForm] = useState({ driver_id: "", day: "Mon", shift: "morning" });

  const { data: driversData, isLoading } = useQuery({
    queryKey: ["drivers"],
    queryFn: () => apiClient.getDrivers({ page_size: 100 }),
    staleTime: 5 * 60_000,
  });

  const drivers = driversData?.items || [];
  const weekDates = getWeekDates(weekOffset);

  const getShift = (driverId: string, day: string) => schedules[driverId]?.[day] || "off";

  const setShift = (driverId: string, day: string, shift: string) => {
    setSchedules((prev) => ({
      ...prev,
      [driverId]: { ...(prev[driverId] || {}), [day]: shift },
    }));
  };

  const handleAssign = () => {
    if (!form.driver_id) {
      toast({ title: "Select a driver", variant: "destructive" });
      return;
    }
    setShift(form.driver_id, form.day, form.shift);
    toast({ title: "Shift assigned" });
    setDialogOpen(false);
  };

  const shiftCfg = (shift: string) => SHIFTS.find((s) => s.value === shift) || SHIFTS[3];
  const scheduledCount = Object.keys(schedules).length;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Driver Schedules</h1>
          <p className="text-muted-foreground">Manage driver shifts and weekly availability</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="w-4 h-4 mr-2" />Assign Shift</Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-md">
            <DialogHeader><DialogTitle>Assign Shift</DialogTitle></DialogHeader>
            <div className="space-y-4 pt-2">
              <div>
                <Label>Driver</Label>
                <Select value={form.driver_id} onValueChange={(v) => setForm((p) => ({ ...p, driver_id: v }))}>
                  <SelectTrigger><SelectValue placeholder="Select driver" /></SelectTrigger>
                  <SelectContent>
                    {drivers.map((d: any) => (
                      <SelectItem key={d.id} value={String(d.id)}>
                        {d.name || `${d.first_name} ${d.last_name}`}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Day</Label>
                <Select value={form.day} onValueChange={(v) => setForm((p) => ({ ...p, day: v }))}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {DAYS.map((d) => <SelectItem key={d} value={d}>{d}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Shift</Label>
                <Select value={form.shift} onValueChange={(v) => setForm((p) => ({ ...p, shift: v }))}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {SHIFTS.map((s) => <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
                <Button onClick={handleAssign}>Assign</Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Total Drivers", value: drivers.length, icon: User, color: "text-blue-500" },
          { label: "Active", value: drivers.filter((d: any) => d.status === "active").length, icon: User, color: "text-green-500" },
          { label: "Scheduled", value: scheduledCount, icon: Calendar, color: "text-purple-500" },
          { label: "Unscheduled", value: Math.max(0, drivers.length - scheduledCount), icon: Clock, color: "text-orange-500" },
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

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />Weekly Schedule
            </CardTitle>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" className="h-8 w-8 p-0" onClick={() => setWeekOffset((p) => p - 1)}>
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <span className="text-sm font-medium min-w-[160px] text-center">
                {weekDates[0].toLocaleDateString("en-GB", { day: "numeric", month: "short" })}
                {" - "}
                {weekDates[6].toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" })}
              </span>
              <Button variant="outline" size="sm" className="h-8 w-8 p-0" onClick={() => setWeekOffset((p) => p + 1)}>
                <ChevronRight className="h-4 w-4" />
              </Button>
              {weekOffset !== 0 && (
                <Button variant="ghost" size="sm" className="h-8 text-xs" onClick={() => setWeekOffset(0)}>Today</Button>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => <div key={i} className="h-12 bg-muted animate-pulse rounded" />)}
            </div>
          ) : drivers.length === 0 ? (
            <div className="text-center py-10 text-muted-foreground">
              <User className="h-10 w-10 mx-auto mb-3 opacity-30" />
              <p>No drivers found.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr>
                    <th className="text-left py-2 pr-4 font-medium text-muted-foreground w-44">Driver</th>
                    {DAYS.map((day, i) => (
                      <th key={day} className="text-center py-2 px-1 font-medium min-w-[110px]">
                        <div>{day}</div>
                        <div className="text-xs text-muted-foreground font-normal">
                          {weekDates[i].getDate()}/{weekDates[i].getMonth() + 1}
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {drivers.map((driver: any) => (
                    <tr key={driver.id} className="border-t hover:bg-muted/20">
                      <td className="py-2 pr-4">
                        <div className="flex items-center gap-2">
                          <Avatar className="h-7 w-7">
                            <AvatarImage src={driver.avatar_url} />
                            <AvatarFallback className="text-xs">
                              {(driver.name || `${driver.first_name} ${driver.last_name}`).split(" ").map((n: string) => n[0]).join("")}
                            </AvatarFallback>
                          </Avatar>
                          <p className="font-medium text-xs leading-tight truncate max-w-[100px]">
                            {driver.name || `${driver.first_name} ${driver.last_name}`}
                          </p>
                        </div>
                      </td>
                      {DAYS.map((day) => {
                        const shift = getShift(String(driver.id), day);
                        const cfg = shiftCfg(shift);
                        return (
                          <td key={day} className="py-1 px-1">
                            <Select value={shift} onValueChange={(v) => setShift(String(driver.id), day, v)}>
                              <SelectTrigger className={`h-7 text-xs border-0 ${cfg.color}`}>
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                {SHIFTS.map((s) => (
                                  <SelectItem key={s.value} value={s.value} className="text-xs">{s.label}</SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="flex items-center gap-3 flex-wrap">
        <span className="text-sm text-muted-foreground">Legend:</span>
        {SHIFTS.map((s) => (
          <Badge key={s.value} className={`text-xs ${s.color}`}>{s.label}</Badge>
        ))}
      </div>
    </div>
  );
}
