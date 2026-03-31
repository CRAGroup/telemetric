import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { useToast } from "@/components/ui/use-toast";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import {
  Wrench,
  Calendar,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Plus,
  Search,
} from "lucide-react";

const maintenanceSchema = z.object({
  vehicle_id: z.string().min(1, "Vehicle is required"),
  service_type: z.string().min(2, "Service type is required"),
  description: z.string().optional(),
  service_date: z.string().min(1, "Date is required"),
  cost: z.string().optional(),
  mechanic: z.string().optional(),
  priority: z.enum(["low", "medium", "high", "critical"]).default("medium"),
  record_type: z.enum(["scheduled", "emergency", "inspection"]).default("scheduled"),
  status: z.enum(["pending", "in_progress", "completed", "overdue"]).default("pending"),
});

const Maintenance = () => {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTab, setActiveTab] = useState("all");
  const [dialogOpen, setDialogOpen] = useState(false);

  const form = useForm<z.infer<typeof maintenanceSchema>>({
    resolver: zodResolver(maintenanceSchema),
    defaultValues: {
      vehicle_id: "",
      service_type: "",
      description: "",
      service_date: new Date().toISOString().split("T")[0],
      cost: "",
      mechanic: "",
      priority: "medium",
      record_type: "scheduled",
      status: "pending",
    },
  });

  const { data: statsData } = useQuery({
    queryKey: ["maintenance-stats"],
    queryFn: () => apiClient.getMaintenanceStats(),
  });

  const { data: maintenanceData, isLoading } = useQuery({
    queryKey: ["maintenance", activeTab, searchQuery],
    queryFn: () =>
      apiClient.getMaintenance({
        status_filter: activeTab !== "all" ? activeTab : undefined,
        q: searchQuery || undefined,
        page_size: 100,
      }),
  });

  const { data: vehiclesData } = useQuery({
    queryKey: ["vehicles-list"],
    queryFn: () => apiClient.getVehicles({ page_size: 200 }),
  });

  const createMutation = useMutation({
    mutationFn: (values: z.infer<typeof maintenanceSchema>) =>
      apiClient.createMaintenance({
        ...values,
        vehicle_id: Number(values.vehicle_id),
        cost: values.cost ? Number(values.cost) : undefined,
      }),
    onSuccess: () => {
      toast({ title: "Maintenance record created" });
      queryClient.invalidateQueries({ queryKey: ["maintenance"] });
      queryClient.invalidateQueries({ queryKey: ["maintenance-stats"] });
      form.reset();
      setDialogOpen(false);
    },
    onError: (e: any) => toast({ title: "Error", description: e.message, variant: "destructive" }),
  });

  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      apiClient.updateMaintenance(id, { status }),
    onSuccess: () => {
      toast({ title: "Status updated" });
      queryClient.invalidateQueries({ queryKey: ["maintenance"] });
      queryClient.invalidateQueries({ queryKey: ["maintenance-stats"] });
    },
    onError: (e: any) => toast({ title: "Error", description: e.message, variant: "destructive" }),
  });

  const stats = statsData || { total: 0, pending: 0, in_progress: 0, overdue: 0, completed: 0 };
  const records = maintenanceData?.items || [];

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed": return "bg-green-100 text-green-800";
      case "in_progress": return "bg-blue-100 text-blue-800";
      case "pending": return "bg-yellow-100 text-yellow-800";
      case "overdue": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getPriorityDot = (priority: string) => {
    switch (priority) {
      case "critical": return "bg-red-500";
      case "high": return "bg-orange-500";
      case "medium": return "bg-yellow-500";
      default: return "bg-green-500";
    }
  };

  const nextStatus: Record<string, string> = {
    pending: "in_progress",
    in_progress: "completed",
    overdue: "in_progress",
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Maintenance Management</h1>
          <p className="text-muted-foreground">Track and manage vehicle maintenance schedules</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button><Plus className="w-4 h-4 mr-2" />Schedule Maintenance</Button>
          </DialogTrigger>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>Schedule Maintenance</DialogTitle>
            </DialogHeader>
            <Form {...form}>
              <form onSubmit={form.handleSubmit((v) => createMutation.mutate(v))} className="space-y-4">
                <FormField control={form.control} name="vehicle_id" render={({ field }) => (
                  <FormItem>
                    <FormLabel>Vehicle</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl><SelectTrigger><SelectValue placeholder="Select vehicle" /></SelectTrigger></FormControl>
                      <SelectContent>
                        {vehiclesData?.items?.map((v: any) => (
                          <SelectItem key={v.id} value={String(v.id)}>
                            {v.registration_number} - {v.make} {v.model_name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )} />
                <div className="grid grid-cols-2 gap-4">
                  <FormField control={form.control} name="service_type" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Service Type</FormLabel>
                      <FormControl><Input placeholder="Oil change, Brake repair..." {...field} /></FormControl>
                      <FormMessage />
                    </FormItem>
                  )} />
                  <FormField control={form.control} name="service_date" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Scheduled Date</FormLabel>
                      <FormControl><Input type="date" {...field} /></FormControl>
                      <FormMessage />
                    </FormItem>
                  )} />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <FormField control={form.control} name="record_type" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Type</FormLabel>
                      <Select onValueChange={field.onChange} value={field.value}>
                        <FormControl><SelectTrigger><SelectValue /></SelectTrigger></FormControl>
                        <SelectContent>
                          <SelectItem value="scheduled">Scheduled</SelectItem>
                          <SelectItem value="emergency">Emergency</SelectItem>
                          <SelectItem value="inspection">Inspection</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )} />
                  <FormField control={form.control} name="priority" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Priority</FormLabel>
                      <Select onValueChange={field.onChange} value={field.value}>
                        <FormControl><SelectTrigger><SelectValue /></SelectTrigger></FormControl>
                        <SelectContent>
                          <SelectItem value="low">Low</SelectItem>
                          <SelectItem value="medium">Medium</SelectItem>
                          <SelectItem value="high">High</SelectItem>
                          <SelectItem value="critical">Critical</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )} />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <FormField control={form.control} name="mechanic" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Mechanic</FormLabel>
                      <FormControl><Input placeholder="Mechanic name" {...field} /></FormControl>
                      <FormMessage />
                    </FormItem>
                  )} />
                  <FormField control={form.control} name="cost" render={({ field }) => (
                    <FormItem>
                      <FormLabel>Estimated Cost (KES)</FormLabel>
                      <FormControl><Input type="number" placeholder="5000" {...field} /></FormControl>
                      <FormMessage />
                    </FormItem>
                  )} />
                </div>
                <FormField control={form.control} name="description" render={({ field }) => (
                  <FormItem>
                    <FormLabel>Description</FormLabel>
                    <FormControl><Textarea placeholder="Details..." rows={3} {...field} /></FormControl>
                    <FormMessage />
                  </FormItem>
                )} />
                <div className="flex justify-end gap-2">
                  <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
                  <Button type="submit" disabled={createMutation.isPending}>
                    {createMutation.isPending ? "Saving..." : "Schedule"}
                  </Button>
                </div>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {[
          { label: "Total", value: stats.total, icon: Wrench, color: "text-blue-500" },
          { label: "Pending", value: stats.pending, icon: Clock, color: "text-yellow-500" },
          { label: "In Progress", value: stats.in_progress, icon: Wrench, color: "text-blue-500" },
          { label: "Overdue", value: stats.overdue, icon: AlertTriangle, color: "text-red-500" },
          { label: "Completed", value: stats.completed, icon: CheckCircle2, color: "text-green-500" },
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
            placeholder="Search maintenance records..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      {/* Records */}
      <Card>
        <CardHeader><CardTitle>Maintenance Records</CardTitle></CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList>
              <TabsTrigger value="all">All</TabsTrigger>
              <TabsTrigger value="pending">Pending</TabsTrigger>
              <TabsTrigger value="in_progress">In Progress</TabsTrigger>
              <TabsTrigger value="overdue">Overdue</TabsTrigger>
              <TabsTrigger value="completed">Completed</TabsTrigger>
            </TabsList>

            <TabsContent value={activeTab} className="mt-4">
              {isLoading ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-20 bg-muted animate-pulse rounded-lg" />
                  ))}
                </div>
              ) : records.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Wrench className="w-12 h-12 mx-auto mb-4 opacity-30" />
                  <p>No maintenance records found</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {records.map((record: any) => (
                    <div key={record.id} className="border rounded-lg p-4 hover:bg-accent/5 transition-colors">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <div className={`w-3 h-3 rounded-full ${getPriorityDot(record.priority)}`} />
                            <h3 className="font-semibold">{record.vehicle_name || `Vehicle #${record.vehicle_id}`}</h3>
                            <Badge className={getStatusColor(record.status)}>
                              {record.status?.replace("_", " ")}
                            </Badge>
                            <Badge variant="outline">{record.type || record.record_type}</Badge>
                          </div>
                          <p className="text-sm font-medium mb-1">{record.service_type}</p>
                          {record.description && (
                            <p className="text-sm text-muted-foreground mb-2">{record.description}</p>
                          )}
                          <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                            <div className="flex items-center space-x-1">
                              <Calendar className="w-3 h-3" />
                              <span>Scheduled: {record.scheduledDate || record.service_date}</span>
                            </div>
                            {record.completedDate && (
                              <div className="flex items-center space-x-1">
                                <CheckCircle2 className="w-3 h-3" />
                                <span>Completed: {record.completedDate}</span>
                              </div>
                            )}
                            {record.mechanic && <span>Mechanic: {record.mechanic}</span>}
                            {record.cost && <span>Cost: KES {Number(record.cost).toLocaleString()}</span>}
                          </div>
                        </div>
                        <div className="flex space-x-2 ml-4">
                          {record.status !== "completed" && nextStatus[record.status] && (
                            <Button
                              size="sm"
                              onClick={() => updateStatusMutation.mutate({ id: record.id, status: nextStatus[record.status] })}
                              disabled={updateStatusMutation.isPending}
                            >
                              {record.status === "pending" ? "Start" : "Complete"}
                            </Button>
                          )}
                        </div>
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
  );
};

export default Maintenance;
