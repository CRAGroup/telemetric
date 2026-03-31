import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { VehicleList } from "./VehicleList";
import { useLocation } from "react-router-dom";
import { Search, Plus } from "lucide-react";

export function SecondarySidebar() {
  const { pathname } = useLocation();
  const [searchQuery, setSearchQuery] = useState("");

  const getTitle = () => {
    if (pathname === "/") return "Tracking";
    return pathname.substring(1).charAt(0).toUpperCase() + pathname.substring(2);
  };

  return (
    <div className="flex flex-col h-full bg-sidebar border-r">
      <div className="flex items-center justify-between p-4 border-b">
        <h2 className="text-lg font-semibold text-foreground capitalize">{getTitle()}</h2>
        <Button size="icon" variant="ghost" className="h-8 w-8">
          <Plus className="h-4 w-4" />
        </Button>
      </div>
      {(pathname === "/tracking" || pathname === "/") && (
        <>
          <div className="p-4 border-b">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input 
                placeholder="Search" 
                className="w-full pl-9" 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
          <VehicleList searchQuery={searchQuery} />
        </>
      )}
    </div>
  );
}
