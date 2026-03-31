import {
  Card,
  CardContent,
  CardHeader,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { MapPin, Gauge, Navigation, Clock } from "lucide-react";

const routeStops = [
  { name: "Nairobi", time: "03/12/24 06:00 AM", status: "completed" },
  { name: "Machakos", time: "03/12/24 07:30 AM", status: "current" },
  { name: "Emali", time: "", status: "upcoming" },
  { name: "Mtito Andei", time: "", status: "upcoming" },
  { name: "Voi", time: "", status: "upcoming" },
  { name: "Mombasa", time: "Est. 03/12/24 till 4PM", status: "upcoming" },
];

export function TrackingDetails() {
  return (
    <Card>
      <CardHeader className="pb-3">
        <Tabs defaultValue="tracking" className="w-full">
          <TabsList className="w-full justify-start">
            <TabsTrigger value="tracking">Tracking details</TabsTrigger>
            <TabsTrigger value="driver">Driver info</TabsTrigger>
            <TabsTrigger value="vehicle">Vehicle</TabsTrigger>
            <TabsTrigger value="customer">Customer info</TabsTrigger>
            <TabsTrigger value="documents">Documents</TabsTrigger>
          </TabsList>
          <TabsContent value="tracking" className="mt-6">
            {/* Route Timeline */}
            <div className="mb-6">
              <div className="flex justify-between items-start mb-3">
                {routeStops.map((stop, index) => (
                  <div key={stop.name} className="flex flex-col items-center flex-1">
                    <div className={`text-sm font-medium ${
                      stop.status === "current" ? "text-primary" : 
                      stop.status === "completed" ? "text-foreground" : 
                      "text-muted-foreground"
                    }`}>
                      {stop.name}
                    </div>
                  </div>
                ))}
              </div>
              
              {/* Progress Bar */}
              <div className="relative mb-3">
                <div className="h-1 bg-muted rounded-full"></div>
                <div className="absolute top-0 h-1 bg-primary rounded-full transition-all" style={{ width: "25%" }}></div>
                {/* Dots for each stop */}
                <div className="absolute top-1/2 -translate-y-1/2 w-full flex justify-between px-0">
                  {routeStops.map((stop, index) => (
                    <div
                      key={`dot-${stop.name}`}
                      className={`w-3 h-3 rounded-full border-2 ${
                        stop.status === "completed" ? "bg-primary border-primary" :
                        stop.status === "current" ? "bg-primary border-primary ring-4 ring-primary/20" :
                        "bg-background border-muted"
                      }`}
                    ></div>
                  ))}
                </div>
              </div>
              
              {/* Timestamps */}
              <div className="flex justify-between items-center text-xs text-muted-foreground">
                <div>{routeStops[0].time}</div>
                <div className="text-primary font-medium">{routeStops[1].time}</div>
                <div className="ml-auto">{routeStops[5].time}</div>
              </div>
            </div>

            {/* Location Stats */}
            <div className="grid grid-cols-4 gap-4 pt-4 border-t">
              <div className="flex items-start gap-3">
                <div className="p-2 rounded-lg bg-primary/10">
                  <MapPin className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <div className="text-sm font-semibold text-foreground">Machakos</div>
                  <div className="text-xs text-muted-foreground">Current Location</div>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="p-2 rounded-lg bg-primary/10">
                  <Gauge className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <div className="text-sm font-semibold text-foreground">85 km/h</div>
                  <div className="text-xs text-muted-foreground">Avg Speed</div>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="p-2 rounded-lg bg-primary/10">
                  <Navigation className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <div className="text-sm font-semibold text-foreground">420 km</div>
                  <div className="text-xs text-muted-foreground">Distance Left</div>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="p-2 rounded-lg bg-primary/10">
                  <Clock className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <div className="text-sm font-semibold text-foreground">30 mins ago</div>
                  <div className="text-xs text-muted-foreground">Last Update</div>
                </div>
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="driver" className="mt-6">
            <div className="space-y-4">
              <div className="flex items-start gap-4">
                <div className="w-20 h-20 rounded-full bg-muted flex items-center justify-center overflow-hidden">
                  <img 
                    src="https://api.dicebear.com/7.x/avataaars/svg?seed=driver1" 
                    alt="Driver" 
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold">Kamau Mwangi</h3>
                  <p className="text-sm text-muted-foreground">Professional Driver</p>
                  <div className="flex gap-2 mt-2">
                    <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">Active</span>
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">5 Years Experience</span>
                  </div>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                <div>
                  <p className="text-xs text-muted-foreground">Phone Number</p>
                  <p className="text-sm font-medium">+254 712 345 678</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">License Number</p>
                  <p className="text-sm font-medium">DL-2019-45678</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">License Expiry</p>
                  <p className="text-sm font-medium">Dec 15, 2026</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Total Deliveries</p>
                  <p className="text-sm font-medium">1,247</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Rating</p>
                  <p className="text-sm font-medium">4.8 / 5.0 ⭐</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Emergency Contact</p>
                  <p className="text-sm font-medium">+254 722 987 654</p>
                </div>
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="vehicle" className="mt-6">
            <div className="space-y-4">
              <div className="flex items-start gap-4">
                <div className="w-32 h-24 rounded-lg bg-muted overflow-hidden">
                  <img 
                    src="https://images.unsplash.com/photo-1519003722824-194d4455a60c?w=200&h=150&fit=crop" 
                    alt="Vehicle" 
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold">Isuzu FVZ 1800</h3>
                  <p className="text-sm text-muted-foreground">Heavy Duty Truck</p>
                  <p className="text-sm font-medium mt-1">KCA 456T</p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                <div>
                  <p className="text-xs text-muted-foreground">Chassis Number</p>
                  <p className="text-sm font-medium">FVZ34-1234567</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Engine Number</p>
                  <p className="text-sm font-medium">6HK1-987654</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Year of Manufacture</p>
                  <p className="text-sm font-medium">2021</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Fuel Type</p>
                  <p className="text-sm font-medium">Diesel</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Max Load Capacity</p>
                  <p className="text-sm font-medium">9,000 kg</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Current Odometer</p>
                  <p className="text-sm font-medium">87,450 km</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Insurance Expiry</p>
                  <p className="text-sm font-medium">Mar 20, 2025</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Next Service Due</p>
                  <p className="text-sm font-medium">Jan 15, 2025</p>
                </div>
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="customer" className="mt-6">
            <div className="space-y-4">
              <div className="flex items-start gap-4">
                <div className="w-16 h-16 rounded-lg bg-primary/10 flex items-center justify-center">
                  <span className="text-2xl font-bold text-primary">TM</span>
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold">Tuskys Mombasa Branch</h3>
                  <p className="text-sm text-muted-foreground">Retail & Wholesale</p>
                  <p className="text-sm text-muted-foreground mt-1">Customer ID: CUST-2024-1156</p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                <div>
                  <p className="text-xs text-muted-foreground">Contact Person</p>
                  <p className="text-sm font-medium">Mary Wanjiru</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Phone Number</p>
                  <p className="text-sm font-medium">+254 41 222 3456</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Email</p>
                  <p className="text-sm font-medium">mary.w@tuskys.co.ke</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Delivery Address</p>
                  <p className="text-sm font-medium">Nyali, Mombasa</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Order Number</p>
                  <p className="text-sm font-medium">ORD-2024-8934</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Payment Status</p>
                  <p className="text-sm font-medium text-green-600">Paid</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Delivery Instructions</p>
                  <p className="text-sm font-medium">Loading dock at rear entrance</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Special Requirements</p>
                  <p className="text-sm font-medium">Temperature controlled</p>
                </div>
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="documents" className="mt-6">
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 border rounded-lg hover:bg-accent/5 cursor-pointer">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded bg-blue-100 flex items-center justify-center">
                    <span className="text-xs font-bold text-blue-700">PDF</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium">Delivery Note</p>
                    <p className="text-xs text-muted-foreground">Uploaded: Dec 3, 2024</p>
                  </div>
                </div>
                <Button variant="ghost" size="sm">View</Button>
              </div>
              
              <div className="flex items-center justify-between p-3 border rounded-lg hover:bg-accent/5 cursor-pointer">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded bg-green-100 flex items-center justify-center">
                    <span className="text-xs font-bold text-green-700">PDF</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium">Invoice</p>
                    <p className="text-xs text-muted-foreground">Uploaded: Dec 3, 2024</p>
                  </div>
                </div>
                <Button variant="ghost" size="sm">View</Button>
              </div>
              
              <div className="flex items-center justify-between p-3 border rounded-lg hover:bg-accent/5 cursor-pointer">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded bg-purple-100 flex items-center justify-center">
                    <span className="text-xs font-bold text-purple-700">PDF</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium">Waybill</p>
                    <p className="text-xs text-muted-foreground">Uploaded: Dec 3, 2024</p>
                  </div>
                </div>
                <Button variant="ghost" size="sm">View</Button>
              </div>
              
              <div className="flex items-center justify-between p-3 border rounded-lg hover:bg-accent/5 cursor-pointer">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded bg-orange-100 flex items-center justify-center">
                    <span className="text-xs font-bold text-orange-700">IMG</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium">Cargo Photos</p>
                    <p className="text-xs text-muted-foreground">3 images • Dec 3, 2024</p>
                  </div>
                </div>
                <Button variant="ghost" size="sm">View</Button>
              </div>
              
              <div className="flex items-center justify-between p-3 border rounded-lg hover:bg-accent/5 cursor-pointer">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded bg-red-100 flex items-center justify-center">
                    <span className="text-xs font-bold text-red-700">PDF</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium">Insurance Certificate</p>
                    <p className="text-xs text-muted-foreground">Valid until: Mar 20, 2025</p>
                  </div>
                </div>
                <Button variant="ghost" size="sm">View</Button>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardHeader>
    </Card>
  );
}