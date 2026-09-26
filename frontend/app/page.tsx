"use client";

import {use, useState} from "react";

export default function Home(){
  const [day, setDay] = useState("");
  const [month , setMonth] = useState("");
  const [year, setYear] = useState("");
  const [worldEvents , setWorldEvents] = useState<any[]>([]);
  const [indiaEvents , setIndiaEvents] = useState<any[]>([]);
  const [weather , setWeather] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const apiurl = process.env.NEXT_PUBLIC_API_URL;
  console.log("API URL is : ", apiurl);

  async function handleSubmit(e : React.FormEvent){
    e.preventDefault();
    setLoading(true);

    const dateStr = `${year}-${month.padStart(2,"0")}-${day.padStart(2,"0")}`;

    const [worldRes, indiaRes, weatherRes] = await Promise.all([
      fetch(`${apiurl}/events/world/list?month=${month}&day=${day}`),
      fetch(`${apiurl}/events/india/list?year=${year}`),
      fetch(`${apiurl}/weather/?region=india&date_str=${dateStr}`),
    ]);
    setWorldEvents(await worldRes.json());
    setIndiaEvents(await indiaRes.json());
    setWeather(await weatherRes.json());
    setLoading(false);
  }


  return (
    <main style = {{padding: "2rem", maxWidth: "800px", margin: "0 auto"}}>
      <h1>What Was the world like?</h1>

      <form onSubmit={handleSubmit} style ={{display : "flex", gap: "0.5rem", marginBottom: "2rem"}}>
        <input placeholder="DD" value = {day} onChange={(e) => setDay(e.target.value)}></input>
        <input placeholder="MM" value = {month} onChange={(e) => setMonth(e.target.value)}></input>
        <input placeholder="YYYY" value = {year} onChange={(e) => setYear(e.target.value)}></input>
        <button type = "submit">Show me</button>
      </form>

      {loading && <p>Loading... </p>}

      {weather && (
        <section style={{marginBottom: "2rem"}}>
          <h2>weather (india)</h2>
          <p>{weather.temp_c}°C, {weather.conditions}</p>
        </section>
      )}

      <div style = {{display: "flex", gap: "2rem"}}>
      <section style = {{flex : 1 }}>
        <h2>In India, {year}</h2>
        {indiaEvents.map((ev,i) => (
          <p key = {i}>
            <strong>{ev.month}/{ev.day}</strong> - {ev.title}
          </p>
        ))}
      </section>

      <section style={{ flex: 1 }}>
          <h2>🌍 World, on {day}/{month}</h2>
          {worldEvents.map((ev, i) => (
            <p key={i}>
              <strong>{ev.year}</strong> — {ev.title}
            </p>
          ))}
        </section>
      </div>


    </main>
  )




}