
import { Polyline } from "react-leaflet";
export default function RouteGlow({route,severity}:{route:any[],severity:string}){
  const c = severity==="High"?"red":severity==="Moderate"?"orange":"green";
  return <Polyline positions={route} pathOptions={{color:c, weight:8, opacity:0.7}}/>
}
