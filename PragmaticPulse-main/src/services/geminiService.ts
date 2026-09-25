import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY || "" });

export async function getResilienceAdvice(scenario: string, answers: Record<string, string>) {
  const prompt = `
    You are the "Pragmatic Sysadmin" AI advisor. 
    A user is simulating a digital disaster: "${scenario}".
    
    Based on their current setup:
    ${Object.entries(answers).map(([q, a]) => `- ${q}: ${a}`).join('\n')}
    
    Provide a pragmatic, no-nonsense assessment of their resilience.
    1. Identify the single biggest point of failure.
    2. Give 3 immediate, actionable steps to improve.
    3. Assign a "Pragmatic Score" from 0-100.
    
    Format the response as JSON with keys: "assessment", "failurePoint", "steps" (array of strings), and "score" (number).
  `;

  try {
    const response = await ai.models.generateContent({
      model: "gemini-3-flash-preview",
      contents: prompt,
      config: {
        responseMimeType: "application/json",
      },
    });
    return JSON.parse(response.text || "{}");
  } catch (error) {
    console.error("Gemini Error:", error);
    return null;
  }
}
