import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Textarea } from "@/components/ui/textarea";

export function ChatFeedback({ messageId, followUp }: { messageId: string; followUp?: boolean }) {
  const [friendliness, setFriendliness] = useState("");
  const [length, setLength] = useState("");
  const [emoji, setEmoji] = useState("");
  const [other, setOther] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSave = async () => {
    setLoading(true);
    setError(null);
    try {
      const feedback = JSON.stringify({
        friendliness,
        length,
        emoji,
        other,
      });
      const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : undefined;
      await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api"}/v1/companies/chats/${messageId}/send-feedback`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({ feedback }),
        }
      );
      setSuccess(true);
      setTimeout(() => setSuccess(false), 2000);
    } catch (err) {
      setError("Kunne ikke lagre tilbakemelding");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="outline" className="ml-5">
          Hvordan gjorde jeg det?
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[400px]">
        <div className="grid gap-4">
          <div className="space-y-2">
            <h4 className="font-display leading-none font-medium">
              Gi tilbakemelding til Ciri
            </h4>
            <p className="text-muted-foreground/60 font-sans text-sm">
              Gi så konkret tilbakemelding som mulig.
            </p>
          </div>
          <div className="grid gap-2">
            <div className="grid grid-cols-3 items-center gap-4">
              <Label htmlFor="width">Vennlighet</Label>
              <Input
                id="width"
                value={friendliness}
                onChange={e => setFriendliness(e.target.value)}
                placeholder="'Vær litt mer konkret og profesjonell'"
                className="col-span-2 h-8"
                disabled={loading}
              />
            </div>
            <div className="grid grid-cols-3 items-center gap-4">
              <Label htmlFor="maxWidth">Svarlengde</Label>
              <Input
                id="maxWidth"
                value={length}
                onChange={e => setLength(e.target.value)}
                placeholder="'Ha litt mer oppsummerende svar'"
                className="col-span-2 h-8"
                disabled={loading}
              />
            </div>
            <div className="grid grid-cols-3 items-center gap-4">
              <Label htmlFor="height">Emojibruk</Label>
              <Input
                id="height"
                value={emoji}
                onChange={e => setEmoji(e.target.value)}
                placeholder="'Litt mindre bruk av 🫶'"
                className="col-span-2 h-8"
                disabled={loading}
              />
            </div>
            <div className="grid grid-cols-3 items-center gap-4">
              <Label htmlFor="maxHeight" className="text-no">
                Annet
              </Label>
              <Textarea
                value={other}
                onChange={e => setOther(e.target.value)}
                placeholder="'I slike hendvendelser, gjør heller [...]'"
                className="col-span-2 h-8"
                disabled={loading}
              />
            </div>
            <Button variant="outline" onClick={handleSave} disabled={loading}>
              {loading ? "Lagrer..." : "Lagre"}
            </Button>
            {success && <div className="text-green-600 text-xs mt-2">Tilbakemelding lagret!</div>}
            {error && <div className="text-red-600 text-xs mt-2">{error}</div>}
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
