import { useState } from "react";
import { Phone, Share2, Send } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useToast } from "@/components/ui/use-toast";

interface Message {
  id: string;
  text: string;
  timestamp: string;
  isFromUser: boolean;
  status?: "sent" | "delivered" | "read";
}

export function DriverChat() {
  const { toast } = useToast();
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      text: "Habari Kamau! Just checking in - are you on schedule for the delivery to Mombasa?",
      timestamp: "07:35 AM",
      isFromUser: true,
      status: "read"
    },
    {
      id: "2",
      text: "Sawa boss! Niko Machakos sasa. Traffic ni poa, tutafika Mombasa mapema. The road is clear.",
      timestamp: "07:40 AM",
      isFromUser: false
    },
    {
      id: "3",
      text: "Poa sana! Keep me updated. Also, remember to refuel at Mtito Andei before the long stretch.",
      timestamp: "07:49 AM",
      isFromUser: true,
      status: "read"
    }
  ]);

  const sendMessage = () => {
    if (!message.trim()) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      text: message,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isFromUser: true,
      status: "sent"
    };

    setMessages(prev => [...prev, newMessage]);
    setMessage("");

    // Simulate message delivery
    setTimeout(() => {
      setMessages(prev => 
        prev.map(msg => 
          msg.id === newMessage.id ? { ...msg, status: "delivered" } : msg
        )
      );
    }, 1000);

    // Simulate driver response (for demo purposes)
    setTimeout(() => {
      const responses = [
        "Sawa boss, received!",
        "Asante, I'll keep you updated.",
        "Roger that, will do.",
        "Poa, no problem.",
        "Noted, thanks for the reminder."
      ];
      
      const randomResponse = responses[Math.floor(Math.random() * responses.length)];
      
      const driverMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: randomResponse,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        isFromUser: false
      };

      setMessages(prev => [...prev, driverMessage]);
      
      // Mark user message as read
      setMessages(prev => 
        prev.map(msg => 
          msg.id === newMessage.id ? { ...msg, status: "read" } : msg
        )
      );
    }, 3000);

    toast({
      title: "Message Sent",
      description: "Your message has been sent to the driver.",
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const getStatusText = (status?: string) => {
    switch (status) {
      case "sent": return "Sent";
      case "delivered": return "Delivered";
      case "read": return "Read";
      default: return "";
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Chat with driver</CardTitle>
          <div className="flex items-center gap-2">
            <Avatar className="w-8 h-8">
              <AvatarImage src="https://api.dicebear.com/7.x/avataaars/svg?seed=driver1" />
              <AvatarFallback>JK</AvatarFallback>
            </Avatar>
            <span className="text-sm text-muted-foreground">John Kamau</span>
            <Button size="icon" variant="ghost" className="h-8 w-8">
              <Phone className="h-4 w-4" />
            </Button>
            <Button size="icon" variant="ghost" className="h-8 w-8">
              <Share2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <ScrollArea className="h-[300px] pr-4">
          <div className="space-y-4">
            {messages.map((msg) => (
              <div key={msg.id} className={`flex ${msg.isFromUser ? 'justify-end' : 'justify-start'}`}>
                <div className={`rounded-2xl px-4 py-2 max-w-[80%] ${
                  msg.isFromUser 
                    ? 'bg-primary text-primary-foreground rounded-tr-sm' 
                    : 'bg-muted rounded-tl-sm'
                }`}>
                  <p className={`text-sm ${msg.isFromUser ? '' : 'text-foreground'}`}>
                    {msg.text}
                  </p>
                  <div className="flex items-center justify-between mt-1">
                    <span className={`text-xs ${
                      msg.isFromUser ? 'opacity-80' : 'text-muted-foreground'
                    }`}>
                      {msg.timestamp}
                    </span>
                    {msg.isFromUser && msg.status && (
                      <span className={`text-xs ml-2 ${
                        msg.isFromUser ? 'opacity-80' : 'text-muted-foreground'
                      }`}>
                        {getStatusText(msg.status)}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>

        <div className="flex gap-2 pt-2 border-t">
          <Input
            placeholder="Write your message"
            className="flex-1"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
          />
          <Button 
            size="icon" 
            variant="ghost"
            onClick={sendMessage}
            disabled={!message.trim()}
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
