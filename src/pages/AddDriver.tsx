import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiClient } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/components/ui/use-toast";
import { ArrowLeft, Upload, User, Phone, Mail, Calendar, FileText, MapPin } from "lucide-react";

interface DriverFormData {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  nationalId: string;
  dateOfBirth: string;
  licenseNumber: string;
  licenseClass: string;
  licenseExpiry: string;
  medicalCertificateExpiry: string;
  psvBadgeNumber: string;
  psvBadgeExpiry: string;
  address: string;
  city: string;
  bloodGroup: string;
  emergencyContact: string;
  emergencyPhone: string;
  nextOfKinName: string;
  nextOfKinPhone: string;
  nextOfKinRelationship: string;
  experience: string;
  previousEmployer: string;
  notes: string;
}

const AddDriver = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState<DriverFormData>({
    firstName: "",
    lastName: "",
    email: "",
    phone: "",
    nationalId: "",
    dateOfBirth: "",
    licenseNumber: "",
    licenseClass: "",
    licenseExpiry: "",
    medicalCertificateExpiry: "",
    psvBadgeNumber: "",
    psvBadgeExpiry: "",
    address: "",
    city: "",
    bloodGroup: "",
    emergencyContact: "",
    emergencyPhone: "",
    nextOfKinName: "",
    nextOfKinPhone: "",
    nextOfKinRelationship: "",
    experience: "",
    previousEmployer: "",
    notes: ""
  });

  const handleInputChange = (field: keyof DriverFormData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      // Validate required fields
      const requiredFields = ['firstName', 'lastName', 'email', 'phone', 'nationalId', 'licenseNumber', 'licenseExpiry'];
      const missingFields = requiredFields.filter(field => !formData[field as keyof DriverFormData]);
      
      if (missingFields.length > 0) {
        toast({
          title: "Missing Required Fields",
          description: `Please fill in: ${missingFields.join(', ')}`,
          variant: "destructive",
        });
        return;
      }

      // Create driver via API
      const driverData = {
        first_name: formData.firstName,
        last_name: formData.lastName,
        email: formData.email,
        phone: formData.phone,
        license_number: formData.licenseNumber,
        license_expiry: formData.licenseExpiry,
        license_class: formData.licenseClass || null,
        date_of_birth: formData.dateOfBirth || null,
        national_id: formData.nationalId,
        address: formData.address && formData.city ? `${formData.address}, ${formData.city}` : null,
        emergency_contact_name: formData.emergencyContact || null,
        emergency_contact_phone: formData.emergencyPhone || null,
        medical_certificate_expiry: formData.medicalCertificateExpiry || null,
        psv_badge_number: formData.psvBadgeNumber || null,
        psv_badge_expiry: formData.psvBadgeExpiry || null,
        years_experience: formData.experience ? parseInt(formData.experience.split('-')[0]) : null,
        previous_employer: formData.previousEmployer || null,
        blood_group: formData.bloodGroup || null,
        next_of_kin_name: formData.nextOfKinName || null,
        next_of_kin_phone: formData.nextOfKinPhone || null,
        next_of_kin_relationship: formData.nextOfKinRelationship || null,
        status: 'active'
      };

      await apiClient.createDriver(driverData);
      
      toast({
        title: "Driver Added Successfully",
        description: `${formData.firstName} ${formData.lastName} has been added to the system.`,
      });
      
      navigate("/drivers");
    } catch (error: any) {
      toast({
        title: "Error Adding Driver",
        description: error.message || "Failed to add driver. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Button variant="outline" size="sm" onClick={() => navigate("/drivers")}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Drivers
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Add New Driver</h1>
          <p className="text-muted-foreground">Enter driver information and documentation</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Personal Information */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <User className="w-5 h-5" />
                  <span>Personal Information</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="firstName">First Name *</Label>
                    <Input
                      id="firstName"
                      value={formData.firstName}
                      onChange={(e) => handleInputChange('firstName', e.target.value)}
                      placeholder="John"
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="lastName">Last Name *</Label>
                    <Input
                      id="lastName"
                      value={formData.lastName}
                      onChange={(e) => handleInputChange('lastName', e.target.value)}
                      placeholder="Doe"
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="nationalId">National ID Number *</Label>
                    <Input
                      id="nationalId"
                      value={formData.nationalId}
                      onChange={(e) => handleInputChange('nationalId', e.target.value)}
                      placeholder="12345678"
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="dateOfBirth">Date of Birth *</Label>
                    <Input
                      id="dateOfBirth"
                      type="date"
                      value={formData.dateOfBirth}
                      onChange={(e) => handleInputChange('dateOfBirth', e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="email">Email Address *</Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                      <Input
                        id="email"
                        type="email"
                        value={formData.email}
                        onChange={(e) => handleInputChange('email', e.target.value)}
                        placeholder="john.doe@example.com"
                        className="pl-9"
                        required
                      />
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="phone">Phone Number *</Label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                      <Input
                        id="phone"
                        value={formData.phone}
                        onChange={(e) => handleInputChange('phone', e.target.value)}
                        placeholder="+254 712 345 678"
                        className="pl-9"
                        required
                      />
                    </div>
                  </div>
                </div>

                <div>
                  <Label htmlFor="bloodGroup">Blood Group</Label>
                  <Select value={formData.bloodGroup} onValueChange={(value) => handleInputChange('bloodGroup', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select blood group" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="A+">A+</SelectItem>
                      <SelectItem value="A-">A-</SelectItem>
                      <SelectItem value="B+">B+</SelectItem>
                      <SelectItem value="B-">B-</SelectItem>
                      <SelectItem value="AB+">AB+</SelectItem>
                      <SelectItem value="AB-">AB-</SelectItem>
                      <SelectItem value="O+">O+</SelectItem>
                      <SelectItem value="O-">O-</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* License Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <FileText className="w-5 h-5" />
                  <span>License Information</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="licenseNumber">License Number *</Label>
                    <Input
                      id="licenseNumber"
                      value={formData.licenseNumber}
                      onChange={(e) => handleInputChange('licenseNumber', e.target.value)}
                      placeholder="DL001234567"
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="licenseClass">License Class</Label>
                    <Select value={formData.licenseClass} onValueChange={(value) => handleInputChange('licenseClass', value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select license class" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="A">Class A (Motorcycles)</SelectItem>
                        <SelectItem value="B">Class B (Light Vehicles)</SelectItem>
                        <SelectItem value="C">Class C (Medium Vehicles)</SelectItem>
                        <SelectItem value="D">Class D (Heavy Vehicles)</SelectItem>
                        <SelectItem value="E">Class E (Articulated Vehicles)</SelectItem>
                        <SelectItem value="F">Class F (Agricultural Tractors)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div>
                  <Label htmlFor="licenseExpiry">License Expiry Date *</Label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <Input
                      id="licenseExpiry"
                      type="date"
                      value={formData.licenseExpiry}
                      onChange={(e) => handleInputChange('licenseExpiry', e.target.value)}
                      className="pl-9"
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="psvBadgeNumber">PSV Badge Number</Label>
                    <Input
                      id="psvBadgeNumber"
                      value={formData.psvBadgeNumber}
                      onChange={(e) => handleInputChange('psvBadgeNumber', e.target.value)}
                      placeholder="PSV001234"
                    />
                  </div>
                  <div>
                    <Label htmlFor="psvBadgeExpiry">PSV Badge Expiry</Label>
                    <Input
                      id="psvBadgeExpiry"
                      type="date"
                      value={formData.psvBadgeExpiry}
                      onChange={(e) => handleInputChange('psvBadgeExpiry', e.target.value)}
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="medicalCertificateExpiry">Medical Certificate Expiry</Label>
                  <Input
                    id="medicalCertificateExpiry"
                    type="date"
                    value={formData.medicalCertificateExpiry}
                    onChange={(e) => handleInputChange('medicalCertificateExpiry', e.target.value)}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Address Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <MapPin className="w-5 h-5" />
                  <span>Address Information</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="address">Street Address</Label>
                  <Input
                    id="address"
                    value={formData.address}
                    onChange={(e) => handleInputChange('address', e.target.value)}
                    placeholder="123 Main Street"
                  />
                </div>
                <div>
                  <Label htmlFor="city">City</Label>
                  <Input
                    id="city"
                    value={formData.city}
                    onChange={(e) => handleInputChange('city', e.target.value)}
                    placeholder="Nairobi"
                  />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            {/* Profile Photo */}
            <Card>
              <CardHeader>
                <CardTitle>Profile Photo</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col items-center space-y-4">
                  <div className="w-32 h-32 rounded-full bg-muted flex items-center justify-center">
                    <User className="w-16 h-16 text-muted-foreground" />
                  </div>
                  <Button variant="outline" size="sm">
                    <Upload className="w-4 h-4 mr-2" />
                    Upload Photo
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Emergency Contact */}
            <Card>
              <CardHeader>
                <CardTitle>Emergency Contact</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="emergencyContact">Contact Name</Label>
                  <Input
                    id="emergencyContact"
                    value={formData.emergencyContact}
                    onChange={(e) => handleInputChange('emergencyContact', e.target.value)}
                    placeholder="Jane Doe"
                  />
                </div>
                <div>
                  <Label htmlFor="emergencyPhone">Contact Phone</Label>
                  <Input
                    id="emergencyPhone"
                    value={formData.emergencyPhone}
                    onChange={(e) => handleInputChange('emergencyPhone', e.target.value)}
                    placeholder="+254 723 456 789"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Next of Kin */}
            <Card>
              <CardHeader>
                <CardTitle>Next of Kin</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="nextOfKinName">Next of Kin Name</Label>
                  <Input
                    id="nextOfKinName"
                    value={formData.nextOfKinName}
                    onChange={(e) => handleInputChange('nextOfKinName', e.target.value)}
                    placeholder="Mary Doe"
                  />
                </div>
                <div>
                  <Label htmlFor="nextOfKinPhone">Next of Kin Phone</Label>
                  <Input
                    id="nextOfKinPhone"
                    value={formData.nextOfKinPhone}
                    onChange={(e) => handleInputChange('nextOfKinPhone', e.target.value)}
                    placeholder="+254 734 567 890"
                  />
                </div>
                <div>
                  <Label htmlFor="nextOfKinRelationship">Relationship</Label>
                  <Select value={formData.nextOfKinRelationship} onValueChange={(value) => handleInputChange('nextOfKinRelationship', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select relationship" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="spouse">Spouse</SelectItem>
                      <SelectItem value="parent">Parent</SelectItem>
                      <SelectItem value="child">Child</SelectItem>
                      <SelectItem value="sibling">Sibling</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Experience */}
            <Card>
              <CardHeader>
                <CardTitle>Experience</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="experience">Years of Experience</Label>
                  <Select value={formData.experience} onValueChange={(value) => handleInputChange('experience', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select experience" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="0-1">0-1 years</SelectItem>
                      <SelectItem value="2-5">2-5 years</SelectItem>
                      <SelectItem value="6-10">6-10 years</SelectItem>
                      <SelectItem value="11-15">11-15 years</SelectItem>
                      <SelectItem value="15+">15+ years</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="previousEmployer">Previous Employer</Label>
                  <Input
                    id="previousEmployer"
                    value={formData.previousEmployer}
                    onChange={(e) => handleInputChange('previousEmployer', e.target.value)}
                    placeholder="ABC Transport Ltd"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Notes */}
            <Card>
              <CardHeader>
                <CardTitle>Additional Notes</CardTitle>
              </CardHeader>
              <CardContent>
                <Textarea
                  value={formData.notes}
                  onChange={(e) => handleInputChange('notes', e.target.value)}
                  placeholder="Any additional information about the driver..."
                  rows={4}
                />
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Submit Buttons */}
        <div className="flex justify-end space-x-4">
          <Button type="button" variant="outline" onClick={() => navigate("/drivers")}>
            Cancel
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Adding Driver..." : "Add Driver"}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default AddDriver;