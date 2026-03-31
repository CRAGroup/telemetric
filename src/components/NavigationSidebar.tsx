import { Home, MapPin, Truck, Wrench, FileText, Bell, Settings, Camera, ChevronLeft, ChevronRight, ChevronDown, ChevronUp, Users } from "lucide-react";
import { useLocation, Link } from "react-router-dom";
import { cn } from "@/lib/utils";
import { buttonVariants } from "@/components/ui/button";
import { useState } from "react";

interface NavigationSidebarProps {
    isCollapsed: boolean;
    onToggleCollapse: () => void;
}

export function NavigationSidebar({ isCollapsed, onToggleCollapse }: NavigationSidebarProps) {
    const { pathname } = useLocation();
    const [expandedMenus, setExpandedMenus] = useState<string[]>([]);

    const toggleMenu = (menuName: string) => {
        setExpandedMenus(prev => 
            prev.includes(menuName) 
                ? prev.filter(name => name !== menuName)
                : [...prev, menuName]
        );
    };

    const links = [
        { name: "Home", href: "/", icon: Home },
        { name: "Tracking", href: "/tracking", icon: MapPin },
        {
            name: "Vehicles",
            icon: Truck,
            href: "/vehicles",
            subLinks: [
                { name: "Vehicles List", href: "/vehicles" },
                { name: "Add Vehicle", href: "/vehicles/add" },
                { name: "Vehicle Types", href: "/vehicle-types" },
            ]
        },
        {
            name: "Drivers",
            icon: Users,
            href: "/drivers",
            subLinks: [
                { name: "All Drivers", href: "/drivers" },
                { name: "Add Driver", href: "/drivers/add" },
                { name: "Driver Performance", href: "/drivers/performance" },
                { name: "Driver Schedules", href: "/drivers/schedules" },
            ]
        },
        { name: "AI Camera", href: "/camera-monitoring", icon: Camera },
        { name: "Maintenance", href: "/maintenance", icon: Wrench },
        { name: "Reports", href: "/reports", icon: FileText },
        { name: "Notifications", href: "/notifications", icon: Bell },
        { name: "Settings", href: "/settings", icon: Settings },
    ];

    return (
        <nav className="flex flex-col gap-2 p-2">
            {/* Collapse/Expand Button */}
            <button
                onClick={onToggleCollapse}
                className={cn(
                    buttonVariants({ variant: "ghost", size: "sm" }),
                    "h-10 justify-center mb-2",
                    isCollapsed ? "w-10" : "w-full justify-start"
                )}
            >
                {isCollapsed ? (
                    <ChevronRight className="h-4 w-4" />
                ) : (
                    <>
                        <ChevronLeft className="h-4 w-4" />
                        <span className="ml-2">Collapse</span>
                    </>
                )}
            </button>

            {links.map((link) => (
                <div key={link.name}>
                    {link.subLinks ? (
                        <>
                            {/* Parent Menu Item */}
                            <button
                                onClick={() => !isCollapsed && toggleMenu(link.name)}
                                className={cn(
                                    buttonVariants({ 
                                        variant: pathname.startsWith("/vehicle") || pathname.startsWith("/driver") ? "secondary" : "ghost", 
                                        size: "sm" 
                                    }),
                                    "h-10 justify-start w-full",
                                    isCollapsed && "w-10 justify-center"
                                )}
                            >
                                <link.icon className="h-4 w-4" />
                                {!isCollapsed && (
                                    <>
                                        <span className="ml-3 flex-1 text-left">{link.name}</span>
                                        {expandedMenus.includes(link.name) ? (
                                            <ChevronUp className="h-3 w-3" />
                                        ) : (
                                            <ChevronDown className="h-3 w-3" />
                                        )}
                                    </>
                                )}
                            </button>
                            
                            {/* Submenu Items */}
                            {!isCollapsed && expandedMenus.includes(link.name) && (
                                <div className="ml-4 mt-1 space-y-1">
                                    {link.subLinks.map((subLink) => (
                                        <Link
                                            key={subLink.name}
                                            to={subLink.href}
                                            className={cn(
                                                buttonVariants({ 
                                                    variant: pathname === subLink.href ? "secondary" : "ghost", 
                                                    size: "sm" 
                                                }),
                                                "h-8 justify-start w-full text-sm pl-6"
                                            )}
                                        >
                                            <span>{subLink.name}</span>
                                        </Link>
                                    ))}
                                </div>
                            )}
                        </>
                    ) : (
                        <Link
                            to={link.href}
                            className={cn(
                                buttonVariants({ 
                                    variant: pathname === link.href ? "secondary" : "ghost", 
                                    size: "sm" 
                                }),
                                "h-10 justify-start",
                                isCollapsed && "w-10 justify-center"
                            )}
                        >
                            <link.icon className="h-4 w-4" />
                            {!isCollapsed && <span className="ml-3">{link.name}</span>}
                        </Link>
                    )}
                </div>
            ))}
        </nav>
    )
}
