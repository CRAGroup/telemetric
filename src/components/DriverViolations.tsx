import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { useToast } from "@/components/ui/use-toast";
import { AlertTriangle, Plus, Calendar, MapPin, User, FileText, Gavel } from "lucide-react";

interface Violation {
  id: string;
  violation_type: string;
  violation_date: string;
  fine_amount: number | null;
  fine_paid: boolean | null;
  fine_paid_date: string | null;
  points_deducted: number | null;
  description: string | null;
  location: string | null;
  officer_name: string | null;
  case_number: string | null;
  court_date: string | null;
  status: string | null;
}

interface DriverViolationsProps {
  driverId: string;
  driverName: string;
}

const DriverViolations = ({ driverId, driverName }: DriverViolationsProps) => {
  const { toast } = useToast();
  const [isAddingViolation, setIsAddingViolation] = useState(false);
  const [newViolation, setNewViolation] = useState({
    violation_type: "",
    violation_date: "",
    fine_amount: "",
    description: "",
    location: "",
    officer_name: "",
    case_number: "",
    points_deducted: ""
  });

  // Fetch violations for this driver
  // NOTE: This requires a violations API endpoint to be added to the backend
  const { data: violations = [], isLoading, refetch } = useQuery({
    queryKey: ['driver-violations', driverId],
    queryFn: async () => {
      // TODO: Add violations endpoint to API
      // For now, return empty array
      console.warn('Violations API endpoint not implemented yet');
      return [];
      
      // When endpoint is ready, use:
      // const response = await apiClient.getDriverViolations(Number(driverId));
      // return response.items;
    },
  });

  const handleAddViolation = async () => {
    try {
      // TODO: Add create violation endpoint to API
      toast({
        title: "Not Implemented",
        description: "Violations API endpoint needs to be added to the backend.",
        variant: "destructive",
      });
      return;
      
      // When endpoint is ready, use:
      // await apiClient.createDriverViolation(Number(driverId), {
      //   violation_type: newViolation.violation_type,
      //   violation_date: newViolation.violation_date,
      //   ...
      // });
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to add violation.",
        variant: "destructive",
      });
    }
  };

  const getStatusColor = (status: string | null) => {
    switch (status) {
      case "resolved": return "bg-green-100 text-green-800";
      case "appealed": return "bg-blue-100 text-blue-800";
      case "pending": return "bg-yellow-100 text-yellow-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getViolationTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case "speeding": return "bg-red-100 text-red-800";
      case "parking": return "bg-blue-100 text-blue-800";
      case "license": return "bg-purple-100 text-purple-800";
      case "vehicle": return "bg-orange-100 text-orange-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            Traffic Violations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-4">Loading violations...</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            Traffic Violations ({violations.length})
          </CardTitle>
          <Dialog open={isAddingViolation} onOpenChange={setIsAddingViolation}>
            <DialogTrigger asChild>
              <Button size="sm">
                <Plus className="h-4 w-4 mr-2" />
                Add Violation
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Add Traffic Violation - {driverName}</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="violation_type">Violation Type *</Label>
                    <Select value={newViolation.violation_type} onValueChange={(value) => setNewViolation({...newViolation, violation_type: value})}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select violation type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="speeding">Speeding</SelectItem>
                        <SelectItem value="parking">Illegal Parking</SelectItem>
                        <SelectItem value="license">License Violation</SelectItem>
                        <SelectItem value="vehicle">Vehicle Defect</SelectItem>
                        <SelectItem value="reckless_driving">Reckless Driving</SelectItem>
                        <SelectItem value="overloading">Overloading</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="violation_date">Violation Date *</Label>
                    <Input
                      id="violation_date"
                      type="date"
                      value={newViolation.violation_date}
                      onChange={(e) => setNewViolation({...newViolation, violation_date: e.target.value})}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="fine_amount">Fine Amount (KSh)</Label>
                    <Input
                      id="fine_amount"
                      type="number"
                      placeholder="5000"
                      value={newViolation.fine_amount}
                      onChange={(e) => setNewViolation({...newViolation, fine_amount: e.target.value})}
                    />
                  </div>
                  <div>
                    <Label htmlFor="points_deducted">Points Deducted</Label>
                    <Input
                      id="points_deducted"
                      type="number"
                      placeholder="3"
                      value={newViolation.points_deducted}
                      onChange={(e) => setNewViolation({...newViolation, points_deducted: e.target.value})}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="location">Location</Label>
                    <Input
                      id="location"
                      placeholder="Thika Road, Nairobi"
                      value={newViolation.location}
                      onChange={(e) => setNewViolation({...newViolation, location: e.target.value})}
                    />
                  </div>
                  <div>
                    <Label htmlFor="officer_name">Officer Name</Label>
                    <Input
                      id="officer_name"
                      placeholder="PC John Doe"
                      value={newViolation.officer_name}
                      onChange={(e) => setNewViolation({...newViolation, officer_name: e.target.value})}
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="case_number">Case Number</Label>
                  <Input
                    id="case_number"
                    placeholder="TRF/2024/001234"
                    value={newViolation.case_number}
                    onChange={(e) => setNewViolation({...newViolation, case_number: e.target.value})}
                  />
                </div>

                <div>
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    placeholder="Details about the violation..."
                    value={newViolation.description}
                    onChange={(e) => setNewViolation({...newViolation, description: e.target.value})}
                    rows={3}
                  />
                </div>

                <div className="flex justify-end space-x-2">
                  <Button variant="outline" onClick={() => setIsAddingViolation(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleAddViolation}>
                    Add Violation
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </CardHeader>
      <CardContent>
        {violations.length === 0 ? (
          <div className="text-center py-8">
            <AlertTriangle className="h-12 w-12 mx-auto mb-4 text-green-600" />
            <p className="text-lg font-medium text-green-600">Clean Record!</p>
            <p className="text-gray-600">No traffic violations recorded</p>
          </div>
        ) : (
          <div className="space-y-4">
            {violations.map((violation) => (
              <div key={violation.id} className="border rounded-lg p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <Badge className={getViolationTypeColor(violation.violation_type)}>
                      {violation.violation_type.replace('_', ' ').toUpperCase()}
                    </Badge>
                    <Badge className={getStatusColor(violation.status)}>
                      {violation.status?.toUpperCase() || 'PENDING'}
                    </Badge>
                  </div>
                  <div className="text-sm text-gray-500">
                    {new Date(violation.violation_date).toLocaleDateString()}
                  </div>
                </div>

                {violation.description && (
                  <p className="text-gray-700 mb-3">{violation.description}</p>
                )}

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  {violation.fine_amount && (
                    <div className="flex items-center gap-2">
                      <span className="font-medium">Fine:</span>
                      <span>KSh {violation.fine_amount.toLocaleString()}</span>
                    </div>
                  )}
                  {violation.points_deducted && (
                    <div className="flex items-center gap-2">
                      <span className="font-medium">Points:</span>
                      <span>{violation.points_deducted}</span>
                    </div>
                  )}
                  {violation.location && (
                    <div className="flex items-center gap-2">
                      <MapPin className="h-3 w-3" />
                      <span>{violation.location}</span>
                    </div>
                  )}
                  {violation.officer_name && (
                    <div className="flex items-center gap-2">
                      <User className="h-3 w-3" />
                      <span>{violation.officer_name}</span>
                    </div>
                  )}
                </div>

                {violation.case_number && (
                  <div className="mt-2 text-xs text-gray-500">
                    Case: {violation.case_number}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default DriverViolations;