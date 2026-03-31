import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import DriverViolations from "@/components/DriverViolations";
import { useToast } from "@/components/ui/use-toast";
import { useState } from "react";
import Swal from "sweetalert2";
import {
  ArrowLeft,
  User,
  Phone,
  Mail,
  Calendar,
  FileText,
  MapPin,
  AlertTriangle,
  Award,
  Heart,
  Users,
  Car,
  Clock,
  Star,
  Trash2,
  Truck,
  Hash,
  Gauge,
  Pencil,
  Link2,
} from "lucide-react";

const DriverProfile = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [assignOpen, setAssignOpen] = useState(false);
  const [selectedVehicleId, setSelectedVehicleId] = useState<string>("");

  const { data: driver, isLoading, error } = useQuery({
    queryKey: ["driver-profile", id],
    queryFn: async () => {
      if (!id) throw new Error("Driver ID is required");
      return apiClient.getDriver(Number(id));
    },
    enabled: !!id,
  });

  // Fetch assigned vehicle details if driver has one
  const { data: assignedVehicle } = useQuery({
    queryKey: ["driver-vehicle", driver?.current_vehicle_id],
    queryFn: () => apiClient.getVehicle(Number(driver!.current_vehicle_id)),
    enabled: !!driver?.current_vehicle_id,
  });

  // Fetch all vehicles for the assign dialog
  const { data: allVehicles } = useQuery({
    queryKey: ["vehicles-for-assign"],
    queryFn: () => apiClient.getVehicles({ page_size: 200 }),
    enabled: assignOpen,
  });

  const assignMutation = useMutation({
    mutationFn: (vehicleId: number) => apiClient.assignVehicleToDriver(Number(id), vehicleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["driver-profile", id] });
      queryClient.invalidateQueries({ queryKey: ["driver-vehicle"] });
      queryClient.invalidateQueries({ queryKey: ["vehicles"] });
      toast({ title: "Vehicle assigned successfully" });
      setAssignOpen(false);
      setSelectedVehicleId("");
    },
    onError: (e: any) =>
      toast({ title: "Error assigning vehicle", description: e.message, variant: "destructive" }),
  });

  const deleteMutation = useMutation({
    mutationFn: () => apiClient.deleteDriver(Number(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["drivers"] });
      toast({ title: "Driver deleted successfully" });
      navigate("/drivers");
    },
    onError: (e: any) =>
      toast({ title: "Error deleting driver", description: e.message, variant: "destructive" }),
  });

  const handleDelete = () => {
    Swal.fire({
      title: "Delete Driver?",
      text: `This will permanently remove ${driver?.name || "this driver"} from the system.`,
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#ef4444",
      cancelButtonColor: "#6b7280",
      confirmButtonText: "Yes, delete",
      cancelButtonText: "Cancel",
    }).then((result) => {
      if (result.isConfirmed) deleteMutation.mutate();
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "bg-green-100 text-green-800";
      case "inactive": return "bg-gray-100 text-gray-800";
      case "on_leave": return "bg-yellow-100 text-yellow-800";
      case "suspended": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const isExpiringSoon = (dateString?: string) => {
    if (!dateString) return false;
    const diff = new Date(dateString).getTime() - Date.now();
    const days = Math.ceil(diff / (1000 * 60 * 60 * 24));
    return days <= 30 && days > 0;
  };

  const isExpired = (dateString?: string) => {
    if (!dateString) return false;
    return new Date(dateString) < new Date();
  };

  const fmt = (val?: string | null, fallback = "Not provided") =>
    val && val.trim() ? val : fallback;

  const fmtDate = (val?: string | null) => {
    if (!val) return "Not provided";
    try { return new Date(val).toLocaleDateString(); } catch { return val; }
  };

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto" />
          <p className="mt-2 text-muted-foreground">Loading driver profile...</p>
        </div>
      </div>
    );
  }

  if (error || !driver) {
    return (
      <div className="p-6 flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-destructive">Error loading driver profile</p>
          <Button onClick={() => navigate("/drivers")} className="mt-4">Back to Drivers</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="outline" size="sm" onClick={() => navigate("/drivers")}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Drivers
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Driver Profile</h1>
            <p className="text-muted-foreground">Complete driver information</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => setAssignOpen(true)}>
            <Link2 className="w-4 h-4 mr-2" />
            Assign Vehicle
          </Button>
          <Button variant="outline" size="sm" onClick={() => navigate(`/drivers/edit/${id}`)}>
            <Pencil className="w-4 h-4 mr-2" />
            Edit Driver
          </Button>
          <Button
            variant="destructive"
            size="sm"
            onClick={handleDelete}
            disabled={deleteMutation.isPending}
          >
            <Trash2 className="w-4 h-4 mr-2" />
            {deleteMutation.isPending ? "Deleting..." : "Delete"}
          </Button>
        </div>
      </div>

      {/* Assign Vehicle Dialog */}
      <Dialog open={assignOpen} onOpenChange={setAssignOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Assign Vehicle to {driver.name}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 pt-2">
            <Select value={selectedVehicleId} onValueChange={setSelectedVehicleId}>
              <SelectTrigger>
                <SelectValue placeholder="Select a vehicle..." />
              </SelectTrigger>
              <SelectContent>
                {allVehicles?.items?.map((v: any) => (
                  <SelectItem key={v.id} value={String(v.id)}>
                    {v.registration_number} — {v.make} {v.model_name || v.model}
                    {v.driver_id && v.driver_id !== Number(id) ? " (assigned)" : ""}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setAssignOpen(false)}>Cancel</Button>
              <Button
                disabled={!selectedVehicleId || assignMutation.isPending}
                onClick={() => assignMutation.mutate(Number(selectedVehicleId))}
              >
                {assignMutation.isPending ? "Assigning..." : "Assign"}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Driver Header Card */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-6">
              <Avatar className="h-20 w-20">
                <AvatarImage src={driver.avatar_url} />
                <AvatarFallback className="text-xl">
                  {(driver.name || "?").split(" ").map((n: string) => n[0]).join("")}
                </AvatarFallback>
              </Avatar>
              <div>
                <h2 className="text-2xl font-bold">{driver.name}</h2>
                <div className="flex items-center gap-4 mt-2 flex-wrap">
                  <Badge className={getStatusColor(driver.status)}>
                    {(driver.status || "active").replace("_", " ").toUpperCase()}
                  </Badge>
                  <div className="flex items-center gap-1 text-muted-foreground text-sm">
                    <Calendar className="h-4 w-4" />
                    <span>Joined {fmtDate(driver.created_at)}</span>
                  </div>
                  <div className="flex items-center gap-1 text-muted-foreground text-sm">
                    <Award className="h-4 w-4" />
                    <span>{driver.years_experience || 0} yrs experience</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Assigned Vehicle Summary */}
            <div className="text-right">
              <p className="text-sm text-muted-foreground mb-1">Assigned Vehicle</p>
              {assignedVehicle ? (
                <div className="text-right">
                  <p className="font-semibold">{assignedVehicle.registration_number}</p>
                  <p className="text-sm text-muted-foreground">
                    {assignedVehicle.make} {assignedVehicle.model_name || assignedVehicle.model}
                  </p>
                  <Badge className="mt-1 bg-green-100 text-green-800">Assigned</Badge>
                </div>
              ) : (
                <Badge variant="secondary">Not Assigned</Badge>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Tabs defaultValue="personal" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="personal">Personal</TabsTrigger>
          <TabsTrigger value="license">License & Permits</TabsTrigger>
          <TabsTrigger value="contacts">Emergency Contacts</TabsTrigger>
          <TabsTrigger value="vehicle">Vehicle</TabsTrigger>
          <TabsTrigger value="violations">Violations</TabsTrigger>
        </TabsList>

        {/* Personal Info */}
        <TabsContent value="personal" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5" />
                  Personal Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {[
                  { label: "Full Name", value: driver.name },
                  { label: "National ID", value: fmt(driver.national_id) },
                  { label: "Date of Birth", value: fmtDate(driver.date_of_birth) },
                  { label: "Blood Group", value: fmt(driver.blood_group) },
                ].map(({ label, value }) => (
                  <div key={label}>
                    <p className="text-xs font-medium text-muted-foreground">{label}</p>
                    <p className="font-medium">{value}</p>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Phone className="h-5 w-5" />
                  Contact Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {[
                  { label: "Phone", value: fmt(driver.phone) },
                  { label: "Email", value: fmt(driver.email) },
                  { label: "Address", value: fmt(driver.address) },
                  { label: "Previous Employer", value: fmt(driver.previous_employer) },
                ].map(({ label, value }) => (
                  <div key={label}>
                    <p className="text-xs font-medium text-muted-foreground">{label}</p>
                    <p className="font-medium">{value}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* License & Permits */}
        <TabsContent value="license" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Driving License
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-xs font-medium text-muted-foreground">License Number</p>
                  <p className="font-medium">{fmt(driver.license_number)}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-muted-foreground">License Class</p>
                  <p className="font-medium">{fmt(driver.license_class)}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-muted-foreground">Expiry Date</p>
                  <div className="flex items-center gap-2">
                    <p className="font-medium">{fmtDate(driver.license_expiry)}</p>
                    {isExpired(driver.license_expiry) && <Badge variant="destructive">Expired</Badge>}
                    {!isExpired(driver.license_expiry) && isExpiringSoon(driver.license_expiry) && (
                      <Badge className="bg-yellow-100 text-yellow-800">Expiring Soon</Badge>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Car className="h-5 w-5" />
                  PSV Badge & Medical
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-xs font-medium text-muted-foreground">PSV Badge Number</p>
                  <p className="font-medium">{fmt(driver.psv_badge_number, "Not applicable")}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-muted-foreground">PSV Badge Expiry</p>
                  <div className="flex items-center gap-2">
                    <p className="font-medium">{fmtDate(driver.psv_badge_expiry)}</p>
                    {isExpired(driver.psv_badge_expiry) && <Badge variant="destructive">Expired</Badge>}
                    {!isExpired(driver.psv_badge_expiry) && isExpiringSoon(driver.psv_badge_expiry) && (
                      <Badge className="bg-yellow-100 text-yellow-800">Expiring Soon</Badge>
                    )}
                  </div>
                </div>
                <div>
                  <p className="text-xs font-medium text-muted-foreground">Medical Certificate Expiry</p>
                  <div className="flex items-center gap-2">
                    <p className="font-medium">{fmtDate(driver.medical_certificate_expiry)}</p>
                    {isExpired(driver.medical_certificate_expiry) && <Badge variant="destructive">Expired</Badge>}
                    {!isExpired(driver.medical_certificate_expiry) && isExpiringSoon(driver.medical_certificate_expiry) && (
                      <Badge className="bg-yellow-100 text-yellow-800">Expiring Soon</Badge>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Emergency Contacts */}
        <TabsContent value="contacts" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5" />
                  Emergency Contact
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-xs font-medium text-muted-foreground">Name</p>
                  <p className="font-medium">{fmt(driver.emergency_contact_name)}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-muted-foreground">Phone</p>
                  <p className="font-medium">{fmt(driver.emergency_contact_phone)}</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  Next of Kin
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-xs font-medium text-muted-foreground">Name</p>
                  <p className="font-medium">{fmt(driver.next_of_kin_name)}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-muted-foreground">Phone</p>
                  <p className="font-medium">{fmt(driver.next_of_kin_phone)}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-muted-foreground">Relationship</p>
                  <p className="font-medium capitalize">{fmt(driver.next_of_kin_relationship)}</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Assigned Vehicle */}
        <TabsContent value="vehicle" className="space-y-4">
          {assignedVehicle ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Truck className="h-5 w-5" />
                    Vehicle Details
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {[
                    { label: "Registration", value: assignedVehicle.registration_number },
                    { label: "Make", value: assignedVehicle.make },
                    { label: "Model", value: assignedVehicle.model_name || assignedVehicle.model },
                    { label: "Body Type", value: fmt(assignedVehicle.body_type) },
                    { label: "Fuel Type", value: fmt(assignedVehicle.fuel_type) },
                  ].map(({ label, value }) => (
                    <div key={label}>
                      <p className="text-xs font-medium text-muted-foreground">{label}</p>
                      <p className="font-medium">{value}</p>
                    </div>
                  ))}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Gauge className="h-5 w-5" />
                    Operational Info
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {[
                    { label: "Status", value: assignedVehicle.vehicle_status || assignedVehicle.status },
                    { label: "Current Odometer", value: assignedVehicle.current_odometer ? `${assignedVehicle.current_odometer.toLocaleString()} km` : "N/A" },
                    { label: "Max Load", value: assignedVehicle.max_load_weight ? `${assignedVehicle.max_load_weight.toLocaleString()} kg` : "N/A" },
                    { label: "Department", value: fmt(assignedVehicle.department) },
                    { label: "Chassis Number", value: fmt(assignedVehicle.chassis_number || assignedVehicle.vin_number) },
                  ].map(({ label, value }) => (
                    <div key={label}>
                      <p className="text-xs font-medium text-muted-foreground">{label}</p>
                      <p className="font-medium capitalize">{value}</p>
                    </div>
                  ))}
                </CardContent>
              </Card>

              <Card className="md:col-span-2">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Hash className="h-5 w-5" />
                    Insurance & Compliance
                  </CardTitle>
                </CardHeader>
                <CardContent className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {[
                    { label: "Insurance Provider", value: fmt(assignedVehicle.insurance_provider) },
                    { label: "Policy Number", value: fmt(assignedVehicle.insurance_policy_number) },
                    { label: "Insurance Expiry", value: fmtDate(assignedVehicle.insurance_expiry) },
                    { label: "Tracking Device", value: fmt(assignedVehicle.tracking_device_id || assignedVehicle.device_imei) },
                  ].map(({ label, value }) => (
                    <div key={label}>
                      <p className="text-xs font-medium text-muted-foreground">{label}</p>
                      <p className="font-medium">{value}</p>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          ) : (
            <Card>
              <CardContent className="py-16 text-center">
                <Truck className="w-16 h-16 mx-auto mb-4 text-muted-foreground opacity-30" />
                <p className="text-lg font-medium text-muted-foreground">No vehicle assigned</p>
                <p className="text-sm text-muted-foreground mt-1">
                  This driver has not been assigned to any vehicle yet.
                </p>
                <Button
                  className="mt-4"
                  variant="outline"
                  onClick={() => navigate("/vehicles")}
                >
                  Go to Vehicles
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Violations */}
        <TabsContent value="violations" className="space-y-4">
          <DriverViolations driverId={driver.id} driverName={driver.name} />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default DriverProfile;
