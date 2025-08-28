import { z } from "zod";

export const leadsSchema = z.object({
  name: z.string({}).min(1, "Skriv et navn"),
  kategori: z.enum(["feelgood", "gjenkjøp"]),
  followUp: z.object({
    intervalFrequency: z.string(),
    intervalDuration: z.string(),
    intervalStart: z.date(),
  }),
  email: z.string().email().min(1, "Legg til en epost"),
});
