
export function speak(msg:string){
  const u = new SpeechSynthesisUtterance(msg);
  u.lang="en-IN"; u.rate=0.9;
  speechSynthesis.cancel(); speechSynthesis.speak(u);
}
