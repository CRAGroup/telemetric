import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/components/ui/use-toast";
import { ArrowLeft, User, Phone, Mail, Calendar, FileText, MapPin, Save } from "lucide-react";

interface DriverFormData {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  national_id: string;
  date_of_birth: string;
  license_number: string;
  license_class: string;
  license_expiry: string;
  medical_certificate_expiry: string;
  psv_badge_number: string;
  psv_badge_expiry: string;
  address: string;
  blood_group: string;
  emergency_contact_name: string;
  emergency_contact_phone: string;
  next_of_kin_name: string;
  next_of_kin_phone: string;
  next_of_kin_relationship: string;
  years_experience: string;
  previous_employer: string;
  status: string;
}

const EMPTY: DriverFormData = {
  first_name: "", last_name: "", email: "", phone: "", national_id: "",
  date_of_birth: "", license_number: "", license_class: "", license_expiry: "",
  medical_certificate_expiry: "", psv_badge_number: "", psv_badge_expiry: "",
  address: "", blood_group: "", emergency_contact_name: "", emergency_contact_phone: "",
  next_of_kin_name: "", next_of_kin_phone: "", next_of_kin_relationship: "",
  years_experience: "", previous_employer: "", status: "active",
};

const toDateInput = (val?: string | null) => {
  if (!val) return "";
  try { return new Date(val).toISOString().split("T")[0]; } catch { return ""; }
};

const EditDriver = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [form, setForm] = useState<DriverFormData>(EMPTY);

  const { data: driver, isLoading } = useQuery({
    queryKey: ["driver-edit", id],
    queryFn: () => apiClient.getDriver(Number(id)),
    enabled: !!id,
  });

  // Populate form once driver data arrives
  useEffect(() => {
    if (!driver) return;
    setForm({
      first_name: driver.first_name || "",
      last_name: driver.last_name || "",
      email: driver.email || "",
      phone: driver.phone || driver.phone_number || "",
      national_id: driver.national_id || "",
      date_of_birth: toDateInput(driver.date_of_birth),
      license_number: driver.license_number || "",
      license_class: driver.license_class || "",
      license_expiry: toDateInput(driver.license_expiry),
      medical_certificate_expiry: toDateInput(driver.medical_certificate_expiry),
      psv_badge_number: driver.psv_badge_number || "",
      psv_badge_expiry: toDateInput(driver.psv_badge_expiry),
      address: driver.address || "",
      blood_group: driver.blood_group || "",
      emergency_contact_name: driver.emergency_contact_name || "",
      emergency_contact_phone: driver.emergency_contact_phone || "",
      next_of_kin_name: driver.next_of_kin_name || "",
      next_of_kin_phone: driver.next_of_kin_phone || "",
      next_of_kin_relationship: driver.next_of_kin_relationship || "",
      years_experience: driver.years_experience ? String(driver.years_experience) : "",
      previous_employer: driver.previous_employer || "",
      status: driver.status || "active",
    });
  }, [driver]);

  const set = (field: keyof DriverFormData, value: string) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const mutation = useMutation({
    mutationFn: (data: any) => apiClient.updateDriver(Number(id), data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["driver-profile", id] });
      queryClient.invalidateQueries({ queryKey: ["drivers"] });
      toast({ title: "Driver updated successfully" });
      navigate(`/driver-profile/${id}`);
    },
    onError: (e: any) =>
      toast({ title: "Error updating driver", description: e.message, variant: "destructive" }),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.first_name || !form.last_name || !form.license_number) {
      toast({ title: "Required fields missing", description: "First name, last name and license number are required.", variant: "destructive" });
      return;
    }
    mutation.mutate({
      first_name: form.first_name,
      last_name: form.last_name,
      email: form.email || undefined,
      phone: form.phone || undefined,
      national_id: form.national_id || undefined,
      date_of_birth: form.date_of_birth || undefined,
      license_number: form.license_number,
      license_class: form.license_class || undefined,
      license_expiry: form.license_expiry || undefined,
      medical_certificate_expiry: form.medical_certificate_expiry || undefined,
      psv_badge_number: form.psv_badge_number || undefined,
      psv_badge_expiry: form.psv_badge_expiry || undefined,
      address: form.address || undefined,
      blood_group: form.blood_group || undefined,
      emergency_contact_name: form.emergency_contact_name || undefined,
      emergency_contact_phone: form.emergency_contact_phone || undefined,
      next_of_kin_name: form.next_of_kin_name || undefined,
      next_of_kin_phone: form.next_of_kin_phone || undefined,
      next_of_kin_relationship: form.next_of_kin_relationship || undefined,
      years_experience: form.years_experience ? Number(form.years_experience) : undefined,
      previous_employer: form.previous_employer || undefined,
      status: form.status,
    });
  };

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center space-x-4">
        <Button variant="outline" size="sm" onClick={() => navigate(`/driver-profile/${id}`)}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Profile
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Edit Driver</h1>
          <p className="text-muted-foreground">Update driver information</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">

            {/* Personal Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2"><User className="w-5 h-5" />Personal Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>First Name *</Label>
                    <Input value={form.first_name} onChange={(e) => set("first_name", e.target.value)} placeholder="John" required />
                  </div>
                  <div>
                    <Label>Last Name *</Label>
                    <Input value={form.last_name} onChange={(e) => set("last_name", e.target.value)} placeholder="Doe" required />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>National ID</Label>
                    <Input value={form.national_id} onChange={(e) => set("national_id", e.target.value)} placeholder="12345678" />
                  </div>
                  <div>
                    <Label>Date of Birth</Label>
                    <Input type="date" value={form.date_of_birth} onChange={(e) => set("date_of_birth", e.target.value)} />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Email</Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                      <Input type="email" value={form.email} onChange={(e) => set("email", e.target.value)} className="pl-9" placeholder="john@example.com" />
                    </div>
                  </div>
                  <div>
                    <Label>Phone</Label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                      <Input value={form.phone} onChange={(e) => set("phone", e.target.value)} className="pl-9" placeholder="+254 712 345 678" />
                    </div>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Blood Group</Label>
                    <Select value={form.blood_group} onValueChange={(v) => set("blood_group", v)}>
                      <SelectTrigger><SelectValue placeholder="Select" /></SelectTrigger>
                      <SelectContent>
                        {["A+","A-","B+","B-","AB+","AB-","O+","O-"].map((g) => (
                          <SelectItem key={g} value={g}>{g}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Status</Label>
                    <Select value={form.status} onValueChange={(v) => set("status", v)}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="active">Active</SelectItem>
                        <SelectItem value="inactive">Inactive</SelectItem>
                        <SelectItem value="on_leave">On Leave</SelectItem>
                        <SelectItem value="suspended">Suspended</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div>
                  <Label>Address</Label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <Input value={form.address} onChange={(e) => set("address", e.target.value)} className="pl-9" placeholder="123 Main Street, Nairobi" />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* License */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2"><FileText className="w-5 h-5" />License & Permits</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>License Number *</Label>
                    <Input value={form.license_number} onChange={(e) => set("license_number", e.target.value)} placeholder="DL001234567" required />
                  </div>
                  <div>
                    <Label>License Class</Label>
                    <Select value={form.license_class} onValueChange={(v) => set("license_class", v)}>
                      <SelectTrigger><SelectValue placeholder="Select class" /></SelectTrigger>
                      <SelectContent>
                        {["A","B","C","D","E","F"].map((c) => (
                          <SelectItem key={c} value={c}>Class {c}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>License Expiry</Label>
                    <div className="relative">
                      <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                      <Input type="date" value={form.license_expiry} onChange={(e) => set("license_expiry", e.target.value)} className="pl-9" />
                    </div>
                  </div>
                  <div>
                    <Label>Medical Certificate Expiry</Label>
                    <Input type="date" value={form.medical_certificate_expiry} onChange={(e) => set("medical_certificate_expiry", e.target.value)} />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>PSV Badge Number</Label>
                    <Input value={form.psv_badge_number} onChange={(e) => set("psv_badge_number", e.target.value)} placeholder="PSV001234" />
                  </div>
                  <div>
                    <Label>PSV Badge Expiry</Label>
                    <Input type="date" value={form.psv_badge_expiry} onChange={(e) => set("psv_badge_expiry", e.target.value)} />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right column */}
          <div className="space-y-6">
            {/* Emergency Contact */}
            <Card>
              <CardHeader><CardTitle>Emergency Contact</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Contact Name</Label>
                  <Input value={form.emergency_contact_name} onChange={(e) => set("emergency_contact_name", e.target.value)} placeholder="Jane Doe" />
                </div>
                <div>
                  <Label>Contact Phone</Label>
                  <Input value={form.emergency_contact_phone} onChange={(e) => set("emergency_contact_phone", e.target.value)} placeholder="+254 723 456 789" />
                </div>
              </CardContent>
            </Card>

            {/* Next of Kin */}
            <Card>
              <CardHeader><CardTitle>Next of Kin</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Name</Label>
                  <Input value={form.next_of_kin_name} onChange={(e) => set("next_of_kin_name", e.target.value)} placeholder="Mary Doe" />
                </div>
                <div>
                  <Label>Phone</Label>
                  <Input value={form.next_of_kin_phone} onChange={(e) => set("next_of_kin_phone", e.target.value)} placeholder="+254 734 567 890" />
                </div>
                <div>
                  <Label>Relationship</Label>
                  <Select value={form.next_of_kin_relationship} onValueChange={(v) => set("next_of_kin_relationship", v)}>
                    <SelectTrigger><SelectValue placeholder="Select" /></SelectTrigger>
                    <SelectContent>
                      {["spouse","parent","child","sibling","other"].map((r) => (
                        <SelectItem key={r} value={r} className="capitalize">{r}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Experience */}
            <Card>
              <CardHeader><CardTitle>Experience</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Years of Experience</Label>
                  <Input type="number" min="0" max="50" value={form.years_experience} onChange={(e) => set("years_experience", e.target.value)} placeholder="5" />
                </div>
                <div>
                  <Label>Previous Employer</Label>
                  <Input value={form.previous_employer} onChange={(e) => set("previous_employer", e.target.value)} placeholder="ABC Transport Ltd" />
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        <div className="flex justify-end gap-4">
          <Button type="button" variant="outline" onClick={() => navigate(`/driver-profile/${id}`)}>Cancel</Button>
          <Button type="submit" disabled={mutation.isPending}>
            <Save className="w-4 h-4 mr-2" />
            {mutation.isPending ? "Saving..." : "Save Changes"}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default EditDriver;
