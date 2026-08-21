
import { useEffect } from "react";
import { speak } from "./voice";

export default function NavigationAlert(){
  useEffect(()=>{
    const t = setInterval(()=>{
      navigator.geolocation.getCurrentPosition(async p=>{
        const r = await fetch("http://localhost:8000/api/route-check/",{
          method:"POST",
          headers:{'Content-Type':'application/json'},
          body: JSON.stringify({current_lat:p.coords.latitude, current_lng:p.coords.longitude})
        });
        const d = await r.json();
        if(d.alert) speak(d.message);
      });
    },8000);
    return ()=>clearInterval(t);
  },[]);
  return null;
}
