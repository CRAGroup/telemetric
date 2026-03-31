import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";

interface Vehicle {
  id: string;
  name: string;
  status: "in-transit" | "stopped" | "awaiting-loading";
  imageUrl: string;
}

const vehicles: Vehicle[] = [
  { id: "KCA 456T", name: "Isuzu FVZ", status: "in-transit", imageUrl: "https://images.unsplash.com/photo-1519003722824-194d4455a60c?w=200&h=200&fit=crop" },
  { id: "KBZ 789M", name: "Mercedes-Benz Actros", status: "in-transit", imageUrl: "https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?w=200&h=200&fit=crop" },
  { id: "KCB 234L", name: "Scania R450", status: "in-transit", imageUrl: "https://images.unsplash.com/photo-1494412651409-8963ce7935a7?w=200&h=200&fit=crop" },
  { id: "KDA 567P", name: "Volvo FH16", status: "in-transit", imageUrl: "https://images.unsplash.com/photo-1519003722824-194d4455a60c?w=200&h=200&fit=crop" },
  { id: "KAA 890R", name: "MAN TGS", status: "stopped", imageUrl: "https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?w=200&h=200&fit=crop" },
  { id: "KBX 123K", name: "Isuzu FTR", status: "in-transit", imageUrl: "https://images.unsplash.com/photo-1494412651409-8963ce7935a7?w=200&h=200&fit=crop" },
  { id: "KCC 456N", name: "DAF XF", status: "awaiting-loading", imageUrl: "https://images.unsplash.com/photo-1519003722824-194d4455a60c?w=200&h=200&fit=crop" },
  { id: "KDB 789Q", name: "Scania P320", status: "in-transit", imageUrl: "https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?w=200&h=200&fit=crop" },
  { id: "KAB 234W", name: "Mercedes-Benz Atego", status: "awaiting-loading", imageUrl: "https://images.unsplash.com/photo-1494412651409-8963ce7935a7?w=200&h=200&fit=crop" },
  { id: "KCE 567Y", name: "Isuzu NQR", status: "awaiting-loading", imageUrl: "https://images.unsplash.com/photo-1519003722824-194d4455a60c?w=200&h=200&fit=crop" },
];

const statusConfig = {
  "in-transit": { label: "In Transit", variant: "default" as const },
  "stopped": { label: "Stopped", variant: "destructive" as const },
  "awaiting-loading": { label: "Awaiting Loading", variant: "secondary" as const },
};

interface VehicleListProps {
  searchQuery?: string;
}

export function VehicleList({ searchQuery = "" }: VehicleListProps) {
  const [selectedVehicle, setSelectedVehicle] = useState<string | null>("#QH-44459-KC");

  const filteredVehicles = vehicles.filter(
    (vehicle) =>
      vehicle.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      vehicle.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <ScrollArea className="h-full">
      <div className="space-y-2 p-4">
        {filteredVehicles.map((vehicle) => (
          <div
            key={vehicle.id}
            onClick={() => setSelectedVehicle(vehicle.id)}
            className={`flex items-start gap-3 p-3 rounded-lg border transition-colors cursor-pointer ${
              selectedVehicle === vehicle.id
                ? "bg-primary/5 border-primary"
                : "bg-card border-border hover:bg-accent/5"
            }`}
          >
            <img
              src={vehicle.imageUrl}
              alt={vehicle.name}
              className="w-12 h-12 rounded-md object-cover flex-shrink-0"
            />
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-sm text-foreground truncate">
                {vehicle.id}
              </p>
              <p className="text-xs text-muted-foreground truncate">
                {vehicle.name}
              </p>
              <Badge 
                variant={statusConfig[vehicle.status].variant}
                className="mt-1.5 text-xs"
              >
                {statusConfig[vehicle.status].label}
              </Badge>
            </div>
          </div>
        ))}
        {filteredVehicles.length === 0 && (
          <div className="text-center py-8 text-sm text-muted-foreground">
            No vehicles found
          </div>
        )}
      </div>
    </ScrollArea>
  );
}
