import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { MapContainer, TileLayer, Marker, Popup, Polyline, CircleMarker, Tooltip } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";

// Fix for default marker icons in Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

// Custom truck icon using SVG
const createTruckIcon = (color: string, status: string) => {
  const svgIcon = `
    <svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
      <circle cx="20" cy="20" r="18" fill="${color}" opacity="0.9"/>
      <path d="M12 16h8v6h-8v-6zm8 0h4l2 3v3h-6v-6zm-10 8a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm12 0a2 2 0 1 0 0-4 2 2 0 0 0 0 4z" 
            fill="white" stroke="white" stroke-width="0.5"/>
      ${status === 'moving' ? '<circle cx="32" cy="8" r="4" fill="#10b981"/>' : ''}
      ${status === 'stopped' ? '<circle cx="32" cy="8" r="4" fill="#ef4444"/>' : ''}
    </svg>
  `;
  return new L.DivIcon({
    html: svgIcon,
    className: 'custom-truck-icon',
    iconSize: [40, 40],
    iconAnchor: [20, 20],
    popupAnchor: [0, -20],
  });
};

// Route waypoints - Nairobi to Mombasa via major towns
const routeWaypoints = [
  { name: "Nairobi", position: [-1.2921, 36.8219] as [number, number], time: "06:00 AM", status: "completed" },
  { name: "Machakos", position: [-1.5177, 37.2634] as [number, number], time: "07:30 AM", status: "current" },
  { name: "Emali", position: [-2.0167, 37.4667] as [number, number], time: "09:15 AM", status: "upcoming" },
  { name: "Mtito Andei", position: [-2.6833, 38.1667] as [number, number], time: "11:00 AM", status: "upcoming" },
  { name: "Voi", position: [-3.3963, 38.5561] as [number, number], time: "01:30 PM", status: "upcoming" },
  { name: "Mombasa", position: [-4.0435, 39.6682] as [number, number], time: "04:00 PM", status: "upcoming" },
];

// Demo vehicles with positions along the route
const demoVehicles = [
  {
    id: "1",
    registration: "KCA 456T",
    make: "Isuzu",
    model: "FVZ 1800",
    position: [-1.5177, 37.2634] as [number, number], // Machakos - current location
    status: "moving",
    speed: "85 km/h",
    driver: "Kamau Mwangi",
    cargo: "FMCG Goods",
    capacity: "75%",
  },
  {
    id: "2",
    registration: "KBZ 789M",
    make: "Mercedes-Benz",
    model: "Actros",
    position: [-2.3, 37.8] as [number, number], // Between Emali and Mtito Andei
    status: "moving",
    speed: "90 km/h",
    driver: "John Omondi",
    cargo: "Electronics",
    capacity: "60%",
  },
  {
    id: "3",
    registration: "KCB 234L",
    make: "Scania",
    model: "R450",
    position: [-3.2, 38.4] as [number, number], // Near Voi
    status: "stopped",
    speed: "0 km/h",
    driver: "Peter Wanjiru",
    cargo: "Construction Materials",
    capacity: "90%",
  },
  {
    id: "4",
    registration: "KDA 567P",
    make: "Volvo",
    model: "FH16",
    position: [-1.35, 36.95] as [number, number], // Between Nairobi and Machakos
    status: "moving",
    speed: "78 km/h",
    driver: "Mary Njeri",
    cargo: "Textiles",
    capacity: "55%",
  },
];

export function MapOverview() {
  // Try to fetch real vehicles from database, but use demo data as fallback
  const { data: dbVehicles } = useQuery({
    queryKey: ["vehicles"],
    queryFn: async () => {
      try {
        const response = await apiClient.getVehicles();
        return response.items;
      } catch (error) {
        console.log("Using demo data for vehicles");
        return null;
      }
    },
  });

  // Use database vehicles if available and have coordinates, otherwise use demo vehicles
  const vehicles = dbVehicles?.filter((v: any) => v.latitude && v.longitude).length 
    ? dbVehicles.filter((v: any) => v.latitude && v.longitude)
    : demoVehicles;

  return (
    <Card className="h-full w-full overflow-hidden">
      <MapContainer 
        center={[-2.5, 37.9]} 
        zoom={7} 
        style={{ height: "100%", width: "100%", position: "relative", zIndex: 1 }}
        className="rounded-lg"
        scrollWheelZoom={true}
      >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      
      {/* Route line - main route */}
      <Polyline
        positions={routeWaypoints.map(wp => wp.position)}
        pathOptions={{ 
          color: "#3b82f6", 
          weight: 4,
          opacity: 0.6,
        }}
      />
      
      {/* Completed route section */}
      <Polyline
        positions={[routeWaypoints[0].position, routeWaypoints[1].position]}
        pathOptions={{ 
          color: "#10b981", 
          weight: 4,
          opacity: 0.8,
        }}
      />
      
      {/* Waypoint markers */}
      {routeWaypoints.map((waypoint, index) => {
        const isCompleted = waypoint.status === "completed";
        const isCurrent = waypoint.status === "current";
        const isStart = index === 0;
        const isEnd = index === routeWaypoints.length - 1;
        
        return (
          <CircleMarker
            key={waypoint.name}
            center={waypoint.position}
            radius={isCurrent ? 10 : 8}
            pathOptions={{
              fillColor: isCurrent ? "#3b82f6" : isCompleted ? "#10b981" : "#ffffff",
              fillOpacity: 1,
              color: isCurrent ? "#3b82f6" : isCompleted ? "#10b981" : "#94a3b8",
              weight: isCurrent ? 3 : 2,
            }}
          >
            <Popup>
              <div className="min-w-[200px]">
                <div className="font-bold text-base mb-1">{waypoint.name}</div>
                <div className="text-sm text-gray-600 mb-2">
                  {isStart && "🏁 Starting Point"}
                  {isEnd && "🎯 Destination"}
                  {isCurrent && "📍 Current Stop"}
                  {!isStart && !isEnd && !isCurrent && "⏱️ Upcoming Stop"}
                </div>
                <div className="text-xs text-gray-500">
                  {isCompleted ? `✓ Passed at ${waypoint.time}` : 
                   isCurrent ? `⏰ Arrived at ${waypoint.time}` :
                   `ETA: ${waypoint.time}`}
                </div>
              </div>
            </Popup>
            <Tooltip direction="top" offset={[0, -10]} opacity={0.9}>
              <span className="font-semibold">{waypoint.name}</span>
            </Tooltip>
          </CircleMarker>
        );
      })}
      
      {/* Vehicle markers */}
      {vehicles.map((vehicle: any) => {
        const isDemo = 'position' in vehicle;
        const position = isDemo ? vehicle.position : [vehicle.latitude, vehicle.longitude];
        const status = isDemo ? vehicle.status : (vehicle.vehicle_status === 'active' ? 'moving' : 'stopped');
        const color = status === 'moving' ? '#3b82f6' : '#ef4444';
        
        return (
          <Marker 
            key={vehicle.id} 
            position={position}
            icon={createTruckIcon(color, status)}
          >
            <Popup>
              <div className="min-w-[250px]">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h3 className="font-bold text-base">
                      {isDemo ? `${vehicle.make} ${vehicle.model}` : `${vehicle.make} ${vehicle.model}`}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {isDemo ? vehicle.registration : vehicle.registration_number}
                    </p>
                  </div>
                  <Badge variant={status === 'moving' ? 'default' : 'destructive'}>
                    {status === 'moving' ? '🚛 Moving' : '🛑 Stopped'}
                  </Badge>
                </div>
                
                {isDemo && (
                  <>
                    <div className="space-y-1 text-sm border-t pt-2 mt-2">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Driver:</span>
                        <span className="font-medium">{vehicle.driver}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Speed:</span>
                        <span className="font-medium">{vehicle.speed}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Cargo:</span>
                        <span className="font-medium">{vehicle.cargo}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Capacity:</span>
                        <span className="font-medium">{vehicle.capacity}</span>
                      </div>
                    </div>
                  </>
                )}
                
                {!isDemo && (
                  <div className="space-y-1 text-sm border-t pt-2 mt-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Status:</span>
                      <span className="font-medium">{vehicle.vehicle_status}</span>
                    </div>
                    {vehicle.driver_name && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Driver:</span>
                        <span className="font-medium">{vehicle.driver_name}</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </Popup>
            <Tooltip direction="top" offset={[0, -20]} opacity={0.9}>
              <div className="text-center">
                <div className="font-semibold">
                  {isDemo ? vehicle.registration : vehicle.registration_number}
                </div>
                <div className="text-xs">
                  {status === 'moving' ? '🚛 Moving' : '🛑 Stopped'}
                </div>
              </div>
            </Tooltip>
          </Marker>
        );
      })}
      </MapContainer>
    </Card>
  );
}
