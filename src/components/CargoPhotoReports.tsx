import { useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Textarea } from "./ui/textarea";
import { useToast } from "./ui/use-toast";
import { Camera, MapPin, Clock, CheckCircle2, AlertCircle } from "lucide-react";

interface CargoPhoto {
  id: number;
  point: string;
  address: string;
  imageUrl: string;
  timestamp?: string;
  status?: "completed" | "pending" | "requested";
  requestedBy?: string;
}

const initialCargoPhotos: CargoPhoto[] = [
  {
    id: 1,
    point: "Point #1",
    address: "Industrial Area, Nairobi",
    imageUrl: "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=400&h=300&fit=crop",
    timestamp: "2 hours ago",
    status: "completed"
  },
  {
    id: 2,
    point: "Point #2", 
    address: "Machakos Junction, Machakos",
    imageUrl: "https://images.unsplash.com/photo-1566576721346-d4a3b4eaeb55?w=400&h=300&fit=crop",
    timestamp: "1 hour ago",
    status: "completed"
  },
  {
    id: 3,
    point: "Point #3",
    address: "Emali Town, Makueni County", 
    imageUrl: "https://images.unsplash.com/photo-1553413077-190dd305871c?w=400&h=300&fit=crop",
    timestamp: "30 minutes ago",
    status: "completed"
  },
];

export function CargoPhotoReports() {
  const { toast } = useToast();
  const [cargoPhotos, setCargoPhotos] = useState<CargoPhoto[]>(initialCargoPhotos);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [requestForm, setRequestForm] = useState({
    location: "",
    description: "",
    priority: "normal"
  });

  const handlePhotoRequest = () => {
    if (!requestForm.location.trim()) {
      toast({
        title: "Location Required",
        description: "Please specify the location for the photo request.",
        variant: "destructive",
      });
      return;
    }

    const newRequest: CargoPhoto = {
      id: Date.now(),
      point: `Point #${cargoPhotos.length + 1}`,
      address: requestForm.location,
      imageUrl: "", // No image yet
      timestamp: "Just now",
      status: "requested",
      requestedBy: "Fleet Manager"
    };

    setCargoPhotos(prev => [...prev, newRequest]);
    setRequestForm({ location: "", description: "", priority: "normal" });
    setIsDialogOpen(false);

    toast({
      title: "Photo Request Sent",
      description: `Photo request sent to driver for ${requestForm.location}`,
    });

    // Simulate driver taking photo after some time
    setTimeout(() => {
      setCargoPhotos(prev => 
        prev.map(photo => 
          photo.id === newRequest.id 
            ? { 
                ...photo, 
                status: "pending",
                timestamp: "Uploading..."
              } 
            : photo
        )
      );
    }, 2000);

    // Simulate photo completion
    setTimeout(() => {
      const sampleImages = [
        "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=400&h=300&fit=crop",
        "https://images.unsplash.com/photo-1566576721346-d4a3b4eaeb55?w=400&h=300&fit=crop", 
        "https://images.unsplash.com/photo-1553413077-190dd305871c?w=400&h=300&fit=crop"
      ];
      
      setCargoPhotos(prev => 
        prev.map(photo => 
          photo.id === newRequest.id 
            ? { 
                ...photo, 
                status: "completed",
                imageUrl: sampleImages[Math.floor(Math.random() * sampleImages.length)],
                timestamp: "Just uploaded"
              } 
            : photo
        )
      );

      toast({
        title: "Photo Received",
        description: "Driver has uploaded the requested photo.",
      });
    }, 5000);
  };

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case "completed": return <CheckCircle2 className="w-3 h-3 text-green-500" />;
      case "pending": return <Clock className="w-3 h-3 text-orange-500" />;
      case "requested": return <AlertCircle className="w-3 h-3 text-blue-500" />;
      default: return null;
    }
  };

  const getStatusColor = (status?: string) => {
    switch (status) {
      case "completed": return "bg-green-100 text-green-800";
      case "pending": return "bg-orange-100 text-orange-800";
      case "requested": return "bg-blue-100 text-blue-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Cargo Photo Reports</CardTitle>
          <Badge variant="outline">
            {cargoPhotos.filter(p => p.status === "completed").length} / {cargoPhotos.length} completed
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="grid grid-cols-4 gap-4">
        {cargoPhotos.map((photo) => (
          <div key={photo.id} className="space-y-2">
            <div className="relative aspect-[4/3] rounded-lg overflow-hidden bg-muted">
              {photo.imageUrl ? (
                <img 
                  src={photo.imageUrl} 
                  alt={photo.point} 
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gray-100">
                  <div className="text-center">
                    <Camera className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-xs text-gray-500">
                      {photo.status === "requested" ? "Requested" : "Uploading..."}
                    </p>
                  </div>
                </div>
              )}
              
              {photo.status && (
                <div className="absolute top-2 right-2">
                  <Badge className={`text-xs ${getStatusColor(photo.status)}`}>
                    <div className="flex items-center space-x-1">
                      {getStatusIcon(photo.status)}
                      <span>{photo.status}</span>
                    </div>
                  </Badge>
                </div>
              )}
            </div>
            
            <div>
              <p className="text-sm font-semibold">{photo.point}</p>
              <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                <MapPin className="w-3 h-3" />
                <span className="line-clamp-1">{photo.address}</span>
              </div>
              {photo.timestamp && (
                <div className="flex items-center space-x-1 text-xs text-muted-foreground mt-1">
                  <Clock className="w-3 h-3" />
                  <span>{photo.timestamp}</span>
                </div>
              )}
            </div>
          </div>
        ))}
        
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button 
              variant="outline" 
              className="h-full min-h-[180px] flex flex-col items-center justify-center gap-2 border-dashed"
            >
              <div className="p-3 rounded-full bg-primary/10">
                <Camera className="h-6 w-6 text-primary" />
              </div>
              <span className="text-sm font-medium">Request Photo</span>
            </Button>
          </DialogTrigger>
          
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Request Cargo Photo</DialogTitle>
            </DialogHeader>
            
            <div className="space-y-4">
              <div>
                <Label htmlFor="location">Location *</Label>
                <Input
                  id="location"
                  placeholder="e.g., Mombasa Port, Gate 3"
                  value={requestForm.location}
                  onChange={(e) => setRequestForm(prev => ({...prev, location: e.target.value}))}
                />
              </div>
              
              <div>
                <Label htmlFor="description">Description (Optional)</Label>
                <Textarea
                  id="description"
                  placeholder="Additional instructions for the driver..."
                  value={requestForm.description}
                  onChange={(e) => setRequestForm(prev => ({...prev, description: e.target.value}))}
                  rows={3}
                />
              </div>
              
              <div className="flex justify-end space-x-2">
                <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handlePhotoRequest}>
                  Send Request
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>
  );
}
